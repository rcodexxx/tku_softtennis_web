from datetime import date

from app.domain.identity import academic_year, identity_label
from app.enums import MemberIdentityEnum, StudyProgramEnum

TODAY = date(2026, 10, 31)


def test_academic_year_starts_in_august():
    assert academic_year(date(2026, 10, 31)) == 115
    assert academic_year(date(2027, 3, 1)) == 115
    assert academic_year(date(2027, 8, 1)) == 116


def test_student_grade_from_enrolment_year():
    student = MemberIdentityEnum.STUDENT
    assert identity_label(student, StudyProgramEnum.BACHELOR, 113, TODAY) == "大三"
    assert identity_label(student, StudyProgramEnum.MASTER, 115, TODAY) == "碩一"
    assert identity_label(student, StudyProgramEnum.BACHELOR, 110, TODAY) == "大六"
    assert identity_label(student, None, None, TODAY) == "在校生"
    assert identity_label(student, StudyProgramEnum.MASTER, None, TODAY) == "碩士"
    assert identity_label(student, StudyProgramEnum.BACHELOR, 116, TODAY) == "在校生"


def test_other_identities():
    assert identity_label(MemberIdentityEnum.EXCHANGE, None, None, TODAY) == "交換生"
    assert identity_label(MemberIdentityEnum.COACH, None, None, TODAY) == "教練"
    assert identity_label(MemberIdentityEnum.ALUMNI, StudyProgramEnum.BACHELOR, 108, TODAY) == "校友"
    assert identity_label(None, None, None, TODAY) is None
    assert identity_label(MemberIdentityEnum.OTHER, None, None, TODAY) is None
