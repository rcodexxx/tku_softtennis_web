from marshmallow import ValidationError as SchemaValidationError
from marshmallow import fields, validate, validates_schema

from .common import BaseSchema, InputSchema


class EventBriefSchema(BaseSchema):
    id = fields.Int()
    name = fields.Str()


class EventSchema(BaseSchema):
    id = fields.Int()
    name = fields.Str()
    start_date = fields.Date(allow_none=True)
    end_date = fields.Date(allow_none=True)
    location = fields.Str(allow_none=True)
    notes = fields.Str(allow_none=True)
    counts_toward_rating = fields.Bool()
    match_count = fields.Function(lambda event: sum(len(match.results) for match in event.matches))


class EventInputSchema(InputSchema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    start_date = fields.Date(allow_none=True)
    end_date = fields.Date(allow_none=True)
    location = fields.Str(allow_none=True, validate=validate.Length(max=100))
    notes = fields.Str(allow_none=True, validate=validate.Length(max=500))
    counts_toward_rating = fields.Bool()

    @validates_schema
    def validate_dates(self, data, **kwargs):
        start, end = data.get("start_date"), data.get("end_date")
        if start and end and end < start:
            raise SchemaValidationError("結束日期不能早於開始日期。", field_name="end_date")
