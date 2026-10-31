"""名單整理：校隊、畢業（轉到校友會）、離隊。

- 畢業：轉到校友會，不算離隊。
- 離隊：保留原本的組織，只記下離隊日期；校隊排行榜不列出，但還在綜合榜、也能被選來記錄比賽。
"""

from datetime import date

from flask import current_app
from sqlalchemy import select

from ..core.errors import ValidationError
from ..extensions import db
from ..models import Member

TEAM, ALUMNI, LEFT = "team", "alumni", "left"


def organization_ids() -> tuple[int, int]:
    return current_app.config["TEAM_ORGANIZATION_ID"], current_app.config["ALUMNI_ORGANIZATION_ID"]


def status_of(member: Member) -> str:
    if member.has_left:
        return LEFT
    return ALUMNI if member.organization_id == organization_ids()[1] else TEAM


def category_of(member: Member) -> str:
    """球員名單的分類：team 校隊、alumni 校友會、left 已離隊、guest 對手（訪客）、other 其他。"""
    team, alumni = organization_ids()
    if member.is_guest:
        return "guest"
    if member.organization_id in (team, alumni):
        return LEFT if member.has_left else (TEAM if member.organization_id == team else ALUMNI)
    return "other"


def candidates() -> list[Member]:
    """要整理的名單：校隊與校友會的正式隊員（包含已離隊的）。"""
    team, alumni = organization_ids()
    return list(
        db.session.scalars(
            select(Member)
            .where(Member.is_guest.is_(False), Member.organization_id.in_([team, alumni]), Member.active_clause())
            .order_by(Member.organization_id, Member.leaved_date.is_not(None), Member.name)
        )
    )


def apply(items: list[dict], on_date: date | None = None) -> list[Member]:
    """套用名單調整（不 commit）。items：[{member_id, status}]，離隊日期預設為今天。"""
    team, alumni = organization_ids()
    members = {
        m.id: m for m in db.session.scalars(select(Member).where(Member.id.in_([i["member_id"] for i in items])))
    }
    changed = []
    for item in items:
        member = members.get(item["member_id"])
        if member is None or member.is_guest:
            raise ValidationError(f"找不到隊員 #{item['member_id']}。")
        if item["status"] == LEFT:
            member.leaved_date = member.leaved_date or on_date or date.today()
        else:
            member.organization_id = team if item["status"] == TEAM else alumni
            member.leaved_date = None
        changed.append(member)
    return changed


def update(items: list[dict]) -> list[Member]:
    changed = apply(items)
    db.session.commit()
    return changed
