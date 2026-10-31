"""依時間順序重算比賽，把分數寫回資料庫。

每個賽季分開計算：賽季開始時所有人回到起始分數，分數取決於這個賽季最近 20 場的表現。
任何比賽、賽季、球員性別或甲組有變動時都從頭重算（資料量小，重算很快）。
"""

from dataclasses import dataclass
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import joinedload

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
    players = db.session.execute(select(Member.id, Member.gender, Member.is_a_division, Member.is_guest)).all()
    starts = {pid: rating_domain.starting_rating(gender, a_division) for pid, gender, a_division, _ in players}
    guest_history = _guest_history({pid for pid, *_, is_guest in players if is_guest})
    ratings = dict(starts)
    performances: dict[int, list[float]] = {}
    results: dict[int, dict[int, MatchResult]] = {}

    stmt = (
        select(MatchRecord)
        .join(MatchRecord.match)
        .options(joinedload(MatchRecord.match).joinedload(Match.event))
        .order_by(Match.match_date.asc(), MatchRecord.id.asc())
    )
    records = db.session.scalars(period.filter(stmt)).unique()
    for record in records:
        side_a, side_b = record.side_a_ids, record.side_b_ids
        if not record.match.counts_toward_rating:
            continue
        if not side_a or not side_b or any(pid not in ratings for pid in side_a + side_b):
            continue
        team_a = rating_domain.team_rating([ratings[pid] for pid in side_a])
        team_b = rating_domain.team_rating([ratings[pid] for pid in side_b])
        swing = rating_domain.swing(team_a, team_b, record.a_games, record.b_games)

        # 對上還不熟的訪客時，這場對我方的影響打折
        known = guest_history.get(record.id, {})

        def weight(opponents: list[int], known: dict[int, int] = known) -> float:
            return sum(rating_domain.familiarity(known[p]) if p in known else 1.0 for p in opponents) / len(opponents)

        deltas = [(pid, swing * weight(side_b)) for pid in side_a] + [(pid, -swing * weight(side_a)) for pid in side_b]
        record_results = {}
        for pid, delta in deltas:
            before = ratings[pid]
            performance = rating_domain.clamp(before + delta)
            performances.setdefault(pid, []).append(performance)
            ratings[pid] = rating_domain.rating_from(performances[pid], starts[pid])
            record_results[pid] = MatchResult(before, performance, ratings[pid])
        results[record.id] = record_results
    return Replay(ratings, performances, results)


def _guest_history(guests: set[int]) -> dict[int, dict[int, int]]:
    """每場比賽裡的訪客在這場之前已經打過幾場（不分賽季），以 MatchRecord.id 為鍵。"""
    seen: dict[int, int] = {}
    history: dict[int, dict[int, int]] = {}
    rows = db.session.execute(
        select(
            MatchRecord.id,
            MatchRecord.player1_id,
            MatchRecord.player2_id,
            MatchRecord.player3_id,
            MatchRecord.player4_id,
        )
        .join(MatchRecord.match)
        .order_by(Match.match_date.asc(), MatchRecord.id.asc())
    )
    for record_id, *player_ids in rows:
        here = {pid: seen.get(pid, 0) for pid in player_ids if pid in guests}
        if here:
            history[record_id] = here
        for pid in here:
            seen[pid] = here[pid] + 1
    return history


def recalculate_all() -> None:
    result = replay(current_period())
    for member in db.session.scalars(select(Member)):
        # 這個賽季還沒打過比賽的球員存 None，顯示時用起始分數
        member.rating = result.ratings[member.id] if member.id in result.performances else None


def results_for_records(record_ids: set[int]) -> dict[int, dict[int, MatchResult]]:
    """指定比賽（以 MatchRecord.id 為鍵）裡每位球員的分數變化，各賽季分開計算。"""
    if not record_ids:
        return {}
    return {
        rid: by_player
        for period in all_periods()
        for rid, by_player in replay(period).results.items()
        if rid in record_ids
    }


def results_for(member_id: int) -> dict[int, MatchResult]:
    """某位球員每場比賽（以 MatchRecord.id 為鍵）的分數變化，各賽季分開計算。"""
    return {
        rid: by_player[member_id]
        for period in all_periods()
        for rid, by_player in replay(period).results.items()
        if member_id in by_player
    }
