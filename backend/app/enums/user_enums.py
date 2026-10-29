from .base import BaseEnum


class UserRoleEnum(BaseEnum):
    """使用者角色"""

    ADMIN = "admin"
    MEMBER = "member"
    COACH = "coach"
    CADRE = "cadre"
