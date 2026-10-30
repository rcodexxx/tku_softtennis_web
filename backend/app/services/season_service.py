"""賽季：比賽依日期歸屬賽季，分數、戰績與排行榜都只看同一個賽季的比賽。

賽季從開始日期到下一個賽季開始的前一天為止；還沒有任何賽季時，所有比賽視為同一段。
"""

from datetime import date, timedelta

from flask import current_app
from sqlalchemy import func, select

from ..core.db import get_or_404
from ..core.errors import ConflictError, ValidationError
from ..extensions import db
from ..models import MatchRecord, Member, Season, SeasonRoster
from . import rating_service

TEAM, ALUMNI, LEFT = "team", "alumni", "left"


def list_seasons() -> list[Season]:
    return list(db.session.scalars(select(Season).order_by(Season.start_date.desc())))


def current_season() -> Season | None:
    return db.session.scalar(select(Season).order_by(Season.start_date.desc()).limit(1))


def resolve(season_id: int | None) -> Season | None:
    """指定的賽季；沒指定時為目前賽季。"""
    return get_or_404(Season, season_id, "找不到指定的賽季。") if season_id else current_season()


def is_current(season: Season | None) -> bool:
    current = current_season()
    return season is None or current is None or season.id == current.id


def period(season: Season | None) -> rating_service.Period:
    if season is None:
        return rating_service.Period()
    next_start = db.session.scalar(select(func.min(Season.start_date)).where(Season.start_date > season.start_date))
    return rating_service.Period(season.start_date, next_start)


def count_matches(span: rating_service.Period) -> int:
    return db.session.scalar(span.filter(select(func.count(MatchRecord.id)).join(MatchRecord.match)))


def describe(season: Season | None) -> dict | None:
    if season is None:
        return None
    span = period(season)
    return {
        "id": season.id,
        "name": season.name,
        "start_date": season.start_date,
        # 下個賽季開始的前一天；目前賽季沒有結束日期
        "end_date": span.end - timedelta(days=1) if span.end else None,
        "is_current": span.end is None,
        "match_count": count_matches(span),
    }


def summaries() -> list[dict]:
    return [describe(season) for season in list_seasons()]


def roster_candidates() -> list[tuple[Member, str]]:
    """開新賽季時要整理的名單：目前在校隊或校友會的正式隊員。"""
    team, alumni = _organization_ids()
    members = db.session.scalars(
        select(Member)
        .where(Member.is_guest.is_(False), Member.organization_id.in_([team, alumni]), Member.active_clause())
        .order_by(Member.organization_id, Member.name)
    )
    return [(m, TEAM if m.organization_id == team else ALUMNI) for m in members]


def start_season(data: dict) -> Season:
    """開新賽季：封存上個賽季的名單、套用名單調整，所有人的分數從起始分數重新計算。"""
    previous = current_season()
    start = data["start_date"]
    if start > date.today():
        raise ValidationError("開始日期不能晚於今天。", details={"start_date": ["開始日期不能晚於今天。"]})
    if previous and start <= previous.start_date:
        message = f"開始日期必須晚於「{previous.name}」的開始日期（{previous.start_date.isoformat()}）。"
        raise ValidationError(message, details={"start_date": [message]})
    if db.session.scalar(select(Season.id).where(Season.name == data["name"])):
        raise ConflictError(f"賽季「{data['name']}」已存在。")

    members = list(db.session.scalars(select(Member)))
    if previous:
        previous.rosters = [
            SeasonRoster(member_id=m.id, organization_id=m.organization_id) for m in members if m.organization_id
        ]

    by_id = {m.id: m for m in members}
    team, alumni = _organization_ids()
    for item in data["roster"]:
        member = by_id.get(item["member_id"])
        if member is None or member.is_guest:
            raise ValidationError(f"找不到隊員 #{item['member_id']}。")
        if item["status"] == LEFT:
            member.leaved_date = member.leaved_date or start
        else:
            member.organization_id = team if item["status"] == TEAM else alumni

    season = Season(name=data["name"], start_date=start)
    db.session.add(season)
    db.session.flush()
    rating_service.recalculate_all()
    db.session.commit()
    return season


def _organization_ids() -> tuple[int, int]:
    return current_app.config["TEAM_ORGANIZATION_ID"], current_app.config["ALUMNI_ORGANIZATION_ID"]
