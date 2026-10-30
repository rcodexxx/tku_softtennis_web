from marshmallow import fields, validate

from .common import BaseSchema, InputSchema
from .roster import RosterItemSchema


class SeasonSchema(BaseSchema):
    id = fields.Int()
    name = fields.Str()
    start_date = fields.Date()
    end_date = fields.Date(allow_none=True)
    is_current = fields.Bool()
    match_count = fields.Int()


class SeasonInputSchema(InputSchema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    start_date = fields.Date(required=True)
    roster = fields.List(fields.Nested(RosterItemSchema), load_default=list)
