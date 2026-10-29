from .conftest import ADMIN_PASSWORD, ADMIN_USERNAME, auth_header, data, error, login


def test_register_creates_user_and_member_and_returns_tokens(client):
    resp = client.post("/api/auth/register", json={"phone_number": "0912345678"})
    body = data(resp, 201)
    assert body["access_token"] and body["refresh_token"]
    assert body["user"]["username"] == "0912345678"
    assert body["user"]["role"] == "member"
    assert body["user"]["member_id"] is not None
    assert "初始密碼" in resp.get_json()["message"]

    # 初始密碼就是手機號碼
    login(client, "0912345678", "0912345678")


def test_register_rejects_invalid_phone(client):
    err = error(client.post("/api/auth/register", json={"phone_number": "12345"}), 400)
    assert err["code"] == "validation_error"
    assert "phone_number" in err["details"]


def test_register_rejects_non_json_body(client):
    assert error(client.post("/api/auth/register", data="x"), 400)["code"] == "validation_error"


def test_register_rejects_duplicate_phone(client):
    client.post("/api/auth/register", json={"phone_number": "0912345678"})
    assert error(client.post("/api/auth/register", json={"phone_number": "0912345678"}), 409)["code"] == "conflict"


def test_login_success(client, admin):
    assert login(client, ADMIN_USERNAME, ADMIN_PASSWORD)["user"]["role"] == "admin"


def test_login_wrong_password(client, admin):
    resp = client.post("/api/auth/login", json={"username": ADMIN_USERNAME, "password": "nope"})
    assert error(resp, 401)["code"] == "invalid_credentials"


def test_login_inactive_user(client, db, admin):
    admin.is_active = False
    db.session.commit()
    resp = client.post("/api/auth/login", json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD})
    assert error(resp, 401)["code"] == "user_inactive"


def test_refresh_returns_new_access_token(client, admin):
    tokens = login(client, ADMIN_USERNAME, ADMIN_PASSWORD)
    body = data(client.post("/api/auth/refresh", headers=auth_header(tokens["refresh_token"])))
    assert body["access_token"]


def test_refresh_rejects_access_token(client, admin):
    tokens = login(client, ADMIN_USERNAME, ADMIN_PASSWORD)
    resp = client.post("/api/auth/refresh", headers=auth_header(tokens["access_token"]))
    assert resp.status_code == 401


def test_me(client, admin_headers):
    assert data(client.get("/api/auth/me", headers=admin_headers))["username"] == ADMIN_USERNAME


def test_token_of_deactivated_user_is_rejected(client, db, admin, admin_headers):
    admin.is_active = False
    db.session.commit()
    assert error(client.get("/api/auth/me", headers=admin_headers), 401)["code"] == "user_inactive"


def test_change_password(client, admin_headers):
    resp = client.post(
        "/api/auth/change-password",
        headers=admin_headers,
        json={"old_password": ADMIN_PASSWORD, "new_password": "new-password"},
    )
    assert data(resp) is None
    login(client, ADMIN_USERNAME, "new-password")


def test_change_password_wrong_old_password(client, admin_headers):
    resp = client.post(
        "/api/auth/change-password",
        headers=admin_headers,
        json={"old_password": "wrong", "new_password": "new-password"},
    )
    assert error(resp, 401)["code"] == "incorrect_password"


def test_protected_endpoint_requires_token(client):
    assert error(client.post("/api/organizations", json={"name": "x"}), 401)["code"] == "unauthorized"


def test_unknown_route_uses_error_envelope(client):
    assert error(client.get("/api/nope"), 404)["code"] == "not_found"
