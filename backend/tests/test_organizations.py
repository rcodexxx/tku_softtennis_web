from .conftest import data, error, make_org, make_user


def test_list_organizations_with_member_count(client, app):
    org = make_org("淡江大學", "TKU")
    make_user("0930000001", organization_id=org.id)
    orgs = data(client.get("/api/organizations"))
    assert len(orgs) == 1
    assert orgs[0]["name"] == "淡江大學"
    assert orgs[0]["members_count"] == 1


def test_get_organization_not_found(client):
    assert error(client.get("/api/organizations/999"), 404)["code"] == "not_found"


def test_create_update_delete_organization(client, admin_headers):
    org = data(client.post("/api/organizations", headers=admin_headers, json={"name": "A 隊", "short_name": "A"}), 201)

    updated = data(client.put(f"/api/organizations/{org['id']}", headers=admin_headers, json={"description": "說明"}))
    assert updated["description"] == "說明"
    assert updated["name"] == "A 隊"

    assert data(client.delete(f"/api/organizations/{org['id']}", headers=admin_headers)) is None
    error(client.get(f"/api/organizations/{org['id']}"), 404)


def test_create_duplicate_organization(client, admin_headers):
    client.post("/api/organizations", headers=admin_headers, json={"name": "A 隊"})
    error(client.post("/api/organizations", headers=admin_headers, json={"name": "A 隊"}), 409)


def test_update_to_existing_short_name(client, admin_headers):
    make_org("A 隊", "A")
    b = make_org("B 隊", "B")
    error(client.put(f"/api/organizations/{b.id}", headers=admin_headers, json={"short_name": "A"}), 409)


def test_delete_organization_in_use(client, admin_headers):
    org = make_org("B 隊")
    make_user("0930000002", organization_id=org.id)
    error(client.delete(f"/api/organizations/{org.id}", headers=admin_headers), 409)


def test_only_admin_manages_organizations(client, coach_headers):
    error(client.post("/api/organizations", headers=coach_headers, json={"name": "A 隊"}), 403)
