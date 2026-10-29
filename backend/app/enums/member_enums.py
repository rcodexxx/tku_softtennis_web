from .base import BaseEnum


class GuestRoleEnum(BaseEnum):
    """訪客在比賽中的身份"""

    TEAMMATE = "teammate"
    OPPONENT = "opponent"
    NEUTRAL = "neutral"

    @property
    def label(self) -> str:
        return _GUEST_ROLE_LABELS[self]


_GUEST_ROLE_LABELS = {
    GuestRoleEnum.TEAMMATE: "隊友",
    GuestRoleEnum.OPPONENT: "對手",
    GuestRoleEnum.NEUTRAL: "訪客",
}
