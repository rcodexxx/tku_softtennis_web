from marshmallow import fields, validate

from ..services.avatar_service import avatar_url
from .common import PHONE_REGEX, BaseSchema, InputSchema

PASSWORD_MIN_LENGTH = 6


class RegisterSchema(InputSchema):
    phone_number = fields.Str(
        required=True, validate=validate.Regexp(PHONE_REGEX, error="手機號碼格式無效（應為 09 開頭的 10 位數字）。")
    )


class LoginSchema(InputSchema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)


class ChangePasswordSchema(InputSchema):
    old_password = fields.Str(required=True)
    new_password = fields.Str(
        required=True, validate=validate.Length(min=PASSWORD_MIN_LENGTH, error="新密碼長度至少需要 6 位。")
    )


class AuthUserSchema(BaseSchema):
    id = fields.Int()
    username = fields.Str()
    email = fields.Str(allow_none=True)
    display_name = fields.Str(allow_none=True)
    role = fields.Function(lambda user: user.role.value)
    is_active = fields.Bool()
    member_id = fields.Function(lambda user: user.member_profile.id if user.member_profile else None)
    avatar_url = fields.Function(
        lambda user: avatar_url(user.member_profile.avatar_filename) if user.member_profile else None
    )
    created_at = fields.DateTime()


class TokenSchema(BaseSchema):
    access_token = fields.Str()
    refresh_token = fields.Str()
    user = fields.Nested(AuthUserSchema)
