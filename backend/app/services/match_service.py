from sqlalchemy import and_, not_, or_, select
from sqlalchemy.orm import joinedload

from ..core.db import get_or_404
from ..core.errors import NotFoundError
from ..core.pagination import Page, paginate
from ..domain import scoring
from ..enums import MatchOutcomeEnum
from ..extensions import db
from ..models import Match, MatchRecord, Member
from ..models.base import utcnow
from ..schemas.match import validate_players, validate_scores
from . import rating_service
from ._queries import involves_player

PLAYER_FIELDS = ("player1_id", "player2_id", "player3_id", "player4_id")

# API 欄位 -> Match 欄位
MATCH_FIELDS = {
    "match_date": "match_date",
    "match_type": "match_type",
    "match_format": "match_format",
    "time_slot": "match_time_slot",
    "court_surface": "court_surface",
    "court_environment": "court_environment",
    "total_points": "total_points",
    "duration_minutes": "duration_minutes",
    "youtube_url": "youtube_url",
    "notes": "notes",
}

_LOAD_OPTIONS = (
    joinedload(MatchRecord.match),
    joinedload(MatchRecord.player1),
    joinedload(MatchRecord.player2),
    joinedload(MatchRecord.player3),
    joinedload(MatchRecord.player4),
)


def list_records(params: dict) -> Page:
    stmt = select(MatchRecord).join(MatchRecord.match).options(*_LOAD_OPTIONS)
    if params.get("start_date"):
        stmt = stmt.where(Match.match_date >= params["start_date"])
    if params.get("end_date"):
        stmt = stmt.where(Match.match_date <= params["end_date"])
    if params.get("match_type"):
        stmt = stmt.where(Match.match_type == params["match_type"])
    if params.get("match_format"):
        stmt = stmt.where(Match.match_format == params["match_format"])
    player_ids = params.get("player_ids") or ([params["player_id"]] if params.get("player_id") else [])
    for player_id in player_ids:
        stmt = stmt.where(involves_player(player_id))
    if params.get("result") and player_ids:
        stmt = stmt.where(_player_result_clause(player_ids[0], won=params["result"] == "win"))

    column = {
        "match_date": Match.match_date,
        "total_games": MatchRecord.a_games + MatchRecord.b_games,
        "id": MatchRecord.id,
    }[params.get("sort_by", "match_date")]
    descending = params.get("sort_order", "desc") == "desc"
    stmt = stmt.order_by(column.desc() if descending else column.asc(), MatchRecord.id.desc())
    return paginate(stmt, params.get("page", 1), params.get("per_page", 20))


def _player_result_clause(player_id: int, won: bool):
    on_side_a = or_(MatchRecord.player1_id == player_id, MatchRecord.player2_id == player_id)
    side_a_won = MatchRecord.side_a_outcome == MatchOutcomeEnum.WIN
    player_won = or_(and_(on_side_a, side_a_won), and_(not_(on_side_a), not_(side_a_won)))
    return player_won if won else not_(player_won)


def get_record(record_id: int) -> MatchRecord:
    return get_or_404(MatchRecord, record_id, "找不到指定的比賽紀錄。")


def create_record(data: dict) -> MatchRecord:
    _ensure_players_exist(data)
    record = MatchRecord(match=Match())
    _apply_match_fields(record.match, data)
    _apply_players(record, data)
    _apply_scores(record, data)
    db.session.add(record)
    _touch_guests(record)
    rating_service.on_match_created(record)
    db.session.commit()
    return record


def update_record(record_id: int, data: dict) -> MatchRecord:
    record = get_record(record_id)
    merged = _merge_for_validation(record, data)
    validate_players(merged)
    if {"games", "a_games", "b_games"} & data.keys():
        validate_scores(merged)
    _ensure_players_exist(data)

    _apply_match_fields(record.match, data)
    _apply_players(record, data)
    if {"games", "a_games", "b_games"} & data.keys():
        _apply_scores(record, merged)
    if "first_serve_side" in data:
        record.first_serve_side = data["first_serve_side"]

    rating_service.recalculate_all()
    db.session.commit()
    return record


def delete_record(record_id: int) -> None:
    record = get_record(record_id)
    # Match 與 MatchRecord 一對一，連同 Match 一起刪除
    db.session.delete(record.match or record)
    rating_service.recalculate_all()
    db.session.commit()


def _apply_match_fields(match: Match, data: dict) -> None:
    for field, column in MATCH_FIELDS.items():
        if field in data:
            setattr(match, column, data[field])


def _apply_players(record: MatchRecord, data: dict) -> None:
    for field in PLAYER_FIELDS:
        if field in data:
            setattr(record, field, data[field])


def _apply_scores(record: MatchRecord, data: dict) -> None:
    if data.get("games") is not None:
        record.game_scores = [(g["a_score"], g["b_score"]) for g in data["games"]]
    if "first_serve_side" in data:
        record.first_serve_side = data["first_serve_side"]

    if scoring.has_detailed_scores(record.game_scores):
        record.a_games, record.b_games = scoring.games_won(record.game_scores)
    else:
        record.a_games, record.b_games = data["a_games"], data["b_games"]
    record.side_a_outcome = MatchOutcomeEnum.WIN if record.a_games > record.b_games else MatchOutcomeEnum.LOSS


def _merge_for_validation(record: MatchRecord, data: dict) -> dict:
    merged = {
        "match_type": record.match.match_type,
        **{field: getattr(record, field) for field in PLAYER_FIELDS},
        "a_games": record.a_games,
        "b_games": record.b_games,
        "games": [{"a_score": a, "b_score": b} for a, b in record.game_scores],
    }
    if "games" in data and ("a_games" not in data or "b_games" not in data):
        # 有新的每局比分時，總局數以比分為準
        merged["a_games"] = merged["b_games"] = None
    elif "games" not in data and ({"a_games", "b_games"} & data.keys()):
        # 只改總局數時，清掉舊的每局比分
        merged["games"] = []
    merged.update(data)
    return merged


def _ensure_players_exist(data: dict) -> None:
    ids = {data[field] for field in PLAYER_FIELDS if data.get(field)}
    if not ids:
        return
    found = set(db.session.scalars(select(Member.id).where(Member.id.in_(ids))))
    missing = ids - found
    if missing:
        raise NotFoundError(f"找不到球員：{', '.join(map(str, sorted(missing)))}。")


def _touch_guests(record: MatchRecord) -> None:
    ids = record.side_a_ids + record.side_b_ids
    for guest in db.session.scalars(select(Member).where(Member.id.in_(ids), Member.is_guest.is_(True))):
        guest.usage_count = (guest.usage_count or 0) + 1
        guest.last_used_at = utcnow()
