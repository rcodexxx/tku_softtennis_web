from flask import Blueprint

from ..core.auth import staff_required
from ..core.requests import load_args, load_json
from ..core.responses import created, ok
from ..schemas.practice import (
    DaySummarySchema,
    NextRoundQuerySchema,
    PracticeSessionInputSchema,
    PracticeSessionSchema,
    RoundSchema,
)
from ..services import practice_service

bp = Blueprint("practice", __name__, url_prefix="/practice-sessions")

session_schema = PracticeSessionSchema()


@bp.get("")
def list_sessions():
    return ok(session_schema.dump(practice_service.list_sessions(), many=True))


@bp.get("/<int:session_id>")
def get_session(session_id: int):
    session = practice_service.get_session(session_id)
    return ok(
        {
            **session_schema.dump(session),
            "summary": DaySummarySchema().dump(practice_service.summary(session)),
        }
    )


@bp.post("")
@staff_required
def create_session():
    session = practice_service.create_session(load_json(PracticeSessionInputSchema()))
    return created(session_schema.dump(session), message="練習日已建立。")


@bp.put("/<int:session_id>")
@staff_required
def update_session(session_id: int):
    session = practice_service.update_session(session_id, load_json(PracticeSessionInputSchema(), partial=True))
    return ok(session_schema.dump(session))


@bp.delete("/<int:session_id>")
@staff_required
def delete_session(session_id: int):
    practice_service.delete_session(session_id)
    return ok(message="練習日已刪除。")


@bp.get("/<int:session_id>/next-round")
@staff_required
def next_round(session_id: int):
    params = load_args(NextRoundQuerySchema())
    round_ = practice_service.next_round(
        practice_service.get_session(session_id), params["courts"], params["mode"], params["seed"]
    )
    return ok(RoundSchema().dump(round_))
