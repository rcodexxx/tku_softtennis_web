from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, Text, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db
from .base import utcnow

if TYPE_CHECKING:
    from .match import Match


class Event(db.Model):
    """自訂賽事（例如某某盃）。比賽可以歸到某個賽事；賽事本身不排名。"""

    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True, comment="賽事唯一識別碼")
    name: Mapped[str] = mapped_column(String(100), comment="賽事名稱")
    start_date: Mapped[date | None] = mapped_column(comment="開始日期")
    end_date: Mapped[date | None] = mapped_column(comment="結束日期")
    location: Mapped[str | None] = mapped_column(String(100), comment="地點")
    notes: Mapped[str | None] = mapped_column(Text, comment="備註")
    # 表演賽之類不想影響分數的賽事可以關掉
    counts_toward_rating: Mapped[bool] = mapped_column(default=True, server_default=true(), comment="是否計入分數")
    created_at: Mapped[datetime | None] = mapped_column(default=utcnow, comment="建立時間")

    matches: Mapped[list["Match"]] = relationship(back_populates="event")

    def __repr__(self) -> str:
        return f"<Event id={self.id} name={self.name!r}>"
