from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..core.db import get_or_404
from ..core.errors import ConflictError
from ..extensions import db
from ..models import Event, Match
from . import rating_service


def list_events() -> list[Event]:
    stmt = select(Event).options(selectinload(Event.matches).selectinload(Match.results))
    return list(db.session.scalars(stmt.order_by(Event.start_date.desc().nulls_last(), Event.id.desc())))


def get_event(event_id: int) -> Event:
    return get_or_404(Event, event_id, "找不到指定的賽事。")


def create_event(data: dict) -> Event:
    event = Event(**data)
    db.session.add(event)
    db.session.commit()
    return event


def update_event(event_id: int, data: dict) -> Event:
    event = get_event(event_id)
    toggled = "counts_toward_rating" in data and data["counts_toward_rating"] != event.counts_toward_rating
    for field, value in data.items():
        setattr(event, field, value)
    if toggled:
        rating_service.recalculate_all()
    db.session.commit()
    return event


def delete_event(event_id: int) -> None:
    event = get_event(event_id)
    if event.matches:
        raise ConflictError(f"賽事「{event.name}」還有 {len(event.matches)} 場比賽，請先刪除或改到其他分類。")
    db.session.delete(event)
    db.session.commit()
