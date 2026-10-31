from datetime import date, time
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..enums import (
    CourtEnvironmentEnum,
    CourtSurfaceEnum,
    MatchCategoryEnum,
    MatchFormatEnum,
    MatchTimeSlotEnum,
    MatchTypeEnum,
)
from ..extensions import db
from .base import enum_column

if TYPE_CHECKING:
    from .event import Event
    from .match_record import MatchRecord
    from .practice import PracticeSession


class Match(db.Model):
    """比賽事件（日期、場地、賽制等）。每場比賽目前對應一筆 MatchRecord。"""

    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(primary_key=True, comment="比賽唯一識別碼")
    match_date: Mapped[date] = mapped_column(index=True, comment="比賽日期")
    match_time: Mapped[time | None] = mapped_column(comment="比賽時間")
    match_time_slot: Mapped[MatchTimeSlotEnum | None] = mapped_column(
        enum_column(MatchTimeSlotEnum, "match_time_slot_enum_matches"), comment="比賽時間段"
    )
    court_surface: Mapped[CourtSurfaceEnum | None] = mapped_column(
        enum_column(CourtSurfaceEnum, "court_surface_enum_matches"), comment="場地材質"
    )
    court_environment: Mapped[CourtEnvironmentEnum | None] = mapped_column(
        enum_column(CourtEnvironmentEnum, "court_environment_enum_matches"), comment="場地環境"
    )
    total_points: Mapped[int | None] = mapped_column(comment="比賽總得分")
    duration_minutes: Mapped[int | None] = mapped_column(comment="比賽時長(分鐘)")
    youtube_url: Mapped[str | None] = mapped_column(String(500), comment="YouTube 連結")
    notes: Mapped[str | None] = mapped_column(Text, comment="比賽備註")
    match_type: Mapped[MatchTypeEnum] = mapped_column(
        enum_column(MatchTypeEnum, "match_type_enum_matches"), comment="比賽類型 (單打、雙打、混雙)"
    )
    match_format: Mapped[MatchFormatEnum] = mapped_column(
        enum_column(MatchFormatEnum, "match_format_enum_matches"), comment="賽制"
    )

    category: Mapped[MatchCategoryEnum] = mapped_column(
        enum_column(MatchCategoryEnum, "match_category_enum"),
        default=MatchCategoryEnum.INTERNAL,
        server_default=MatchCategoryEnum.INTERNAL.value,
        comment="比賽分類（internal/friendly/event）",
    )
    event_id: Mapped[int | None] = mapped_column(
        ForeignKey("events.id", name="fk_matches_event_id", ondelete="SET NULL"), index=True, comment="所屬賽事ID"
    )

    session_id: Mapped[int | None] = mapped_column(
        ForeignKey("practice_sessions.id", name="fk_matches_session_id", ondelete="SET NULL"),
        index=True,
        comment="所屬練習日ID",
    )

    event: Mapped["Event | None"] = relationship(back_populates="matches")
    session: Mapped["PracticeSession | None"] = relationship(back_populates="matches")
    results: Mapped[list["MatchRecord"]] = relationship(back_populates="match", cascade="all, delete-orphan")

    @property
    def counts_toward_rating(self) -> bool:
        return self.event is None or self.event.counts_toward_rating

    def __repr__(self) -> str:
        return f"<Match id={self.id} date={self.match_date} type={self.match_type}>"
