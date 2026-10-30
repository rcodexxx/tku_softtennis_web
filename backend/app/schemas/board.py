from marshmallow import fields, validate

from .common import BaseSchema, InputSchema
from .member import PlayerBriefSchema


class BoardSchema(BaseSchema):
    id = fields.Int()
    name = fields.Str()
    members = fields.Nested(PlayerBriefSchema, many=True)


class BoardInputSchema(InputSchema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    member_ids = fields.List(fields.Int(validate=validate.Range(min=1)), load_default=list)
