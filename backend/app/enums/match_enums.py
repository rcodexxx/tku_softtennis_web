from .base import BaseEnum


class MatchTypeEnum(BaseEnum):
    """比賽類型"""

    SINGLES = "singles"
    DOUBLES = "doubles"
    MIXED_DOUBLES = "mixed_doubles"


class MatchOutcomeEnum(BaseEnum):
    """A 方視角的比賽結果"""

    WIN = "win"
    LOSS = "loss"
    PENDING = "pending"


class MatchFormatEnum(BaseEnum):
    """賽制（幾局制）"""

    GAMES_5 = "games_5"
    GAMES_7 = "games_7"
    GAMES_9 = "games_9"

    @property
    def games_to_win(self) -> int:
        return {"games_5": 3, "games_7": 4, "games_9": 5}[self.value]


class MatchPositionEnum(BaseEnum):
    """擅長位置"""

    FRONT = "front"
    BACK = "back"
    VERSATILE = "versatile"


class MatchCategoryEnum(BaseEnum):
    """比賽分類：隊內、校外友誼、自訂賽事"""

    INTERNAL = "internal"
    FRIENDLY = "friendly"
    EVENT = "event"


class CourtSurfaceEnum(BaseEnum):
    """場地材質"""

    HARD_COURT = "hard_court"
    CLAY_COURT = "clay_court"
    GRASS_COURT = "grass_court"
    SYNTHETIC = "synthetic"
    CARPET = "carpet"


class CourtEnvironmentEnum(BaseEnum):
    """場地環境"""

    INDOOR = "indoor"
    OUTDOOR = "outdoor"


class MatchTimeSlotEnum(BaseEnum):
    """比賽時段"""

    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"


class MatchStartServeEnum(BaseEnum):
    """第一局發球方"""

    SIDE_A = "side_a"
    SIDE_B = "side_b"

    @property
    def other(self) -> "MatchStartServeEnum":
        return MatchStartServeEnum.SIDE_B if self is MatchStartServeEnum.SIDE_A else MatchStartServeEnum.SIDE_A
