from flask import Blueprint
from flask_jwt_extended import verify_jwt_in_request

from ..core.auth import get_current_user, is_staff
from ..core.errors import PermissionDeniedError, ValidationError
from ..core.requests import load_args
from ..core.responses import ok
from ..schemas.leaderboard import LeaderboardQuerySchema, SeasonQuerySchema
from ..schemas.member import MemberSchema
from ..schemas.season import SeasonSchema
from ..services import leaderboard_service, season_service

bp = Blueprint("leaderboard", __name__, url_prefix="/leaderboard")

member_schema = MemberSchema()
season_schema = SeasonSchema()


@bp.get("")
def get_leaderboard():
    params = load_args(LeaderboardQuerySchema())
    if params.get("board_id"):
        _require_staff()
    season, page = leaderboard_service.leaderboard(params)
    rows = [
        {**member_schema.dump(e.member), **e.stats.to_dict(), "rating": round(e.score, 2), "rank": e.rank}
        for e in page.items
    ]
    return ok(rows, meta={**page.meta, "season": season_schema.dump(season_service.describe(season))})


@bp.get("/statistics")
def get_statistics():
    return ok(leaderboard_service.statistics(load_args(SeasonQuerySchema()).get("season_id")))


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


def _require_staff() -> None:
    """自訂榜單目前只給幹部看。"""
    verify_jwt_in_request()
    if not is_staff(get_current_user()):
        raise PermissionDeniedError()
