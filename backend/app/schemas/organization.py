from marshmallow import fields, validate

from .common import BaseSchema, InputSchema


def _kind(org) -> str | None:
    from ..services.roster_service import organization_ids

    team, alumni = organization_ids()
    return {team: "team", alumni: "alumni"}.get(org.id)


class OrganizationSchema(BaseSchema):
    id = fields.Int()
    name = fields.Str()
    short_name = fields.Str(allow_none=True)
    description = fields.Str(allow_none=True)
    contact_person = fields.Str(allow_none=True)
    contact_email = fields.Str(allow_none=True)
    contact_phone = fields.Str(allow_none=True)
    members_count = fields.Function(lambda org: len(org.members))
    # team：校隊；alumni：校友會；其他組織為 null
    kind = fields.Function(_kind)


class OrganizationInputSchema(InputSchema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    short_name = fields.Str(allow_none=True, validate=validate.Length(max=30))
    description = fields.Str(allow_none=True)
    contact_person = fields.Str(allow_none=True, validate=validate.Length(max=50))
    contact_email = fields.Email(allow_none=True)
    contact_phone = fields.Str(allow_none=True, validate=validate.Length(max=30))
