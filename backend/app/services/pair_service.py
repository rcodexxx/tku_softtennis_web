"""組合榜：雙打搭檔的戰績、組合表現與默契值。

- 組合表現：這兩人同隊時，兩人「本場表現」的平均
- 默契值：組合表現減掉兩人各自整季的平均表現；正的代表搭起來比各自平常打得好
"""

from collections import defaultdict
from dataclasses import dataclass, field
from statistics import mean

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from ..domain.pairing import Pair, pair_key
from ..enums import MatchOutcomeEnum
from ..extensions import db
from ..models import Match, MatchRecord, Member, Season
from . import rating_service, season_service


@dataclass
class PairStats:
    players: tuple[Member, Member]
    wins: int = 0
    losses: int = 0
    performances: list[float] = field(default_factory=list)
    chemistry: float = 0.0
    # 這組裡誰當前衛幾次（有記錄站位的比賽）
    fronts: dict[int, int] = field(default_factory=dict)

    @property
    def matches(self) -> int:
        return self.wins + self.losses

    @property
    def win_rate(self) -> float:
        return round(self.wins / self.matches * 100, 1) if self.matches else 0.0

    @property
    def rating(self) -> float:
        return mean(self.performances) if self.performances else 0.0


def pairs(season: Season | None, min_matches: int = 1) -> list[PairStats]:
    period = season_service.period(season)
    replay = rating_service.replay(period)
    stmt = (
        select(MatchRecord)
        .join(MatchRecord.match)
        .options(joinedload(MatchRecord.match))
        .where(MatchRecord.player2_id.is_not(None), MatchRecord.player4_id.is_not(None))
        .order_by(Match.match_date, MatchRecord.id)
    )

    stats: dict[Pair, PairStats] = {}
    members: dict[int, Member] = {}
    for record in db.session.scalars(period.filter(stmt)).unique():
        if record.side_a_outcome not in (MatchOutcomeEnum.WIN, MatchOutcomeEnum.LOSS):
            continue
        results = replay.results.get(record.id)
        if not results:
            continue
        a_won = record.side_a_outcome == MatchOutcomeEnum.WIN
        for side, won, front in (
            (record.side_a_ids, a_won, record.a_front_id),
            (record.side_b_ids, not a_won, record.b_front_id),
        ):
            key = pair_key(*side)
            entry = stats.get(key)
            if entry is None:
                for pid in key:
                    members.setdefault(pid, db.session.get(Member, pid))
                entry = stats.setdefault(key, PairStats((members[key[0]], members[key[1]])))
            entry.wins += won
            entry.losses += not won
            entry.performances.append(mean(results[pid].performance for pid in key))
            if front in key:
                entry.fronts[front] = entry.fronts.get(front, 0) + 1

    baseline = {pid: mean(values) for pid, values in replay.performances.items()}
    for (a, b), entry in stats.items():
        entry.chemistry = entry.rating - mean((baseline[a], baseline[b]))
    return [entry for entry in stats.values() if entry.matches >= min_matches]


def partner_chemistry(member_id: int, season: Season | None) -> dict[int, float]:
    """某位球員和每位搭檔的默契值（以搭檔 id 為鍵）。"""
    result = defaultdict(float)
    for entry in pairs(season):
        ids = [player.id for player in entry.players]
        if member_id in ids:
            result[ids[1] if ids[0] == member_id else ids[0]] = entry.chemistry
    return dict(result)
