from marshmallow import fields, validate

from ..services.season_service import ALUMNI, LEFT, TEAM
from .common import BaseSchema, InputSchema
from .member import PlayerBriefSchema


class SeasonSchema(BaseSchema):
    id = fields.Int()
    name = fields.Str()
    start_date = fields.Date()
    end_date = fields.Date(allow_none=True)
    is_current = fields.Bool()
    match_count = fields.Int()


class RosterCandidateSchema(BaseSchema):
    member = fields.Nested(PlayerBriefSchema)
    gender = fields.Str(allow_none=True)
    status = fields.Str()
    # 目前賽季的戰績，方便判斷誰還在打球
    total_matches = fields.Int()
    last_match_date = fields.Date(allow_none=True)


class RosterItemSchema(InputSchema):
    member_id = fields.Int(required=True)
    status = fields.Str(required=True, validate=validate.OneOf([TEAM, ALUMNI, LEFT]))


class SeasonInputSchema(InputSchema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    start_date = fields.Date(required=True)
    roster = fields.List(fields.Nested(RosterItemSchema), load_default=list)
