from flask import Blueprint

from ..core.auth import admin_required
from ..core.requests import load_json
from ..core.responses import created, ok
from ..schemas.season import SeasonInputSchema, SeasonSchema
from ..services import season_service

bp = Blueprint("seasons", __name__, url_prefix="/seasons")

season_schema = SeasonSchema()


@bp.get("")
def list_seasons():
    return ok(season_schema.dump(season_service.summaries(), many=True))


@bp.post("")
@admin_required
def start_season():
    season = season_service.start_season(load_json(SeasonInputSchema()))
    return created(season_schema.dump(season_service.describe(season)), message=f"「{season.name}」已開始。")
