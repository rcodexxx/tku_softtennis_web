from flask import Blueprint

from ..core.auth import get_current_user, staff_required
from ..core.requests import load_args, load_json
from ..core.responses import created, ok
from ..schemas.member import GuestInputSchema, GuestQuerySchema, MemberSchema
from ..services import guest_service

bp = Blueprint("guests", __name__, url_prefix="/guests")

member_schema = MemberSchema()


@bp.get("")
@staff_required
def search_guests():
    guests = guest_service.search_guests(get_current_user(), load_args(GuestQuerySchema()))
    return ok(member_schema.dump(guests, many=True))


@bp.get("/role-options")
def role_options():
    return ok(guest_service.role_options())


@bp.post("")
@staff_required
def create_guest():
    guest = guest_service.create_guest(get_current_user(), load_json(GuestInputSchema()))
    return created(member_schema.dump(guest), message=f"訪客「{guest.name}」已建立。")


@bp.put("/<int:guest_id>")
@staff_required
def update_guest(guest_id: int):
    guest = guest_service.update_guest(get_current_user(), guest_id, load_json(GuestInputSchema(), partial=True))
    return ok(member_schema.dump(guest), message="訪客資料已更新。")


@bp.delete("/<int:guest_id>")
@staff_required
def delete_guest(guest_id: int):
    guest_service.delete_guest(get_current_user(), guest_id)
    return ok(message="訪客已刪除。")
