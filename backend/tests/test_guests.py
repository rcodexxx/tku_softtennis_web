from types import SimpleNamespace

from app.enums import UserRoleEnum
from app.models import Member

from .conftest import auth_header, data, error, login, make_user
from .test_matches import create_record


def create_guest(client, headers, **payload):
    return data(client.post("/api/guests", headers=headers, json={"name": "王小明", **payload}), 201)


def test_create_guest(client, admin_headers):
    guest = create_guest(client, admin_headers, phone="0987654321", guest_role="opponent")
    assert guest["is_guest"] is True
    assert guest["guest_role"] == "opponent"
    assert guest["guest_role_label"] == "對手"
    assert guest["display_name"] == "王小明 (對手-4321)"


def test_create_guest_defaults_to_neutral_role(client, admin_headers):
    assert create_guest(client, admin_headers)["guest_role"] == "neutral"


def test_create_guest_duplicate_name_for_same_creator(client, admin_headers):
    first = create_guest(client, admin_headers)
    err = error(client.post("/api/guests", headers=admin_headers, json={"name": "王小明"}), 409)
    assert err["details"]["existing_guest_id"] == first["id"]


def test_regular_member_cannot_create_guest(client, member_headers):
    error(client.post("/api/guests", headers=member_headers, json={"name": "王小明"}), 403)


def test_search_my_guests(client, admin_headers, coach_headers):
    create_guest(client, admin_headers)
    create_guest(client, admin_headers, name="李大華")
    create_guest(client, coach_headers, name="王小明的朋友")
    guests = data(client.get("/api/guests", headers=admin_headers, query_string={"q": "小明"}))
    assert [g["name"] for g in guests] == ["王小明"]


def test_only_creator_or_admin_can_modify_guest(client, db, coach_headers, admin_headers):
    guest_id = create_guest(client, coach_headers)["id"]
    make_user("0950000001", "other-password", role=UserRoleEnum.CADRE)
    other = auth_header(login(client, "0950000001", "other-password")["access_token"])

    error(client.put(f"/api/guests/{guest_id}", headers=other, json={"name": "改名"}), 403)
    error(client.delete(f"/api/guests/{guest_id}", headers=other), 403)

    assert (
        data(client.put(f"/api/guests/{guest_id}", headers=coach_headers, json={"notes": "備註"}))["guest_notes"]
        == "備註"
    )
    renamed = data(client.put(f"/api/guests/{guest_id}", headers=admin_headers, json={"name": "王小明二"}))
    assert renamed["name"] == "王小明二"
    assert renamed["guest_role"] == "neutral"  # 部分更新不會套用預設值

    data(client.delete(f"/api/guests/{guest_id}", headers=coach_headers))
    assert db.session.get(Member, guest_id) is None


def test_cannot_delete_guest_with_match_history(client, admin_headers, players):
    guest = create_guest(client, admin_headers)
    p1, p2, p3, _ = players
    create_record(client, admin_headers, (p1, p2, p3, SimpleNamespace(id=guest["id"])))
    error(client.delete(f"/api/guests/{guest['id']}", headers=admin_headers), 409)


def test_match_participation_updates_guest_usage(client, db, admin_headers, players):
    guest = create_guest(client, admin_headers)
    p1, p2, p3, _ = players
    create_record(client, admin_headers, (p1, p2, p3, SimpleNamespace(id=guest["id"])))
    stored = db.session.get(Member, guest["id"])
    assert stored.usage_count == 1
    assert stored.last_used_at is not None


def test_guest_role_options(client):
    options = data(client.get("/api/guests/role-options"))
    assert {o["value"]: o["label"] for o in options} == {"teammate": "隊友", "opponent": "對手", "neutral": "訪客"}
