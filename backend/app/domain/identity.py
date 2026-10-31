"""球員身分的顯示文字，例如「大三」「碩一」「交換生」「教練」。純函式，不碰資料庫。"""

from datetime import date

from ..enums import MemberIdentityEnum, StudyProgramEnum

PROGRAM_PREFIX = {StudyProgramEnum.BACHELOR: "大", StudyProgramEnum.MASTER: "碩", StudyProgramEnum.PHD: "博"}
# 知道學制但不知道入學年度時（例如剛升碩士、學號還沒更新）
PROGRAM_LABELS = {StudyProgramEnum.BACHELOR: "大學部", StudyProgramEnum.MASTER: "碩士", StudyProgramEnum.PHD: "博士"}
NUMERALS = "一二三四五六七八九十"
IDENTITY_LABELS = {
    MemberIdentityEnum.EXCHANGE: "交換生",
    MemberIdentityEnum.COACH: "教練",
    MemberIdentityEnum.ALUMNI: "校友",
}


def academic_year(today: date) -> int:
    """民國學年度：8 月開學，2026-10 與 2027-03 都是 115 學年度。"""
    return (today.year if today.month >= 8 else today.year - 1) - 1911


def grade(enrolled_year: int, today: date) -> int:
    """入學學年度算出現在是幾年級（入學那一年是一年級）。"""
    return academic_year(today) - enrolled_year + 1


def identity_label(
    identity: MemberIdentityEnum | None,
    program: StudyProgramEnum | None,
    enrolled_year: int | None,
    today: date | None = None,
) -> str | None:
    if identity in IDENTITY_LABELS:
        return IDENTITY_LABELS[identity]
    if identity != MemberIdentityEnum.STUDENT:
        return None
    if program is None:
        return "在校生"
    if enrolled_year is None:
        return PROGRAM_LABELS[program]
    year = grade(enrolled_year, today or date.today())
    if not 1 <= year <= len(NUMERALS):
        return "在校生"
    return f"{PROGRAM_PREFIX[program]}{NUMERALS[year - 1]}"
