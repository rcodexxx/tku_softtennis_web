from datetime import datetime

from sqlalchemy import JSON, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from ..extensions import db
from .base import utcnow


class PlayerStats(db.Model):
    """單場比賽的球員統計（目前尚無 API 使用，保留資料表）。"""

    __tablename__ = "player_stats"
    __table_args__ = (UniqueConstraint("match_record_id", "member_id", name="uq_player_stats_match_member"),)

    id: Mapped[int] = mapped_column(primary_key=True, comment="球員單場比賽統計的唯一識別碼")
    match_record_id: Mapped[int] = mapped_column(
        ForeignKey("match_records.id", name="fk_player_stats_match_record_id", ondelete="CASCADE"),
        index=True,
        comment="所屬的比賽記錄ID",
    )
    member_id: Mapped[int] = mapped_column(
        ForeignKey("members.id", name="fk_player_stats_member_id", ondelete="CASCADE"),
        index=True,
        comment="所屬的隊員ID",
    )
    points_won: Mapped[int | None] = mapped_column(default=0, comment="總得分")
    additional_stats: Mapped[dict | None] = mapped_column(JSON, comment="額外統計數據(JSON格式)")
    created_at: Mapped[datetime] = mapped_column(default=utcnow, comment="創建時間")
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow, comment="更新時間")
