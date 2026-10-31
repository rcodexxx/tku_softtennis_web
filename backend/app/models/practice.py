from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db
from .base import utcnow

if TYPE_CHECKING:
    from .match import Match
    from .member import Member

practice_attendees = Table(
    "practice_attendees",
    db.metadata,
    Column(
        "session_id",
        ForeignKey("practice_sessions.id", name="fk_practice_attendees_session_id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "member_id",
        ForeignKey("members.id", name="fk_practice_attendees_member_id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class PracticeSession(db.Model):
    """練習日：一天到場的人輪流排組對打，比賽都掛在這一天底下。"""

    __tablename__ = "practice_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, comment="練習日唯一識別碼")
    session_date: Mapped[date] = mapped_column(index=True, comment="日期")
    location: Mapped[str | None] = mapped_column(String(100), comment="地點")
    notes: Mapped[str | None] = mapped_column(Text, comment="備註")
    created_at: Mapped[datetime | None] = mapped_column(default=utcnow, comment="建立時間")

    attendees: Mapped[list["Member"]] = relationship(secondary=practice_attendees, order_by="Member.name")
    matches: Mapped[list["Match"]] = relationship(back_populates="session")

    def __repr__(self) -> str:
        return f"<PracticeSession id={self.id} date={self.session_date}>"
