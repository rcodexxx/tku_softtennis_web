from datetime import date

from app.models import Member, User

from .conftest import data, error, make_guest, make_org
from .test_matches import create_record


def test_list_members_excludes_guests_and_inactive_by_default(client, db, players):
    players[0].user.is_active = False
    db.session.commit()
    make_guest("訪客A")
    resp = client.get("/api/members")
    assert {m["name"] for m in data(resp)} == {"乙", "丙", "丁"}
    assert resp.get_json()["meta"]["total"] == 3


def test_list_members_can_include_guests_and_inactive(client, db, players):
    players[0].leaved_date = date(2024, 1, 1)
    db.session.commit()
    make_guest("訪客A")
    members = data(client.get("/api/members", query_string={"include_guests": "true", "include_inactive": "true"}))
    assert {m["name"] for m in members} == {"甲", "乙", "丙", "丁", "訪客A"}


def test_list_members_search(client, players):
    assert [m["name"] for m in data(client.get("/api/members", query_string={"q": "丙"}))] == ["丙"]
    assert [m["name"] for m in data(client.get("/api/members", query_string={"q": "0920000004"}))] == ["丁"]


def test_list_members_sort_and_limit(client, players):
    members = data(client.get("/api/members", query_string={"sort_by": "name", "sort_order": "desc", "limit": 2}))
    assert len(members) == 2


def test_get_member(client, players):
    member = data(client.get(f"/api/members/{players[0].id}"))
    assert member["name"] == "甲"
    assert member["gender"] == "male"
    assert member["user"]["username"] == "0920000001"
    assert member["rating"] == 5.0  # 男生的起始分數


def test_get_member_not_found(client):
    error(client.get("/api/members/999"), 404)


def test_create_member_with_user(client, db, coach_headers):
    org = make_org("C 隊")
    member = data(
        client.post(
            "/api/members",
            headers=coach_headers,
            json={
                "username": "0940000001",
                "name": "新隊員",
                "gender": "female",
                "blood_type": "O",
                "organization_id": org.id,
                "student_id": "",
            },
        ),
        201,
    )
    created = db.session.get(Member, member["id"])
    assert created.user.username == "0940000001"
    assert created.user.check_password("0940000001")
    assert created.user.role.value == "member"
    assert created.blood_type.value == "O"
    assert created.student_id is None
    assert member["organization"]["name"] == "C 隊"


def test_create_member_duplicate_username(client, admin_headers, players):
    resp = client.post("/api/members", headers=admin_headers, json={"username": "0920000001", "name": "重複"})
    error(resp, 409)


def test_create_member_unknown_organization(client, admin_headers):
    resp = client.post(
        "/api/members", headers=admin_headers, json={"username": "0940000002", "name": "X", "organization_id": 99}
    )
    error(resp, 404)


def test_regular_member_cannot_create_member(client, member_headers):
    resp = client.post("/api/members", headers=member_headers, json={"username": "0940000003", "name": "X"})
    assert error(resp, 403)["code"] == "forbidden"


def test_update_member_and_user_fields(client, db, admin_headers, players):
    member = data(
        client.put(
            f"/api/members/{players[0].id}",
            headers=admin_headers,
            json={"name": "甲改", "position": "front", "blood_type": "A", "display_name": "新暱稱", "role": "cadre"},
        )
    )
    assert member["name"] == "甲改"
    assert member["display_name"] == "新暱稱"
    stored = db.session.get(Member, players[0].id)
    assert stored.position.value == "front"
    assert stored.blood_type.value == "A"
    assert stored.user.role.value == "cadre"


def test_only_admin_can_change_roles(client, coach_headers, players):
    resp = client.put(f"/api/members/{players[0].id}", headers=coach_headers, json={"role": "admin"})
    error(resp, 403)
    resp = client.post(
        "/api/members", headers=coach_headers, json={"username": "0940000009", "name": "X", "role": "coach"}
    )
    error(resp, 403)
    # 角色沒變時可以照常更新
    data(client.put(f"/api/members/{players[0].id}", headers=coach_headers, json={"role": "member", "notes": "ok"}))


def test_update_ignores_username(client, db, admin_headers, players):
    data(client.put(f"/api/members/{players[0].id}", headers=admin_headers, json={"username": "admin-name"}))
    assert db.session.get(Member, players[0].id).user.username == "0920000001"


def test_update_member_rejects_leave_before_join(client, admin_headers, players):
    resp = client.put(
        f"/api/members/{players[0].id}",
        headers=admin_headers,
        json={"joined_date": "2025-01-01", "leaved_date": "2024-01-01"},
    )
    assert "leaved_date" in error(resp, 400)["details"]


def test_delete_member_also_deletes_user(client, db, admin_headers, players):
    member_id, user_id = players[0].id, players[0].user_id
    assert data(client.delete(f"/api/members/{member_id}", headers=admin_headers)) is None
    assert db.session.get(Member, member_id) is None
    assert db.session.get(User, user_id) is None


def test_cannot_delete_member_with_match_history(client, admin_headers, players):
    create_record(client, admin_headers, players)
    error(client.delete(f"/api/members/{players[0].id}", headers=admin_headers), 409)


def test_only_admin_deletes_member(client, coach_headers, players):
    error(client.delete(f"/api/members/{players[0].id}", headers=coach_headers), 403)


def test_member_created_at_is_set_per_row(app, players):
    assert all(p.created_at is not None for p in players)


def test_member_stats(client, admin_headers, players):
    create_record(client, admin_headers, players)
    stats = data(client.get(f"/api/members/{players[0].id}/stats"))
    assert (stats["wins"], stats["losses"], stats["total_matches"]) == (1, 0, 1)
    assert stats["last_match_date"] == "2025-03-01"


def test_changing_gender_recalculates_rating(client, db, admin_headers, players):
    create_record(client, admin_headers, players)
    before = db.session.get(Member, players[2].id).rating
    member = data(client.put(f"/api/members/{players[2].id}", headers=admin_headers, json={"gender": "male"}))
    # 起始分數從 4.0 變成 5.0
    assert member["rating"] > before
