from flask import Blueprint

from ..core.auth import get_current_user, login_required
from ..core.requests import load_args, load_json
from ..core.responses import ok
from ..schemas.common import PageQuerySchema
from ..schemas.match import MatchRecordSchema
from ..schemas.profile import ProfileSchema, ProfileUpdateSchema
from ..services import profile_service

bp = Blueprint("profile", __name__, url_prefix="/profile")

profile_schema = ProfileSchema()
record_schema = MatchRecordSchema()


@bp.get("/me")
@login_required
def get_profile():
    return ok(profile_schema.dump(get_current_user()))


@bp.put("/me")
@login_required
def update_profile():
    data = load_json(ProfileUpdateSchema(), partial=True)
    user = profile_service.update_profile(get_current_user(), data)
    return ok(profile_schema.dump(user), message="個人資料已更新。")


@bp.get("/me/matches")
@login_required
def my_matches():
    params = load_args(PageQuerySchema())
    user = get_current_user()
    page = profile_service.my_matches(user, params["page"], params["per_page"])
    member_id = user.member_profile.id
    items = [
        {**record_schema.dump(record), "perspective": profile_service.perspective(record, member_id)}
        for record in page.items
    ]
    return ok(items, meta=page.meta)
