from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..enums import MatchOutcomeEnum, MatchStartServeEnum
from ..extensions import db
from .base import enum_column

if TYPE_CHECKING:
    from .match import Match
    from .member import Member

MAX_GAMES = 9


def _player_fk(slot: int):
    return ForeignKey("members.id", name=f"fk_match_records_p{slot}_id", ondelete="SET NULL")


def _game_score(game: int, side: str):
    return mapped_column(default=0, comment=f"第{game}局{side}方得分")


class MatchRecord(db.Model):
    """一場比賽的對戰紀錄。A 方為 player1/player2，B 方為 player3/player4。"""

    __tablename__ = "match_records"

    id: Mapped[int] = mapped_column(primary_key=True, comment="比賽記錄唯一識別碼")
    match_id: Mapped[int | None] = mapped_column(
        ForeignKey("matches.id", name="fk_match_records_match_id", ondelete="CASCADE"),
        index=True,
        comment="所屬比賽事件ID",
    )
    player1_id: Mapped[int] = mapped_column(_player_fk(1), index=True)
    player2_id: Mapped[int | None] = mapped_column(_player_fk(2), index=True)
    player3_id: Mapped[int] = mapped_column(_player_fk(3), index=True)
    player4_id: Mapped[int | None] = mapped_column(_player_fk(4), index=True)

    a_games: Mapped[int] = mapped_column(comment="A方贏得的總局數")
    b_games: Mapped[int] = mapped_column(comment="B方贏得的總局數")
    side_a_outcome: Mapped[MatchOutcomeEnum] = mapped_column(
        enum_column(MatchOutcomeEnum, "outcome_enum_match_records"), comment="A方視角的比賽結果 (勝/負)"
    )
    first_serve_side: Mapped[MatchStartServeEnum | None] = mapped_column(
        enum_column(MatchStartServeEnum, "serve_start_enum_match_records"), comment="第一局發球方 (A方/B方)"
    )

    game1_a_score: Mapped[int | None] = _game_score(1, "A")
    game1_b_score: Mapped[int | None] = _game_score(1, "B")
    game2_a_score: Mapped[int | None] = _game_score(2, "A")
    game2_b_score: Mapped[int | None] = _game_score(2, "B")
    game3_a_score: Mapped[int | None] = _game_score(3, "A")
    game3_b_score: Mapped[int | None] = _game_score(3, "B")
    game4_a_score: Mapped[int | None] = _game_score(4, "A")
    game4_b_score: Mapped[int | None] = _game_score(4, "B")
    game5_a_score: Mapped[int | None] = _game_score(5, "A")
    game5_b_score: Mapped[int | None] = _game_score(5, "B")
    game6_a_score: Mapped[int | None] = _game_score(6, "A")
    game6_b_score: Mapped[int | None] = _game_score(6, "B")
    game7_a_score: Mapped[int | None] = _game_score(7, "A")
    game7_b_score: Mapped[int | None] = _game_score(7, "B")
    game8_a_score: Mapped[int | None] = _game_score(8, "A")
    game8_b_score: Mapped[int | None] = _game_score(8, "B")
    game9_a_score: Mapped[int | None] = _game_score(9, "A")
    game9_b_score: Mapped[int | None] = _game_score(9, "B")

    # 雙打的前衛（網前）是誰；另一位就是後衛。可以不填
    a_front_id: Mapped[int | None] = mapped_column(
        ForeignKey("members.id", name="fk_match_records_a_front_id", ondelete="SET NULL"), comment="A方前衛"
    )
    b_front_id: Mapped[int | None] = mapped_column(
        ForeignKey("members.id", name="fk_match_records_b_front_id", ondelete="SET NULL"), comment="B方前衛"
    )

    match: Mapped["Match | None"] = relationship(back_populates="results")
    player1: Mapped["Member"] = relationship(foreign_keys=[player1_id])
    player2: Mapped["Member | None"] = relationship(foreign_keys=[player2_id])
    player3: Mapped["Member"] = relationship(foreign_keys=[player3_id])
    player4: Mapped["Member | None"] = relationship(foreign_keys=[player4_id])

    @property
    def side_a_ids(self) -> list[int]:
        return [pid for pid in (self.player1_id, self.player2_id) if pid]

    @property
    def side_b_ids(self) -> list[int]:
        return [pid for pid in (self.player3_id, self.player4_id) if pid]

    @property
    def side_a_won(self) -> bool:
        return self.side_a_outcome == MatchOutcomeEnum.WIN

    @property
    def game_scores(self) -> list[tuple[int, int]]:
        """九局的 (A 方得分, B 方得分)，未進行的局為 (0, 0)。"""
        return [
            (getattr(self, f"game{n}_a_score") or 0, getattr(self, f"game{n}_b_score") or 0)
            for n in range(1, MAX_GAMES + 1)
        ]

    @game_scores.setter
    def game_scores(self, scores: list[tuple[int, int]]) -> None:
        padded = list(scores) + [(0, 0)] * (MAX_GAMES - len(scores))
        for n, (a_score, b_score) in enumerate(padded[:MAX_GAMES], start=1):
            setattr(self, f"game{n}_a_score", a_score)
            setattr(self, f"game{n}_b_score", b_score)

    def __repr__(self) -> str:
        return f"<MatchRecord id={self.id} {self.a_games}-{self.b_games}>"
