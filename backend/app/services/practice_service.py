"""練習日：到場名單、排下一輪、當天戰報。"""

from collections import Counter
from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..core.db import get_or_404
from ..core.errors import NotFoundError
from ..domain import pairing
from ..enums import MatchOutcomeEnum
from ..extensions import db
from ..models import Match, MatchRecord, Member, PracticeSession
from . import rating_service


def list_sessions() -> list[PracticeSession]:
    stmt = select(PracticeSession).options(
        selectinload(PracticeSession.attendees), selectinload(PracticeSession.matches).selectinload(Match.results)
    )
    return list(db.session.scalars(stmt.order_by(PracticeSession.session_date.desc(), PracticeSession.id.desc())))


def get_session(session_id: int) -> PracticeSession:
    return get_or_404(PracticeSession, session_id, "找不到指定的練習日。")


def create_session(data: dict) -> PracticeSession:
    session = PracticeSession(session_date=data["session_date"], location=data.get("location"), notes=data.get("notes"))
    session.attendees = _members(data.get("player_ids", []))
    db.session.add(session)
    db.session.commit()
    return session


def update_session(session_id: int, data: dict) -> PracticeSession:
    session = get_session(session_id)
    for name in ("session_date", "location", "notes"):
        if name in data:
            setattr(session, name, data[name])
    if "player_ids" in data:
        session.attendees = _members(data["player_ids"])
    db.session.commit()
    return session


def delete_session(session_id: int) -> None:
    """刪掉練習日；當天的比賽紀錄保留，只是不再屬於這一天。"""
    db.session.delete(get_session(session_id))
    db.session.commit()


def records_of(session: PracticeSession) -> list[MatchRecord]:
    return sorted((record for match in session.matches for record in match.results), key=lambda r: r.id)


def next_round(session: PracticeSession, courts: int, mode: str, seed: int) -> pairing.Round:
    """依今天已經打過的場次與搭檔，排出下一輪。"""
    played: Counter[int] = Counter()
    partnered: Counter[pairing.Pair] = Counter()
    for record in records_of(session):
        for side in (record.side_a_ids, record.side_b_ids):
            played.update(side)
            if len(side) == 2:
                partnered[pairing.pair_key(*side)] += 1
    ratings = {member.id: member.score for member in session.attendees}
    return pairing.next_round([m.id for m in session.attendees], ratings, played, partnered, courts, mode, seed)


@dataclass
class DayLine:
    """一位球員當天的戰績與分數變化。"""

    player: Member
    wins: int = 0
    losses: int = 0
    games_for: int = 0
    games_against: int = 0
    rating_before: float | None = None
    rating_after: float | None = None

    @property
    def rating_change(self) -> float | None:
        if self.rating_before is None or self.rating_after is None:
            return None
        return self.rating_after - self.rating_before


@dataclass
class DayPair:
    players: tuple[Member, Member]
    wins: int = 0
    losses: int = 0


@dataclass
class DaySummary:
    lines: list[DayLine] = field(default_factory=list)
    pairs: list[DayPair] = field(default_factory=list)


def summary(session: PracticeSession) -> DaySummary:
    records = records_of(session)
    results = rating_service.results_for_records({record.id for record in records})
    lines: dict[int, DayLine] = {}
    pairs: dict[pairing.Pair, DayPair] = {}
    for record in records:
        if record.side_a_outcome not in (MatchOutcomeEnum.WIN, MatchOutcomeEnum.LOSS):
            continue
        a_won = record.side_a_outcome == MatchOutcomeEnum.WIN
        for side, won, scored, conceded in (
            (record.side_a_ids, a_won, record.a_games, record.b_games),
            (record.side_b_ids, not a_won, record.b_games, record.a_games),
        ):
            for pid in side:
                line = lines.get(pid) or lines.setdefault(pid, DayLine(db.session.get(Member, pid)))
                line.wins += won
                line.losses += not won
                line.games_for += scored
                line.games_against += conceded
                result = results.get(record.id, {}).get(pid)
                if result:
                    line.rating_before = result.before if line.rating_before is None else line.rating_before
                    line.rating_after = result.after
            if len(side) == 2:
                key = pairing.pair_key(*side)
                pair = pairs.get(key) or pairs.setdefault(
                    key, DayPair((db.session.get(Member, key[0]), db.session.get(Member, key[1])))
                )
                pair.wins += won
                pair.losses += not won
    return DaySummary(
        sorted(lines.values(), key=lambda line: (-line.wins, line.losses, -(line.games_for - line.games_against))),
        sorted(pairs.values(), key=lambda pair: (-pair.wins, pair.losses)),
    )


def _members(ids: list[int]) -> list[Member]:
    members = list(db.session.scalars(select(Member).where(Member.id.in_(set(ids)))))
    if len(members) != len(set(ids)):
        raise NotFoundError("有球員不存在。")
    return members
