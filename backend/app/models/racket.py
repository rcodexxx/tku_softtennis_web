from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from ..extensions import db


class Racket(db.Model):
    __tablename__ = "rackets"

    id: Mapped[int] = mapped_column(primary_key=True, comment="球拍唯一識別碼")
    brand: Mapped[str] = mapped_column(String(50), index=True, comment="品牌")
    model_name: Mapped[str] = mapped_column(String(100), index=True, comment="型號名稱")

    def __repr__(self) -> str:
        return f"<Racket id={self.id} {self.brand} {self.model_name}>"
