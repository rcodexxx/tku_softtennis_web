from dataclasses import dataclass, field
from datetime import date, timedelta

from flask import current_app
from sqlalchemy import func, select
from sqlalchemy.orm import joinedload

from ..core.db import get_or_404
from ..core.pagination import Page, paginate_list
from ..domain import rating as rating_domain
from ..enums import MatchOutcomeEnum
from ..extensions import db
from ..models import Match, MatchRecord, Member, Organization
from . import rating_service

RECENT_FORM_SIZE = 5


@dataclass
class MatchStats:
    wins: int = 0
    losses: int = 0
    last_match_date: date | None = None
    # 最近的比賽結果，最新的在前：True 為勝
    recent_results: list[bool] = field(default_factory=list)
    score_change: float | None = None

    @property
    def total_matches(self) -> int:
        return self.wins + self.losses

    @property
    def win_rate(self) -> float:
        return round(self.wins / self.total_matches * 100, 2) if self.total_matches else 0.0

    def to_dict(self) -> dict:
        return {
            "wins": self.wins,
            "losses": self.losses,
            "total_matches": self.total_matches,
            "win_rate": self.win_rate,
            "last_match_date": self.last_match_date.isoformat() if self.last_match_date else None,
            "recent_form": ["W" if won else "L" for won in self.recent_results],
            "score_change": round(self.score_change, 2) if self.score_change is not None else None,
        }


@dataclass
class LeaderboardEntry:
    member: Member
    stats: MatchStats
    rank: int = field(default=0)


def match_stats() -> dict[int, MatchStats]:
    """一次查詢計算所有球員的勝敗場次、近況與最近一場的分數變化。"""
    rows = db.session.execute(
        select(
            MatchRecord.player1_id,
            MatchRecord.player2_id,
            MatchRecord.player3_id,
            MatchRecord.player4_id,
            MatchRecord.side_a_outcome,
            Match.match_date,
        )
        .join(Match, MatchRecord.match_id == Match.id)
        .where(MatchRecord.side_a_outcome.in_([MatchOutcomeEnum.WIN, MatchOutcomeEnum.LOSS]))
        .order_by(Match.match_date.desc(), MatchRecord.id.desc())
    )
    stats: dict[int, MatchStats] = {}
    for p1, p2, p3, p4, outcome, match_date in rows:
        side_a_won = outcome == MatchOutcomeEnum.WIN
        for pid, won in ((p1, side_a_won), (p2, side_a_won), (p3, not side_a_won), (p4, not side_a_won)):
            if not pid:
                continue
            s = stats.setdefault(pid, MatchStats())
            if won:
                s.wins += 1
            else:
                s.losses += 1
            if len(s.recent_results) < RECENT_FORM_SIZE:
                s.recent_results.append(won)
            if s.last_match_date is None or match_date > s.last_match_date:
                s.last_match_date = match_date
    for pid, result in rating_service.last_match_results().items():
        stats.setdefault(pid, MatchStats()).score_change = result.change
    return stats


def member_stats(member_id: int) -> tuple[Member, MatchStats]:
    member = get_or_404(Member, member_id, "找不到指定的成員。")
    return member, match_stats().get(member_id, MatchStats())


def leaderboard(params: dict) -> Page:
    stmt = select(Member).options(joinedload(Member.user), joinedload(Member.organization))
    if not params["include_guests"]:
        stmt = stmt.where(Member.is_guest.is_(False))
    if not params["include_inactive"]:
        stmt = stmt.where(Member.active_clause())
    if params.get("organization_id"):
        stmt = stmt.where(Member.organization_id == params["organization_id"])
    if params["scope"] != "all":
        stmt = stmt.where(Member.organization_id.in_(_scope_organizations(params["scope"])))
    if params.get("gender"):
        stmt = stmt.where(Member.gender == params["gender"])
    if params.get("joined_after"):
        stmt = stmt.where(Member.joined_date >= params["joined_after"])

    all_stats = match_stats()
    entries = [LeaderboardEntry(m, all_stats.get(m.id, MatchStats())) for m in db.session.scalars(stmt).unique()]
    entries = [e for e in entries if e.stats.total_matches >= params["min_matches"]]
    if params.get("min_win_rate") is not None:
        entries = [e for e in entries if e.stats.win_rate >= params["min_win_rate"]]
    if params.get("active_since"):
        entries = [e for e in entries if e.stats.last_match_date and e.stats.last_match_date >= params["active_since"]]

    entries.sort(key=_sort_key(params["sort_by"]), reverse=params["sort_order"] == "desc")
    for rank, entry in enumerate(entries, start=1):
        entry.rank = rank
    return paginate_list(entries, params["page"], params["per_page"])


def _scope_organizations(scope: str) -> list[int]:
    team = current_app.config["TEAM_ORGANIZATION_ID"]
    return [team] if scope == "team" else [team, current_app.config["ALUMNI_ORGANIZATION_ID"]]


def _sort_key(sort_by: str):
    return {
        "score": lambda e: e.member.score,
        "win_rate": lambda e: (e.stats.win_rate, e.stats.total_matches),
        "total_matches": lambda e: e.stats.total_matches,
        "wins": lambda e: e.stats.wins,
        "recent_activity": lambda e: e.stats.last_match_date or date.min,
        "join_date": lambda e: e.member.joined_date or date.min,
    }[sort_by]


def compare(member1_id: int, member2_id: int) -> dict:
    member1 = get_or_404(Member, member1_id, "找不到指定的成員。")
    member2 = get_or_404(Member, member2_id, "找不到指定的成員。")
    stats = match_stats()
    score1, score2 = member1.score, member2.score
    return {
        "member1": member1,
        "member1_stats": stats.get(member1.id, MatchStats()),
        "member2": member2,
        "member2_stats": stats.get(member2.id, MatchStats()),
        "comparison": {
            "score_difference": round(score1 - score2, 2),
            "is_likely_stronger": score1 > score2,
            # member1 對上 member2（搭檔實力相同時）預期拿下的局數比例
            "expected_games_share": round(rating_domain.expected_share(score1, score2), 3),
        },
    }


def statistics() -> dict:
    members = list(db.session.scalars(select(Member).where(Member.active_clause())))
    total_members = db.session.scalar(select(func.count()).where(Member.is_guest.is_(False)))
    total_guests = db.session.scalar(select(func.count()).where(Member.is_guest.is_(True)))
    total_matches = db.session.scalar(select(func.count(MatchRecord.id)))
    total_players = total_members + total_guests
    scores = sorted(m.score for m in members)

    today = date.today()

    def matches_since(days: int) -> int:
        return db.session.scalar(
            select(func.count(MatchRecord.id)).join(Match).where(Match.match_date >= today - timedelta(days=days))
        )

    organization_distribution = dict(
        db.session.execute(
            select(Organization.name, func.count(Member.id))
            .join(Member, Member.organization_id == Organization.id)
            .where(Member.active_clause())
            .group_by(Organization.name)
        ).all()
    )

    return {
        "total_players": total_players,
        "total_members": total_members,
        "total_guests": total_guests,
        "total_active_players": len(members),
        "total_matches": total_matches,
        "average_matches_per_player": round(total_matches / total_players, 2) if total_players else 0.0,
        "score_distribution": _distribution(scores),
        "organization_distribution": organization_distribution,
        "matches_last_week": matches_since(7),
        "matches_last_month": matches_since(30),
        "new_players_last_month": db.session.scalar(
            select(func.count()).where(Member.joined_date >= today - timedelta(days=30))
        ),
    }


def _distribution(scores: list[float]) -> dict:
    n = len(scores)
    if n == 0:
        return {}
    mean = sum(scores) / n
    return {
        "min": round(scores[0], 2),
        "max": round(scores[-1], 2),
        "avg": round(mean, 2),
        "median": round(scores[n // 2], 2),
        "std_dev": round((sum((s - mean) ** 2 for s in scores) / n) ** 0.5, 2),
    }
