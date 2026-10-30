from datetime import date, datetime

from sqlalchemy import ForeignKey, String, false
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db
from .base import utcnow


class Season(db.Model):
    """賽季。從 start_date 開始，到下一個賽季開始的前一天為止；比賽依日期歸屬賽季。"""

    __tablename__ = "seasons"

    id: Mapped[int] = mapped_column(primary_key=True, comment="賽季唯一識別碼")
    name: Mapped[str] = mapped_column(String(50), unique=True, comment="賽季名稱")
    start_date: Mapped[date] = mapped_column(unique=True, index=True, comment="開始日期")
    created_at: Mapped[datetime | None] = mapped_column(default=utcnow, comment="建立時間")

    rosters: Mapped[list["SeasonRoster"]] = relationship(cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Season id={self.id} name={self.name!r} start={self.start_date}>"


class SeasonRoster(db.Model):
    """賽季結束時每位球員的隊籍，讓舊賽季的排行榜照當時的名單分校隊／校友會。"""

    __tablename__ = "season_rosters"

    season_id: Mapped[int] = mapped_column(
        ForeignKey("seasons.id", name="fk_season_rosters_season_id", ondelete="CASCADE"), primary_key=True
    )
    member_id: Mapped[int] = mapped_column(
        ForeignKey("members.id", name="fk_season_rosters_member_id", ondelete="CASCADE"), primary_key=True
    )
    organization_id: Mapped[int | None] = mapped_column(
        ForeignKey("organizations.id", name="fk_season_rosters_organization_id", ondelete="SET NULL"),
        comment="賽季結束時所屬組織ID",
    )
    has_left: Mapped[bool] = mapped_column(default=False, server_default=false(), comment="賽季結束時是否已離隊")
