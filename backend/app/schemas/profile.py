from marshmallow import fields, validate

from ..enums import GenderEnum, MatchPositionEnum
from .auth import AuthUserSchema
from .common import EnumField, InputSchema
from .member import MemberSchema


class ProfileSchema(AuthUserSchema):
    member = fields.Nested(MemberSchema, attribute="member_profile", allow_none=True)


class ProfileUpdateSchema(InputSchema):
    email = fields.Email(allow_none=True)
    display_name = fields.Str(allow_none=True, validate=validate.Length(max=50))
    name = fields.Str(validate=validate.Length(min=1, max=80))
    student_id = fields.Str(allow_none=True, validate=validate.Regexp(r"^\d{7,9}$", error="學號必須是 7 到 9 位數字。"))
    gender = EnumField(GenderEnum, allow_none=True)
    position = EnumField(MatchPositionEnum, allow_none=True)
    organization_id = fields.Int(allow_none=True)
