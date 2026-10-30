"""依時間順序重算比賽，把分數寫回資料庫。

每個賽季分開計算：賽季開始時所有人回到起始分數，分數取決於這個賽季最近 20 場的表現。
任何比賽、賽季或球員性別有變動時都從頭重算（資料量小，重算很快）。
"""

from dataclasses import dataclass
from datetime import date

from sqlalchemy import func, select

from ..domain import rating as rating_domain
from ..extensions import db
from ..models import Match, MatchRecord, Member, Season


@dataclass(frozen=True)
class Period:
    """比賽日期範圍 start <= 日期 < end；None 表示該端不設限。"""

    start: date | None = None
    end: date | None = None

    def contains(self, day: date) -> bool:
        return (self.start is None or day >= self.start) and (self.end is None or day < self.end)

    def filter(self, stmt):
        """把日期範圍加到已 join Match 的查詢上。"""
        if self.start:
            stmt = stmt.where(Match.match_date >= self.start)
        if self.end:
            stmt = stmt.where(Match.match_date < self.end)
        return stmt


def current_period() -> Period:
    """目前賽季（最後一個賽季）的範圍；還沒有賽季時為全部比賽。"""
    return Period(db.session.scalar(select(func.max(Season.start_date))))


def all_periods() -> list[Period]:
    """依賽季切開、涵蓋所有日期的範圍（第一個賽季之前的比賽自成一段）。"""
    bounds = [None, *sorted(db.session.scalars(select(Season.start_date))), None]
    return [Period(start, end) for start, end in zip(bounds, bounds[1:], strict=False)]


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

    def latest_results(self) -> dict[int, MatchResult]:
        """每位球員最近一場比賽的分數變化。"""
        latest: dict[int, MatchResult] = {}
        for by_player in self.results.values():
            latest.update(by_player)
        return latest


def replay(period: Period | None = None) -> Replay:
    """依序重算某段期間（預設為全部）的比賽；期間開始時所有人都從起始分數算起。"""
    period = period or Period()
    db.session.flush()
    genders = db.session.execute(select(Member.id, Member.gender))
    starts = {pid: rating_domain.starting_rating(gender) for pid, gender in genders}
    ratings = dict(starts)
    performances: dict[int, list[float]] = {}
    results: dict[int, dict[int, MatchResult]] = {}

    stmt = select(MatchRecord).join(MatchRecord.match).order_by(Match.match_date.asc(), MatchRecord.id.asc())
    records = db.session.scalars(period.filter(stmt))
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
    result = replay(current_period())
    for member in db.session.scalars(select(Member)):
        # 這個賽季還沒打過比賽的球員存 None，顯示時用起始分數
        member.rating = result.ratings[member.id] if member.id in result.performances else None


def results_for(member_id: int) -> dict[int, MatchResult]:
    """某位球員每場比賽（以 MatchRecord.id 為鍵）的分數變化，各賽季分開計算。"""
    return {
        rid: by_player[member_id]
        for period in all_periods()
        for rid, by_player in replay(period).results.items()
        if member_id in by_player
    }
