"""球員頁的數據：分數走勢、搭檔、對手、歷屆賽季。"""

from dataclasses import dataclass, field
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from ..core.db import get_or_404
from ..enums import MatchOutcomeEnum
from ..extensions import db
from ..models import Match, MatchRecord, Member, Season
from . import pair_service, rating_service, season_service
from ._queries import involves_player


@dataclass
class HeadToHead:
    """和某位球員同隊（搭檔）或對打（對手）的戰績。"""

    player: Member
    wins: int = 0
    losses: int = 0
    last_date: date | None = None
    # 搭檔才有：兩人同隊時打得比各自平常好多少
    chemistry: float | None = None

    @property
    def matches(self) -> int:
        return self.wins + self.losses

    @property
    def win_rate(self) -> float:
        return round(self.wins / self.matches * 100, 1) if self.matches else 0.0


@dataclass
class Insights:
    member: Member
    season: Season | None
    rating: float
    wins: int = 0
    losses: int = 0
    # 這個賽季每場比賽後的分數（舊到新）
    trend: list[dict] = field(default_factory=list)
    partners: list[HeadToHead] = field(default_factory=list)
    opponents: list[HeadToHead] = field(default_factory=list)
    seasons: list[dict] = field(default_factory=list)


def insights(member_id: int, season_id: int | None = None) -> Insights:
    member = get_or_404(Member, member_id, "找不到指定的球員。")
    season = season_service.resolve(season_id)
    period = season_service.period(season)
    replay = rating_service.replay(period)

    result = Insights(member, season, replay.ratings.get(member.id, member.score))
    partners: dict[int, HeadToHead] = {}
    opponents: dict[int, HeadToHead] = {}
    for record in _records(member.id, period):
        on_a = member.id in record.side_a_ids
        if record.side_a_outcome not in (MatchOutcomeEnum.WIN, MatchOutcomeEnum.LOSS):
            continue
        won = (record.side_a_outcome == MatchOutcomeEnum.WIN) == on_a
        mates = record.side_a_ids if on_a else record.side_b_ids
        rivals = record.side_b_ids if on_a else record.side_a_ids
        if won:
            result.wins += 1
        else:
            result.losses += 1
        for pid, table in [(pid, partners) for pid in mates if pid != member.id] + [(pid, opponents) for pid in rivals]:
            entry = table.get(pid) or table.setdefault(pid, HeadToHead(db.session.get(Member, pid)))
            if won:
                entry.wins += 1
            else:
                entry.losses += 1
            entry.last_date = record.match.match_date
        after = replay.results.get(record.id, {}).get(member.id)
        if after:
            result.trend.append(
                {"date": record.match.match_date, "rating": round(after.after, 2), "won": won, "record_id": record.id}
            )

    chemistry = pair_service.partner_chemistry(member.id, season)
    for pid, entry in partners.items():
        entry.chemistry = chemistry.get(pid)
    result.partners = sorted(partners.values(), key=_most_played)
    result.opponents = sorted(opponents.values(), key=_most_played)
    result.seasons = season_history(member)
    return result


def season_history(member: Member) -> list[dict]:
    """每個賽季結束時（或目前）的分數、場數與名次（在有上場的正式隊員裡）。"""
    history = []
    guests = set(db.session.scalars(select(Member.id).where(Member.is_guest.is_(True))))
    for season in season_service.list_seasons():
        replay = rating_service.replay(season_service.period(season))
        if member.id not in replay.performances:
            continue
        ranked = sorted((pid for pid in replay.performances if pid not in guests), key=lambda pid: -replay.ratings[pid])
        history.append(
            {
                "season_id": season.id,
                "season_name": season.name,
                "is_current": season_service.is_current(season),
                "rating": round(replay.ratings[member.id], 2),
                "matches": len(replay.performances[member.id]),
                "rank": ranked.index(member.id) + 1 if member.id in ranked else None,
                "ranked_count": len(ranked),
            }
        )
    return history


def _most_played(entry: HeadToHead) -> tuple[int, float]:
    return -entry.matches, -entry.win_rate


def _records(member_id: int, period: rating_service.Period) -> list[MatchRecord]:
    stmt = (
        select(MatchRecord)
        .join(MatchRecord.match)
        .options(joinedload(MatchRecord.match))
        .where(involves_player(member_id))
        .order_by(Match.match_date.asc(), MatchRecord.id.asc())
    )
    return list(db.session.scalars(period.filter(stmt)).unique())
