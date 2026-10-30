from flask import Blueprint

from ..core.auth import admin_required, staff_required
from ..core.requests import load_json
from ..core.responses import created, ok
from ..schemas.season import RosterCandidateSchema, SeasonInputSchema, SeasonSchema
from ..services import leaderboard_service, season_service

bp = Blueprint("seasons", __name__, url_prefix="/seasons")

season_schema = SeasonSchema()
candidate_schema = RosterCandidateSchema()


@bp.get("")
def list_seasons():
    return ok(season_schema.dump(season_service.summaries(), many=True))


@bp.get("/roster")
@staff_required
def roster():
    stats = leaderboard_service.season_data(season_service.current_season()).stats
    rows = []
    for member, status in season_service.roster_candidates():
        member_stats = stats.get(member.id, leaderboard_service.MatchStats())
        rows.append(
            {
                "member": member,
                "gender": member.gender.value if member.gender else None,
                "status": status,
                "total_matches": member_stats.total_matches,
                "last_match_date": member_stats.last_match_date,
            }
        )
    return ok(candidate_schema.dump(rows, many=True))


@bp.post("")
@admin_required
def start_season():
    season = season_service.start_season(load_json(SeasonInputSchema()))
    return created(season_schema.dump(season_service.describe(season)), message=f"「{season.name}」已開始。")
