from sqlalchemy import select

from ..core.db import get_or_404
from ..core.errors import ConflictError
from ..extensions import db
from ..models import Organization


def list_organizations() -> list[Organization]:
    return list(db.session.scalars(select(Organization).order_by(Organization.name)))


def get_organization(org_id: int) -> Organization:
    return get_or_404(Organization, org_id, "找不到指定的組織。")


def create_organization(data: dict) -> Organization:
    _ensure_unique(data)
    org = Organization(**data)
    db.session.add(org)
    db.session.commit()
    return org


def update_organization(org_id: int, data: dict) -> Organization:
    org = get_organization(org_id)
    _ensure_unique(data, exclude_id=org.id)
    for field, value in data.items():
        setattr(org, field, value)
    db.session.commit()
    return org


def delete_organization(org_id: int) -> None:
    org = get_organization(org_id)
    if org.members:
        raise ConflictError(f"組織「{org.name}」尚有 {len(org.members)} 位成員，請先將成員移至其他組織。")
    db.session.delete(org)
    db.session.commit()


def _ensure_unique(data: dict, exclude_id: int | None = None) -> None:
    for field, label in (("name", "名稱"), ("short_name", "簡稱")):
        value = data.get(field)
        if not value:
            continue
        stmt = select(Organization.id).where(getattr(Organization, field) == value)
        if exclude_id is not None:
            stmt = stmt.where(Organization.id != exclude_id)
        if db.session.scalar(stmt):
            raise ConflictError(f"組織{label}「{value}」已存在。")
