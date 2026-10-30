from marshmallow import ValidationError, fields, validate, validates_schema

from ..enums import BloodTypeEnum, GenderEnum, GuestRoleEnum, MatchPositionEnum, UserRoleEnum
from .auth import PASSWORD_MIN_LENGTH
from .common import PHONE_REGEX, BaseSchema, EnumField, InputSchema, OrganizationBriefSchema, UserBriefSchema


def _avatar_url(member) -> str | None:
    from ..services.avatar_service import avatar_url

    return avatar_url(member.avatar_filename)


class PlayerBriefSchema(BaseSchema):
    id = fields.Int()
    name = fields.Str()
    avatar_url = fields.Function(_avatar_url)
    display_name = fields.Str()
    is_guest = fields.Bool()


class MemberSchema(BaseSchema):
    id = fields.Int()
    name = fields.Str()
    avatar_url = fields.Function(_avatar_url)
    display_name = fields.Str()
    short_display_name = fields.Str()
    student_id = fields.Str(allow_none=True)
    gender = EnumField(GenderEnum, allow_none=True)
    blood_type = EnumField(BloodTypeEnum, allow_none=True)
    position = EnumField(MatchPositionEnum, allow_none=True)
    is_guest = fields.Bool()
    is_active = fields.Bool()
    joined_date = fields.Date(allow_none=True)
    leaved_date = fields.Date(allow_none=True)
    has_left = fields.Bool()
    is_a_division = fields.Bool()
    notes = fields.Str(allow_none=True)
    created_at = fields.DateTime(allow_none=True)

    organization_id = fields.Int(allow_none=True)
    organization = fields.Nested(OrganizationBriefSchema, allow_none=True)
    racket_id = fields.Int(allow_none=True)
    user = fields.Nested(UserBriefSchema, allow_none=True)

    # 訪客
    guest_phone = fields.Str(allow_none=True)
    guest_role = EnumField(GuestRoleEnum, allow_none=True)
    guest_role_label = fields.Function(lambda m: m.guest_role.label if m.guest_role else None)
    guest_notes = fields.Str(allow_none=True)
    usage_count = fields.Int(allow_none=True)
    last_used_at = fields.DateTime(allow_none=True)
    created_by_user_id = fields.Int(allow_none=True)

    # 分數（1–10）；還沒打過比賽時為起始分數
    rating = fields.Function(lambda m: round(m.score, 2))


class _MemberFieldsSchema(InputSchema):
    # 帳號 (User)
    email = fields.Email(allow_none=True)
    display_name = fields.Str(allow_none=True, validate=validate.Length(max=50))
    role = EnumField(UserRoleEnum)
    is_active = fields.Bool()

    # 球員 (Member)
    name = fields.Str(validate=validate.Length(min=1, max=80))
    student_id = fields.Str(allow_none=True, validate=validate.Length(max=20))
    gender = EnumField(GenderEnum, allow_none=True)
    blood_type = EnumField(BloodTypeEnum, allow_none=True)
    position = EnumField(MatchPositionEnum, allow_none=True)
    organization_id = fields.Int(allow_none=True)
    racket_id = fields.Int(allow_none=True)
    joined_date = fields.Date(allow_none=True)
    leaved_date = fields.Date(allow_none=True)
    is_a_division = fields.Bool()
    notes = fields.Str(allow_none=True)

    @validates_schema
    def validate_dates(self, data, **kwargs):
        joined, leaved = data.get("joined_date"), data.get("leaved_date")
        if joined and leaved and leaved <= joined:
            raise ValidationError("離隊日期必須晚於入隊日期。", field_name="leaved_date")


class MemberCreateSchema(_MemberFieldsSchema):
    username = fields.Str(required=True, validate=validate.Regexp(PHONE_REGEX, error="手機號碼格式無效。"))
    password = fields.Str(allow_none=True, validate=validate.Length(min=PASSWORD_MIN_LENGTH))
    name = fields.Str(required=True, validate=validate.Length(min=1, max=80))
    role = EnumField(UserRoleEnum, load_default=UserRoleEnum.MEMBER)


class MemberUpdateSchema(_MemberFieldsSchema):
    """帳號（username）不能透過編輯成員修改。"""


class MemberQuerySchema(InputSchema):
    q = fields.Str()
    include_guests = fields.Bool(load_default=False)
    include_inactive = fields.Bool(load_default=False)
    organization_id = fields.Int()
    sort_by = fields.Str(load_default="name", validate=validate.OneOf(["name", "rating", "joined_date", "created_at"]))
    sort_order = fields.Str(load_default="asc", validate=validate.OneOf(["asc", "desc"]))
    limit = fields.Int(validate=validate.Range(min=1, max=500))


class GuestInputSchema(InputSchema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=80))
    phone = fields.Str(
        allow_none=True, validate=validate.Regexp(r"^[0-9\-+\s()]{0,20}$", error="請輸入有效的電話號碼。")
    )
    guest_role = EnumField(GuestRoleEnum, load_default=GuestRoleEnum.NEUTRAL)
    organization_id = fields.Int(allow_none=True)
    notes = fields.Str(allow_none=True, validate=validate.Length(max=200))


class GuestQuerySchema(InputSchema):
    q = fields.Str()
    guest_role = EnumField(GuestRoleEnum)
    organization_id = fields.Int()
    limit = fields.Int(load_default=10, validate=validate.Range(min=1, max=50))
