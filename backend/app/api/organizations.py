from flask import Blueprint

from ..core.auth import admin_required
from ..core.requests import load_json
from ..core.responses import created, ok
from ..schemas.organization import OrganizationInputSchema, OrganizationSchema
from ..services import organization_service

bp = Blueprint("organizations", __name__, url_prefix="/organizations")

org_schema = OrganizationSchema()


@bp.get("")
def list_organizations():
    return ok(org_schema.dump(organization_service.list_organizations(), many=True))


@bp.get("/<int:org_id>")
def get_organization(org_id: int):
    return ok(org_schema.dump(organization_service.get_organization(org_id)))


@bp.post("")
@admin_required
def create_organization():
    org = organization_service.create_organization(load_json(OrganizationInputSchema()))
    return created(org_schema.dump(org), message="組織已建立。")


@bp.put("/<int:org_id>")
@admin_required
def update_organization(org_id: int):
    org = organization_service.update_organization(org_id, load_json(OrganizationInputSchema(), partial=True))
    return ok(org_schema.dump(org), message="組織已更新。")


@bp.delete("/<int:org_id>")
@admin_required
def delete_organization(org_id: int):
    organization_service.delete_organization(org_id)
    return ok(message="組織已刪除。")
