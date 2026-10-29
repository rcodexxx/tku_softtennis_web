from sqlalchemy import or_, select
from sqlalchemy.orm import joinedload

from ..core.auth import ADMIN_ROLES
from ..core.db import get_or_404
from ..core.errors import ConflictError, NotFoundError, PermissionDeniedError
from ..domain.rating import CONSERVATIVE_K
from ..enums import UserRoleEnum
from ..extensions import db
from ..models import Member, Organization, Racket, User
from . import avatar_service
from ._queries import has_match_records

USER_FIELDS = ("email", "display_name", "role", "is_active")
MEMBER_FIELDS = (
    "name",
    "student_id",
    "gender",
    "blood_type",
    "position",
    "organization_id",
    "racket_id",
    "joined_date",
    "leaved_date",
    "notes",
)

_SORT_COLUMNS = {
    "name": Member.name,
    "conservative_score": Member.mu - CONSERVATIVE_K * Member.sigma,
    "joined_date": Member.joined_date,
    "created_at": Member.created_at,
}


def list_members(params: dict) -> list[Member]:
    stmt = select(Member).options(joinedload(Member.user), joinedload(Member.organization))
    if not params["include_guests"]:
        stmt = stmt.where(Member.is_guest.is_(False))
    if not params["include_inactive"]:
        stmt = stmt.where(Member.active_clause())
    if params.get("organization_id"):
        stmt = stmt.where(Member.organization_id == params["organization_id"])
    if params.get("q"):
        like = f"%{params['q']}%"
        stmt = stmt.outerjoin(Member.user).where(
            or_(
                Member.name.ilike(like),
                Member.student_id.ilike(like),
                User.display_name.ilike(like),
                User.username.ilike(like),
            )
        )
    column = _SORT_COLUMNS[params["sort_by"]]
    stmt = stmt.order_by(column.desc() if params["sort_order"] == "desc" else column.asc(), Member.id)
    if params.get("limit"):
        stmt = stmt.limit(params["limit"])
    return list(db.session.scalars(stmt).unique())


def get_member(member_id: int) -> Member:
    return get_or_404(Member, member_id, "找不到指定的成員。")


def create_member(actor: User, data: dict) -> Member:
    _ensure_can_assign_role(actor, data["role"], current=UserRoleEnum.MEMBER)
    _ensure_user_unique(data)
    _ensure_references(data)
    user = User(
        username=data["username"],
        email=data.get("email"),
        display_name=data.get("display_name") or data["name"],
        role=data["role"],
        is_active=data.get("is_active", True),
    )
    user.set_password(data.get("password") or data["username"])
    member = Member(user=user, **{field: data[field] for field in MEMBER_FIELDS if field in data})
    db.session.add_all([user, member])
    db.session.commit()
    return member


def update_member(actor: User, member_id: int, data: dict) -> Member:
    member = get_member(member_id)
    if member.user and "role" in data:
        _ensure_can_assign_role(actor, data["role"], current=member.user.role)
    _ensure_references(data)
    for field in MEMBER_FIELDS:
        if field in data:
            setattr(member, field, data[field])

    if member.user:
        _ensure_user_unique(data, exclude_user_id=member.user.id)
        for field in USER_FIELDS:
            if field in data:
                setattr(member.user, field, data[field])

    db.session.commit()
    return member


def delete_member(member_id: int) -> None:
    member = get_member(member_id)
    if db.session.scalar(select(has_match_records(member.id))):
        raise ConflictError("此成員已有比賽紀錄，無法刪除。請改為設定離隊日期。")
    if member.user:
        db.session.delete(member.user)  # 透過 cascade 一併刪除 member
    else:
        db.session.delete(member)
    db.session.commit()
    avatar_service.delete_file(member.avatar_filename)


def _ensure_can_assign_role(actor: User, role: UserRoleEnum, current: UserRoleEnum) -> None:
    """只有管理員可以變更角色。"""
    if role != current and actor.role not in ADMIN_ROLES:
        raise PermissionDeniedError("只有管理員可以變更成員角色。")


def _ensure_user_unique(data: dict, exclude_user_id: int | None = None) -> None:
    for field, label in (("username", "手機號碼"), ("email", "電子郵件")):
        value = data.get(field)
        if not value:
            continue
        stmt = select(User.id).where(getattr(User, field) == value)
        if exclude_user_id is not None:
            stmt = stmt.where(User.id != exclude_user_id)
        if db.session.scalar(stmt):
            raise ConflictError(f"{label} {value} 已被其他帳號使用。")


def _ensure_references(data: dict) -> None:
    if data.get("organization_id") and db.session.get(Organization, data["organization_id"]) is None:
        raise NotFoundError("指定的組織不存在。")
    if data.get("racket_id") and db.session.get(Racket, data["racket_id"]) is None:
        raise NotFoundError("指定的球拍不存在。")
