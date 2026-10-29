"""把 domain.rating 的計算結果寫回資料庫。

評分與比賽順序有關，所以只要不是「新增最新一場比賽」，一律從頭重算全部比賽。
"""

from sqlalchemy import exists, select

from ..domain.rating import Participant, Rating, conservative_score, rate_match
from ..extensions import db
from ..models import Match, MatchRecord, Member


def _apply(record: MatchRecord, ratings: dict[int, Rating], genders: dict) -> None:
    ids = record.side_a_ids + record.side_b_ids
    if not record.side_a_ids or not record.side_b_ids or any(pid not in ratings for pid in ids):
        return

    def team(pids):
        return [Participant(pid, ratings[pid], genders.get(pid)) for pid in pids]

    ratings.update(
        rate_match(team(record.side_a_ids), team(record.side_b_ids), record.a_games, record.b_games, record.side_a_won)
    )


def _replay(members: list[Member], on_match=None) -> tuple[dict[int, Rating], dict[int, Rating]]:
    """依時間順序重算所有比賽，回傳 (最終評分, 每位球員最後一場比賽前的評分)。

    on_match(record, before, after) 會在每場比賽算完後被呼叫。
    """
    ratings = {m.id: Rating() for m in members}
    genders = {m.id: m.gender for m in members}
    before_last: dict[int, Rating] = {}

    records = db.session.scalars(
        select(MatchRecord).join(MatchRecord.match).order_by(Match.match_date.asc(), MatchRecord.id.asc())
    )
    for record in records:
        before = dict(ratings) if on_match else None
        for pid in record.side_a_ids + record.side_b_ids:
            if pid in ratings:
                before_last[pid] = ratings[pid]
        _apply(record, ratings, genders)
        if on_match:
            on_match(record, before, ratings)
    return ratings, before_last


def recalculate_all() -> None:
    db.session.flush()
    members = db.session.scalars(select(Member)).all()
    ratings, _ = _replay(members)
    for member in members:
        member.mu, member.sigma = ratings[member.id].mu, ratings[member.id].sigma


def last_match_score_changes() -> dict[int, float]:
    """每位球員最近一場比賽讓排名分數（conservative score）變動多少。"""
    members = db.session.scalars(select(Member)).all()
    ratings, before_last = _replay(members)
    return {pid: conservative_score(ratings[pid]) - conservative_score(before) for pid, before in before_last.items()}


def on_match_created(record: MatchRecord) -> None:
    db.session.flush()
    if _is_latest(record):
        _apply_incrementally(record)
    else:
        recalculate_all()


def _is_latest(record: MatchRecord) -> bool:
    later = exists().where(MatchRecord.match_id == Match.id, Match.match_date > record.match.match_date)
    return not db.session.scalar(select(later))


def _apply_incrementally(record: MatchRecord) -> None:
    members = {
        m.id: m for m in db.session.scalars(select(Member).where(Member.id.in_(record.side_a_ids + record.side_b_ids)))
    }
    ratings = {pid: m.rating for pid, m in members.items()}
    _apply(record, ratings, {pid: m.gender for pid, m in members.items()})
    for pid, member in members.items():
        member.mu, member.sigma = ratings[pid].mu, ratings[pid].sigma


def score_changes_for(member_id: int) -> dict[int, float]:
    """某位球員在每場比賽（以 MatchRecord.id 為鍵）的排名分數變化。"""
    changes: dict[int, float] = {}

    def record_change(record, before, after):
        if member_id in record.side_a_ids + record.side_b_ids and member_id in after:
            changes[record.id] = conservative_score(after[member_id]) - conservative_score(before[member_id])

    _replay(db.session.scalars(select(Member)).all(), on_match=record_change)
    return changes
