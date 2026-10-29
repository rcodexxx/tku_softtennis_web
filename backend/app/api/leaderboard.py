from flask import Blueprint

from ..core.errors import ValidationError
from ..core.requests import load_args
from ..core.responses import ok
from ..schemas.leaderboard import LeaderboardQuerySchema
from ..schemas.member import MemberSchema
from ..services import leaderboard_service

bp = Blueprint("leaderboard", __name__, url_prefix="/leaderboard")

member_schema = MemberSchema()


@bp.get("")
def get_leaderboard():
    page = leaderboard_service.leaderboard(load_args(LeaderboardQuerySchema()))
    rows = [{**member_schema.dump(e.member), **e.stats.to_dict(), "rank": e.rank} for e in page.items]
    return ok(rows, meta=page.meta)


@bp.get("/statistics")
def get_statistics():
    return ok(leaderboard_service.statistics())


@bp.get("/compare/<int:member1_id>/<int:member2_id>")
def compare(member1_id: int, member2_id: int):
    if member1_id == member2_id:
        raise ValidationError("不能比較同一位球員。")
    result = leaderboard_service.compare(member1_id, member2_id)
    return ok(
        {
            "member1": {**member_schema.dump(result["member1"]), **result["member1_stats"].to_dict()},
            "member2": {**member_schema.dump(result["member2"]), **result["member2_stats"].to_dict()},
            "comparison": result["comparison"],
        }
    )
