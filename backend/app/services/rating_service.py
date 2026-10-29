"""把 domain.rating 的計算結果寫回資料庫。

評分與比賽順序有關，所以只要不是「新增最新一場比賽」，一律從頭重算全部比賽。
"""

from sqlalchemy import exists, select

from ..domain.rating import Participant, Rating, rate_match
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


def recalculate_all() -> None:
    db.session.flush()
    members = db.session.scalars(select(Member)).all()
    ratings = {m.id: Rating() for m in members}
    genders = {m.id: m.gender for m in members}

    records = db.session.scalars(
        select(MatchRecord).join(MatchRecord.match).order_by(Match.match_date.asc(), MatchRecord.id.asc())
    )
    for record in records:
        _apply(record, ratings, genders)

    for member in members:
        member.mu, member.sigma = ratings[member.id].mu, ratings[member.id].sigma


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
