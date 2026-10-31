from marshmallow import fields, validate

from ..domain.pairing import MODES
from .common import BaseSchema, InputSchema
from .member import PlayerBriefSchema


class PracticeSessionSchema(BaseSchema):
    id = fields.Int()
    session_date = fields.Date()
    location = fields.Str(allow_none=True)
    notes = fields.Str(allow_none=True)
    attendees = fields.Nested(PlayerBriefSchema, many=True)
    match_count = fields.Function(lambda s: sum(len(match.results) for match in s.matches))


class PracticeSessionInputSchema(InputSchema):
    session_date = fields.Date(required=True)
    location = fields.Str(allow_none=True, validate=validate.Length(max=100))
    notes = fields.Str(allow_none=True, validate=validate.Length(max=500))
    player_ids = fields.List(fields.Int(validate=validate.Range(min=1)), load_default=list)


class NextRoundQuerySchema(InputSchema):
    courts = fields.Int(load_default=2, validate=validate.Range(min=1, max=8))
    mode = fields.Str(load_default="rotate", validate=validate.OneOf(MODES))
    seed = fields.Int(load_default=0)


class CourtSchema(BaseSchema):
    side_a = fields.List(fields.Int())
    side_b = fields.List(fields.Int())


class RoundSchema(BaseSchema):
    courts = fields.Nested(CourtSchema, many=True)
    resting = fields.List(fields.Int())


class DayLineSchema(BaseSchema):
    player = fields.Nested(PlayerBriefSchema)
    wins = fields.Int()
    losses = fields.Int()
    games_for = fields.Int()
    games_against = fields.Int()
    rating_after = fields.Float(allow_none=True)
    rating_change = fields.Float(allow_none=True)


class DayPairSchema(BaseSchema):
    players = fields.List(fields.Nested(PlayerBriefSchema))
    wins = fields.Int()
    losses = fields.Int()


class DaySummarySchema(BaseSchema):
    lines = fields.Nested(DayLineSchema, many=True)
    pairs = fields.Nested(DayPairSchema, many=True)
