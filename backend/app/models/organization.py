from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db

if TYPE_CHECKING:
    from .member import Member


class Organization(db.Model):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(primary_key=True, comment="組織唯一識別碼")
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, comment="組織全名")
    short_name: Mapped[str | None] = mapped_column(String(30), unique=True, index=True, comment="組織簡稱或代號")
    description: Mapped[str | None] = mapped_column(Text, comment="組織描述")
    contact_person: Mapped[str | None] = mapped_column(String(50), comment="主要聯絡人")
    contact_email: Mapped[str | None] = mapped_column(String(120), comment="聯絡Email")
    contact_phone: Mapped[str | None] = mapped_column(String(30), comment="聯絡電話")

    members: Mapped[list["Member"]] = relationship(back_populates="organization")

    def __repr__(self) -> str:
        return f"<Organization id={self.id} name={self.name!r}>"
