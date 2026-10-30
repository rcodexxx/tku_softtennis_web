from marshmallow import fields, validate

from ..services.roster_service import ALUMNI, LEFT, TEAM
from .common import BaseSchema, InputSchema
from .member import PlayerBriefSchema


class RosterCandidateSchema(BaseSchema):
    member = fields.Nested(PlayerBriefSchema)
    gender = fields.Str(allow_none=True)
    is_a_division = fields.Bool()
    # team：校隊；alumni：已畢業（校友會）；left：已離隊
    status = fields.Str()
    # 目前賽季的戰績，方便判斷誰還在打球
    total_matches = fields.Int()
    last_match_date = fields.Date(allow_none=True)


class RosterItemSchema(InputSchema):
    member_id = fields.Int(required=True)
    status = fields.Str(required=True, validate=validate.OneOf([TEAM, ALUMNI, LEFT]))


class RosterUpdateSchema(InputSchema):
    roster = fields.List(fields.Nested(RosterItemSchema), required=True, validate=validate.Length(min=1))
