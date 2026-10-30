from flask import Blueprint, request

from ..core.auth import admin_required, get_current_user, login_required, staff_required
from ..core.requests import load_args, load_json
from ..core.responses import created, ok
from ..schemas.member import MemberCreateSchema, MemberQuerySchema, MemberSchema, MemberUpdateSchema
from ..schemas.roster import RosterCandidateSchema, RosterUpdateSchema
from ..services import avatar_service, leaderboard_service, member_service, roster_service, season_service

bp = Blueprint("members", __name__, url_prefix="/members")

member_schema = MemberSchema()
candidate_schema = RosterCandidateSchema()


@bp.get("")
def list_members():
    members = member_service.list_members(load_args(MemberQuerySchema()))
    return ok(member_schema.dump(members, many=True), meta={"total": len(members)})


@bp.get("/roster")
@staff_required
def roster():
    stats = leaderboard_service.season_data(season_service.current_season()).stats
    rows = []
    for member in roster_service.candidates():
        member_stats = stats.get(member.id, leaderboard_service.MatchStats())
        rows.append(
            {
                "member": member,
                "gender": member.gender.value if member.gender else None,
                "is_a_division": member.is_a_division,
                "status": roster_service.status_of(member),
                "total_matches": member_stats.total_matches,
                "last_match_date": member_stats.last_match_date,
            }
        )
    return ok(candidate_schema.dump(rows, many=True))


@bp.put("/roster")
@staff_required
def update_roster():
    changed = roster_service.update(load_json(RosterUpdateSchema())["roster"])
    return ok(member_schema.dump(changed, many=True), message=f"已更新 {len(changed)} 位隊員的隊籍。")


@bp.get("/<int:member_id>")
def get_member(member_id: int):
    return ok(member_schema.dump(member_service.get_member(member_id)))


@bp.get("/<int:member_id>/stats")
def get_member_stats(member_id: int):
    member, stats = leaderboard_service.member_stats(member_id)
    return ok({"member": member_schema.dump(member), **stats.to_dict()})


@bp.post("")
@staff_required
def create_member():
    member = member_service.create_member(get_current_user(), load_json(MemberCreateSchema()))
    return created(member_schema.dump(member), message="成員已建立。")


@bp.put("/<int:member_id>")
@staff_required
def update_member(member_id: int):
    member = member_service.update_member(get_current_user(), member_id, load_json(MemberUpdateSchema(), partial=True))
    return ok(member_schema.dump(member), message="成員已更新。")


@bp.delete("/<int:member_id>")
@admin_required
def delete_member(member_id: int):
    member_service.delete_member(member_id)
    return ok(message="成員已刪除。")


@bp.post("/<int:member_id>/avatar")
@login_required
def upload_avatar(member_id: int):
    member = avatar_service.save_avatar(get_current_user(), member_id, request.files.get("file"))
    return ok(member_schema.dump(member), message="頭像已更新。")


@bp.delete("/<int:member_id>/avatar")
@login_required
def delete_avatar(member_id: int):
    member = avatar_service.remove_avatar(get_current_user(), member_id)
    return ok(member_schema.dump(member), message="頭像已移除。")
