from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, String, Text, exists, false, or_, select
from sqlalchemy.orm import Mapped, aliased, mapped_column, relationship

from ..domain.rating import starting_rating
from ..enums import BloodTypeEnum, GenderEnum, GuestRoleEnum, MatchPositionEnum
from ..extensions import db
from .base import enum_column, utcnow
from .user import User

if TYPE_CHECKING:
    from .organization import Organization
    from .player_stats import PlayerStats
    from .racket import Racket


class Member(db.Model):
    """球員。正式會員有對應的 User；訪客 (is_guest) 沒有帳號，由建立者管理。"""

    __tablename__ = "members"

    id: Mapped[int] = mapped_column(primary_key=True, comment="隊員唯一識別碼")
    name: Mapped[str] = mapped_column(String(80), comment="真實姓名")
    student_id: Mapped[str | None] = mapped_column(String(20), unique=True, index=True, comment="學號（僅正式會員）")
    gender: Mapped[GenderEnum | None] = mapped_column(
        enum_column(GenderEnum, "gender_enum_members"), comment="性別（male/female）"
    )
    blood_type: Mapped[BloodTypeEnum | None] = mapped_column(
        enum_column(BloodTypeEnum, "blood_type_enum_members"), comment="血型（A/B/AB/O/unknown）"
    )
    position: Mapped[MatchPositionEnum | None] = mapped_column(
        enum_column(MatchPositionEnum, "player_position_enum_members"), comment="擅長位置（front/back/versatile）"
    )

    # 訪客
    is_guest: Mapped[bool] = mapped_column(default=False, comment="是否為訪客球員")
    guest_phone: Mapped[str | None] = mapped_column(String(20), comment="訪客電話")
    guest_identifier: Mapped[str | None] = mapped_column(String(50), unique=True, comment="訪客唯一識別碼")
    guest_role: Mapped[GuestRoleEnum | None] = mapped_column(
        enum_column(GuestRoleEnum, "guest_role_enum"), comment="訪客身份類型"
    )
    guest_notes: Mapped[str | None] = mapped_column(Text, comment="訪客備註")
    created_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), comment="創建訪客的用戶ID")
    created_at: Mapped[datetime | None] = mapped_column(default=utcnow, comment="創建時間")
    last_used_at: Mapped[datetime | None] = mapped_column(comment="最後使用時間（訪客專用）")
    usage_count: Mapped[int | None] = mapped_column(default=0, comment="使用次數（訪客專用）")

    # 隊籍：離隊的人不算校隊，但還會一起打球，所以仍是活躍的球員
    joined_date: Mapped[date | None] = mapped_column(comment="入隊日期")
    leaved_date: Mapped[date | None] = mapped_column(comment="離隊日期")
    is_a_division: Mapped[bool] = mapped_column(default=False, server_default=false(), comment="是否為甲組")

    # 由 rating_service 依比賽紀錄重算；沒打過比賽時為 None
    rating: Mapped[float | None] = mapped_column(Float, comment="分數（1–10）")

    notes: Mapped[str | None] = mapped_column(Text, comment="隊員備註")
    avatar_filename: Mapped[str | None] = mapped_column(String(255), comment="頭像檔名")

    organization_id: Mapped[int | None] = mapped_column(
        ForeignKey("organizations.id", name="fk_members_organization_id"), index=True, comment="所屬組織ID"
    )
    racket_id: Mapped[int | None] = mapped_column(
        ForeignKey("rackets.id", name="fk_members_racket_id"), index=True, comment="使用球拍ID"
    )
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", name="fk_members_user_id", ondelete="CASCADE"),
        unique=True,
        index=True,
        comment="對應的使用者帳號ID",
    )

    organization: Mapped["Organization | None"] = relationship(back_populates="members")
    racket: Mapped["Racket | None"] = relationship()
    user: Mapped["User | None"] = relationship(foreign_keys=[user_id], back_populates="member_profile")
    creator: Mapped["User | None"] = relationship(foreign_keys=[created_by_user_id])
    match_stats_records: Mapped[list["PlayerStats"]] = relationship(cascade="all, delete-orphan")

    @property
    def score(self) -> float:
        """目前分數；還沒打過比賽時用起始分數。"""
        return self.rating if self.rating is not None else starting_rating(self.gender, self.is_a_division)

    @property
    def has_left(self) -> bool:
        return self.leaved_date is not None

    @property
    def is_active(self) -> bool:
        """能不能被選來記錄比賽；只有帳號停用才算不活躍（離隊不算）。"""
        if self.is_guest:
            return True
        return bool(self.user and self.user.is_active)

    @classmethod
    def active_clause(cls):
        """SQL 版的 is_active。"""
        account = aliased(User)
        active_user = exists(select(account.id).where(account.id == cls.user_id, account.is_active.is_(True)))
        return or_(cls.is_guest.is_(True), active_user)

    @property
    def display_name(self) -> str:
        if self.is_guest:
            role = self.guest_role.label if self.guest_role else "訪客"
            suffix = f"-{self.guest_phone[-4:]}" if self.guest_phone else ""
            return f"{self.name} ({role}{suffix})"
        if self.user and self.user.display_name:
            return self.user.display_name
        return self.name

    @property
    def short_display_name(self) -> str:
        if self.is_guest:
            return f"{self.name}(訪)"
        if self.user and self.user.display_name:
            return self.user.display_name
        return self.name

    def __repr__(self) -> str:
        return f"<Member id={self.id} name={self.name!r}{' guest' if self.is_guest else ''}>"
