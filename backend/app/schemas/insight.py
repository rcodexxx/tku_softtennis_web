from marshmallow import fields

from .common import BaseSchema
from .member import MemberSchema, PlayerBriefSchema


class HeadToHeadSchema(BaseSchema):
    player = fields.Nested(PlayerBriefSchema)
    matches = fields.Int()
    wins = fields.Int()
    losses = fields.Int()
    win_rate = fields.Float()
    last_date = fields.Date(allow_none=True)
    chemistry = fields.Function(lambda e: round(e.chemistry, 2) if e.chemistry is not None else None)


class TrendPointSchema(BaseSchema):
    date = fields.Date()
    rating = fields.Float()
    won = fields.Bool()
    record_id = fields.Int()


class SeasonHistorySchema(BaseSchema):
    season_id = fields.Int()
    season_name = fields.Str()
    is_current = fields.Bool()
    rating = fields.Float()
    matches = fields.Int()
    rank = fields.Int(allow_none=True)
    ranked_count = fields.Int()


class InsightsSchema(BaseSchema):
    member = fields.Nested(MemberSchema)
    season_name = fields.Function(lambda i: i.season.name if i.season else None)
    rating = fields.Function(lambda i: round(i.rating, 2))
    wins = fields.Int()
    losses = fields.Int()
    trend = fields.Nested(TrendPointSchema, many=True)
    partners = fields.Nested(HeadToHeadSchema, many=True)
    opponents = fields.Nested(HeadToHeadSchema, many=True)
    seasons = fields.Nested(SeasonHistorySchema, many=True)
