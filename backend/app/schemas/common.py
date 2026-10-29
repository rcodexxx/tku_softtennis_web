from marshmallow import EXCLUDE, Schema, fields, pre_load, validate

PHONE_REGEX = r"^09\d{8}$"


def EnumField(enum_cls, **kwargs):  # noqa: N802
    return fields.Enum(enum_cls, by_value=True, **kwargs)


class IntList(fields.Field):
    """查詢參數用的逗號分隔整數清單，例如 player_ids=3,8。"""

    def _deserialize(self, value, attr, data, **kwargs):
        try:
            items = [int(part) for part in str(value).split(",") if part.strip()]
        except ValueError as error:
            raise self.make_error("invalid") from error
        if any(item < 1 for item in items):
            raise self.make_error("invalid")
        return items

    default_error_messages = {"invalid": "必須是以逗號分隔的正整數。"}


class BaseSchema(Schema):
    class Meta:
        unknown = EXCLUDE


class InputSchema(BaseSchema):
    """請求用 schema：空字串一律視為 None。"""

    @pre_load
    def blank_to_none(self, data, **kwargs):
        return {key: (None if isinstance(value, str) and not value.strip() else value) for key, value in data.items()}


class PageQuerySchema(InputSchema):
    page = fields.Int(load_default=1, validate=validate.Range(min=1))
    per_page = fields.Int(load_default=20, validate=validate.Range(min=1, max=200))
    sort_order = fields.Str(load_default="desc", validate=validate.OneOf(["asc", "desc"]))


class OrganizationBriefSchema(BaseSchema):
    id = fields.Int()
    name = fields.Str()
    short_name = fields.Str(allow_none=True)


class UserBriefSchema(BaseSchema):
    id = fields.Int()
    username = fields.Str()
    display_name = fields.Str(allow_none=True)
    role = fields.Function(lambda user: user.role.value)
    is_active = fields.Bool()
