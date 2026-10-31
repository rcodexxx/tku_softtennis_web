import uuid

from sqlalchemy import or_, select
from sqlalchemy.orm import joinedload

from ..core.db import get_or_404
from ..core.errors import ConflictError, NotFoundError
from ..enums import GuestRoleEnum
from ..extensions import db
from ..models import Member, Organization, User
from . import avatar_service, rating_service
from ._queries import has_match_records

# API 欄位 -> Member 欄位
_FIELD_MAP = {
    "name": "name",
    "phone": "guest_phone",
    "guest_role": "guest_role",
    "organization_id": "organization_id",
    "notes": "guest_notes",
    # 性別與甲組決定起始分數，讓系統對校外對手的實力猜得比較準
    "gender": "gender",
    "is_a_division": "is_a_division",
}


def role_options() -> list[dict]:
    return [{"value": role.value, "label": role.label} for role in GuestRoleEnum]


def search_guests(user: User, params: dict) -> list[Member]:
    stmt = (
        select(Member)
        .options(joinedload(Member.organization))
        .where(Member.is_guest.is_(True))
        .order_by(Member.usage_count.desc(), Member.last_used_at.desc(), Member.id.desc())
        .limit(params["limit"])
    )
    if params.get("q"):
        like = f"%{params['q']}%"
        stmt = stmt.where(or_(Member.name.ilike(like), Member.guest_phone.ilike(like), Member.guest_notes.ilike(like)))
    if params.get("guest_role"):
        stmt = stmt.where(Member.guest_role == params["guest_role"])
    if params.get("organization_id"):
        stmt = stmt.where(Member.organization_id == params["organization_id"])
    return list(db.session.scalars(stmt).unique())


def create_guest(user: User, data: dict) -> Member:
    existing = db.session.scalar(select(Member).where(Member.is_guest.is_(True), Member.name == data["name"]))
    if existing:
        raise ConflictError(f"已經有名為「{data['name']}」的訪客。", details={"existing_guest_id": existing.id})
    _ensure_organization(data)

    guest = Member(
        is_guest=True,
        guest_identifier=f"GUEST_{uuid.uuid4().hex[:16].upper()}",
        created_by_user_id=user.id,
        usage_count=0,
        **{column: data.get(field) for field, column in _FIELD_MAP.items()},
    )
    db.session.add(guest)
    db.session.commit()
    return guest


def update_guest(user: User, guest_id: int, data: dict) -> Member:
    guest = _get_owned_guest(user, guest_id)
    _ensure_organization(data)
    for field, column in _FIELD_MAP.items():
        if field in data:
            setattr(guest, column, data[field])
    if "gender" in data or "is_a_division" in data:
        rating_service.recalculate_all()
    db.session.commit()
    return guest


def delete_guest(user: User, guest_id: int) -> None:
    guest = _get_owned_guest(user, guest_id)
    if db.session.scalar(select(has_match_records(guest.id))):
        raise ConflictError("此訪客已參與比賽，無法刪除。")
    db.session.delete(guest)
    db.session.commit()
    avatar_service.delete_file(guest.avatar_filename)


def _get_owned_guest(user: User, guest_id: int) -> Member:
    """訪客是所有幹部共用的，誰建立的都可以修改。"""
    guest = get_or_404(Member, guest_id, "找不到指定的訪客。")
    if not guest.is_guest:
        raise NotFoundError("找不到指定的訪客。")
    return guest


def _ensure_organization(data: dict) -> None:
    if data.get("organization_id") and db.session.get(Organization, data["organization_id"]) is None:
        raise NotFoundError("指定的組織不存在。")
