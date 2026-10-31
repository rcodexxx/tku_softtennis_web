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


class MemberIdentityEnum(BaseEnum):
    """校內球員的身分（和登入權限無關）"""

    STUDENT = "student"
    EXCHANGE = "exchange"
    COACH = "coach"
    ALUMNI = "alumni"
    OTHER = "other"


class StudyProgramEnum(BaseEnum):
    """在校生的學制"""

    BACHELOR = "bachelor"
    MASTER = "master"
    PHD = "phd"
