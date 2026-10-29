from enum import StrEnum


class BaseEnum(StrEnum):
    @classmethod
    def values(cls) -> list[str]:
        return [member.value for member in cls]
