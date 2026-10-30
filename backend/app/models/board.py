from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db
from .base import utcnow

if TYPE_CHECKING:
    from .member import Member

board_members = Table(
    "board_members",
    db.metadata,
    Column("board_id", ForeignKey("boards.id", name="fk_board_members_board_id", ondelete="CASCADE"), primary_key=True),
    Column(
        "member_id", ForeignKey("members.id", name="fk_board_members_member_id", ondelete="CASCADE"), primary_key=True
    ),
)


class Board(db.Model):
    """自訂榜單（例如「打球嗎」）：用同一套分數，只是名單由自己挑。"""

    __tablename__ = "boards"

    id: Mapped[int] = mapped_column(primary_key=True, comment="榜單唯一識別碼")
    name: Mapped[str] = mapped_column(String(50), unique=True, comment="榜單名稱")
    created_at: Mapped[datetime | None] = mapped_column(default=utcnow, comment="建立時間")

    members: Mapped[list["Member"]] = relationship(secondary=board_members, order_by="Member.name")

    def __repr__(self) -> str:
        return f"<Board id={self.id} name={self.name!r}>"
