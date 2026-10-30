from marshmallow import fields, validate

from ..enums import GenderEnum
from .common import EnumField, InputSchema

SORT_FIELDS = ["score", "win_rate", "total_matches", "wins", "recent_activity", "join_date"]


class SeasonQuerySchema(InputSchema):
    # 沒指定時為目前賽季
    season_id = fields.Int()


class LeaderboardQuerySchema(SeasonQuerySchema):
    include_guests = fields.Bool(load_default=True)
    include_inactive = fields.Bool(load_default=False)
    organization_id = fields.Int()
    # team：校隊；combined：校隊 + 校友會；all：不限
    scope = fields.Str(load_default="all", validate=validate.OneOf(["all", "team", "combined"]))
    gender = EnumField(GenderEnum)
    min_matches = fields.Int(load_default=0, validate=validate.Range(min=0))
    min_win_rate = fields.Float(validate=validate.Range(min=0, max=100))
    active_since = fields.Date()
    joined_after = fields.Date()
    sort_by = fields.Str(load_default="score", validate=validate.OneOf(SORT_FIELDS))
    sort_order = fields.Str(load_default="desc", validate=validate.OneOf(["asc", "desc"]))
    page = fields.Int(load_default=1, validate=validate.Range(min=1))
    per_page = fields.Int(load_default=50, validate=validate.Range(min=1, max=500))
