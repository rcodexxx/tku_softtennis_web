"""依時間順序重算所有比賽，把分數寫回資料庫。

分數取決於最近 20 場的表現，任何比賽或球員性別有變動時都從頭重算（資料量小，重算很快）。
"""

from dataclasses import dataclass

from sqlalchemy import select

from ..domain import rating as rating_domain
from ..extensions import db
from ..models import Match, MatchRecord, Member


@dataclass(frozen=True)
class MatchResult:
    """某位球員在某場比賽的分數：賽前、本場表現、賽後。"""

    before: float
    performance: float
    after: float

    @property
    def change(self) -> float:
        return self.after - self.before


@dataclass
class Replay:
    ratings: dict[int, float]
    # 有打過比賽的球員才會出現在這裡
    performances: dict[int, list[float]]
    # record_id -> {player_id: MatchResult}
    results: dict[int, dict[int, MatchResult]]


def replay() -> Replay:
    db.session.flush()
    genders = db.session.execute(select(Member.id, Member.gender))
    starts = {pid: rating_domain.starting_rating(gender) for pid, gender in genders}
    ratings = dict(starts)
    performances: dict[int, list[float]] = {}
    results: dict[int, dict[int, MatchResult]] = {}

    records = db.session.scalars(
        select(MatchRecord).join(MatchRecord.match).order_by(Match.match_date.asc(), MatchRecord.id.asc())
    )
    for record in records:
        side_a, side_b = record.side_a_ids, record.side_b_ids
        if not side_a or not side_b or any(pid not in ratings for pid in side_a + side_b):
            continue
        team_a = rating_domain.team_rating([ratings[pid] for pid in side_a])
        team_b = rating_domain.team_rating([ratings[pid] for pid in side_b])
        swing = rating_domain.swing(team_a, team_b, record.a_games, record.b_games)

        record_results = {}
        for pid, delta in [(pid, swing) for pid in side_a] + [(pid, -swing) for pid in side_b]:
            before = ratings[pid]
            performance = rating_domain.clamp(before + delta)
            performances.setdefault(pid, []).append(performance)
            ratings[pid] = rating_domain.rating_from(performances[pid], starts[pid])
            record_results[pid] = MatchResult(before, performance, ratings[pid])
        results[record.id] = record_results
    return Replay(ratings, performances, results)


def recalculate_all() -> None:
    result = replay()
    for member in db.session.scalars(select(Member)):
        # 沒打過比賽的球員存 None，顯示時用起始分數
        member.rating = result.ratings[member.id] if member.id in result.performances else None


def results_for(member_id: int) -> dict[int, MatchResult]:
    """某位球員每場比賽（以 MatchRecord.id 為鍵）的分數變化。"""
    return {rid: by_player[member_id] for rid, by_player in replay().results.items() if member_id in by_player}


def last_match_results() -> dict[int, MatchResult]:
    """每位球員最近一場比賽的分數變化。"""
    latest: dict[int, MatchResult] = {}
    for by_player in replay().results.values():
        latest.update(by_player)
    return latest
