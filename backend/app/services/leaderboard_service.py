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
from ..models import Match, MatchRecord, Member, Organization, Season
from . import rating_service, season_service

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
    # 這個賽季的分數
    score: float
    rank: int = field(default=0)


@dataclass
class SeasonData:
    period: rating_service.Period
    replay: rating_service.Replay
    stats: dict[int, MatchStats]

    def score(self, member: Member) -> float:
        return self.replay.ratings.get(member.id, member.score)


def season_data(season: Season | None) -> SeasonData:
    """某個賽季（None 為全部比賽）的分數重算結果與每位球員的戰績。"""
    period = season_service.period(season)
    replay = rating_service.replay(period)
    return SeasonData(period, replay, match_stats(period, replay))


def match_stats(period: rating_service.Period, replay: rating_service.Replay) -> dict[int, MatchStats]:
    """一次查詢計算期間內所有球員的勝敗場次、近況與最近一場的分數變化。"""
    stmt = (
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
    stmt = period.filter(stmt)
    stats: dict[int, MatchStats] = {}
    for p1, p2, p3, p4, outcome, match_date in db.session.execute(stmt):
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
    for pid, result in replay.latest_results().items():
        stats.setdefault(pid, MatchStats()).score_change = result.change
    return stats


def member_stats(member_id: int) -> tuple[Member, MatchStats]:
    """目前賽季的戰績。"""
    member = get_or_404(Member, member_id, "找不到指定的成員。")
    data = season_data(season_service.current_season())
    return member, data.stats.get(member_id, MatchStats())


def leaderboard(params: dict) -> tuple[Season | None, Page]:
    season = season_service.resolve(params.get("season_id"))
    current = season_service.is_current(season)
    members = _leaderboard_members(params, season, current)

    data = season_data(season)
    entries = [LeaderboardEntry(m, data.stats.get(m.id, MatchStats()), data.score(m)) for m in members]
    min_matches = params["min_matches"] if current else max(1, params["min_matches"])
    entries = [e for e in entries if e.stats.total_matches >= min_matches]
    if params.get("min_win_rate") is not None:
        entries = [e for e in entries if e.stats.win_rate >= params["min_win_rate"]]
    if params.get("active_since"):
        entries = [e for e in entries if e.stats.last_match_date and e.stats.last_match_date >= params["active_since"]]

    entries.sort(key=_sort_key(params["sort_by"]), reverse=params["sort_order"] == "desc")
    for rank, entry in enumerate(entries, start=1):
        entry.rank = rank
    return season, paginate_list(entries, params["page"], params["per_page"])


def _leaderboard_members(params: dict, season: Season | None, current: bool) -> list[Member]:
    # 舊賽季照封存的名單分組，並列出當時有上場的所有人（包含之後離隊的）
    roster = {} if current else {r.member_id: r.organization_id for r in season.rosters}
    stmt = select(Member).options(joinedload(Member.user), joinedload(Member.organization))
    if not params["include_guests"]:
        stmt = stmt.where(Member.is_guest.is_(False))
    if current and not params["include_inactive"]:
        stmt = stmt.where(Member.active_clause())
    if params.get("gender"):
        stmt = stmt.where(Member.gender == params["gender"])
    if params.get("joined_after"):
        stmt = stmt.where(Member.joined_date >= params["joined_after"])

    def organization_of(member: Member) -> int | None:
        return roster.get(member.id, member.organization_id)

    members = list(db.session.scalars(stmt).unique())
    if params["scope"] != "all":
        allowed = _scope_organizations(params["scope"])
        members = [m for m in members if organization_of(m) in allowed]
    if params.get("organization_id"):
        members = [m for m in members if organization_of(m) == params["organization_id"]]
    return members


def _scope_organizations(scope: str) -> list[int]:
    team = current_app.config["TEAM_ORGANIZATION_ID"]
    return [team] if scope == "team" else [team, current_app.config["ALUMNI_ORGANIZATION_ID"]]


def _sort_key(sort_by: str):
    return {
        "score": lambda e: e.score,
        "win_rate": lambda e: (e.stats.win_rate, e.stats.total_matches),
        "total_matches": lambda e: e.stats.total_matches,
        "wins": lambda e: e.stats.wins,
        "recent_activity": lambda e: e.stats.last_match_date or date.min,
        "join_date": lambda e: e.member.joined_date or date.min,
    }[sort_by]


def compare(member1_id: int, member2_id: int) -> dict:
    member1 = get_or_404(Member, member1_id, "找不到指定的成員。")
    member2 = get_or_404(Member, member2_id, "找不到指定的成員。")
    stats = season_data(season_service.current_season()).stats
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


def statistics(season_id: int | None = None) -> dict:
    """球員人數是目前的狀況；比賽數與分數分布只看指定的賽季（預設為目前賽季）。"""
    data = season_data(season_service.resolve(season_id))
    members = list(db.session.scalars(select(Member).where(Member.active_clause())))
    total_members = db.session.scalar(select(func.count()).where(Member.is_guest.is_(False)))
    total_guests = db.session.scalar(select(func.count()).where(Member.is_guest.is_(True)))
    total_matches = season_service.count_matches(data.period)
    total_players = total_members + total_guests
    # 這個賽季有上場的球員
    scores = sorted(data.replay.ratings[pid] for pid in data.replay.performances)

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
