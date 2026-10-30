from flask import Blueprint

from ..core.auth import staff_required
from ..core.requests import load_json
from ..core.responses import created, ok
from ..schemas.event import EventInputSchema, EventSchema
from ..services import event_service

bp = Blueprint("events", __name__, url_prefix="/events")

event_schema = EventSchema()


@bp.get("")
def list_events():
    return ok(event_schema.dump(event_service.list_events(), many=True))


@bp.get("/<int:event_id>")
def get_event(event_id: int):
    return ok(event_schema.dump(event_service.get_event(event_id)))


@bp.post("")
@staff_required
def create_event():
    event = event_service.create_event(load_json(EventInputSchema()))
    return created(event_schema.dump(event), message="賽事已建立。")


@bp.put("/<int:event_id>")
@staff_required
def update_event(event_id: int):
    event = event_service.update_event(event_id, load_json(EventInputSchema(), partial=True))
    return ok(event_schema.dump(event), message="賽事已更新。")


@bp.delete("/<int:event_id>")
@staff_required
def delete_event(event_id: int):
    event_service.delete_event(event_id)
    return ok(message="賽事已刪除。")
