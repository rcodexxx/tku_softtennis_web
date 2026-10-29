from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

from ..enums import UserRoleEnum
from ..extensions import db
from .base import enum_column, utcnow

if TYPE_CHECKING:
    from .member import Member


class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, comment="使用者唯一識別碼")
    username: Mapped[str] = mapped_column(String(30), unique=True, index=True, comment="帳號 (登入用)")
    email: Mapped[str | None] = mapped_column(
        String(120), unique=True, index=True, comment="電子郵件 (通常用於登入或通知)"
    )
    password_hash: Mapped[str] = mapped_column(String(256), comment="雜湊後的密碼")
    display_name: Mapped[str | None] = mapped_column(String(50), comment="暱稱 (顯示名稱)")
    role: Mapped[UserRoleEnum] = mapped_column(
        enum_column(UserRoleEnum, "user_role_enum"), default=UserRoleEnum.MEMBER, comment="使用者角色"
    )
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow, comment="最後更新時間")
    is_active: Mapped[bool] = mapped_column(default=True, comment="帳號是否啟用")

    member_profile: Mapped["Member | None"] = relationship(
        foreign_keys="Member.user_id", back_populates="user", cascade="all, delete-orphan"
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return bool(self.password_hash) and check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username!r} role={self.role}>"
