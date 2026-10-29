from sqlalchemy import select

from ..core.errors import ConflictError, NotFoundError
from ..core.pagination import Page
from ..extensions import db
from ..models import MatchRecord, Organization, User
from . import match_service

USER_FIELDS = ("email", "display_name")
MEMBER_FIELDS = ("name", "student_id", "gender", "position", "organization_id")


def update_profile(user: User, data: dict) -> User:
    if data.get("email") and db.session.scalar(select(User.id).where(User.email == data["email"], User.id != user.id)):
        raise ConflictError(f"電子郵件 {data['email']} 已被其他帳號使用。")
    if data.get("organization_id") and db.session.get(Organization, data["organization_id"]) is None:
        raise NotFoundError("指定的組織不存在。")

    for field in USER_FIELDS:
        if field in data:
            setattr(user, field, data[field])
    if user.member_profile:
        for field in MEMBER_FIELDS:
            if field in data:
                setattr(user.member_profile, field, data[field])
    db.session.commit()
    return user


def my_matches(user: User, page: int, per_page: int) -> Page:
    if user.member_profile is None:
        raise NotFoundError("此帳號沒有對應的球員資料。")
    return match_service.list_records(
        {"player_id": user.member_profile.id, "page": page, "per_page": per_page, "sort_by": "match_date"}
    )


def perspective(record: MatchRecord, member_id: int) -> dict | None:
    """從某位球員的角度描述比賽結果。"""
    if member_id in record.side_a_ids:
        side, my_games, opponent_games = "A", record.a_games, record.b_games
        won, opponents = record.side_a_won, [record.player3, record.player4]
    elif member_id in record.side_b_ids:
        side, my_games, opponent_games = "B", record.b_games, record.a_games
        won, opponents = not record.side_a_won, [record.player1, record.player2]
    else:
        return None
    return {
        "side": side,
        "is_winner": won,
        "my_games": my_games,
        "opponent_games": opponent_games,
        "opponent_names": [p.display_name for p in opponents if p],
    }
