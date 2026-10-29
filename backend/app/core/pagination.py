import math
from dataclasses import dataclass
from typing import Any

from sqlalchemy import Select, func, select

from ..extensions import db


@dataclass
class Page:
    items: list[Any]
    page: int
    per_page: int
    total: int

    @property
    def pages(self) -> int:
        return math.ceil(self.total / self.per_page) if self.per_page else 0

    @property
    def meta(self) -> dict:
        return {"page": self.page, "per_page": self.per_page, "total": self.total, "pages": self.pages}


def paginate(stmt: Select, page: int, per_page: int) -> Page:
    total = db.session.scalar(select(func.count()).select_from(stmt.order_by(None).subquery()))
    items = db.session.scalars(stmt.limit(per_page).offset((page - 1) * per_page)).unique().all()
    return Page(items=list(items), page=page, per_page=per_page, total=total or 0)


def paginate_list(items: list, page: int, per_page: int) -> Page:
    start = (page - 1) * per_page
    return Page(items=items[start : start + per_page], page=page, per_page=per_page, total=len(items))
