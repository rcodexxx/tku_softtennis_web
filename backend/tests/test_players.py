from datetime import date

from app.enums import GenderEnum
from app.models import MatchRecord, Member

from .conftest import data, error, make_guest, make_org, make_user
from .test_matches import create_record


def test_create_player_without_account(client, db, admin_headers, orgs):
    team, _ = orgs
    player = data(
        client.post(
            "/api/members", headers=admin_headers, json={"name": "新生", "gender": "male", "organization_id": team.id}
        ),
        201,
    )
    assert (player["user"], player["is_active"], player["rating"]) == (None, True, 5.0)
    # 沒帳號也會出現在名單上、可以被選來記錄比賽
    assert "新生" in {m["name"] for m in data(client.get("/api/members"))}


def test_roster_order_puts_our_school_first(client, orgs):
    team, alumni = orgs
    other = make_org("台灣大學")
    make_guest("外校甲", organization_id=other.id)
    make_user("0931000001", name="乙隊員", organization_id=team.id)
    make_user("0931000002", name="甲校友", organization_id=alumni.id)
    make_user("0931000003", name="丙離隊", organization_id=team.id, leaved_date=date(2026, 1, 1))
    names = [
        m["name"] for m in data(client.get("/api/members", query_string={"sort_by": "roster", "include_guests": True}))
    ]
    assert names == ["乙隊員", "甲校友", "丙離隊", "外校甲"]


def test_merge_duplicate_guest_moves_matches(client, db, admin_headers, players):
    p1, p2, p3, _ = players
    duplicate = make_guest("王小明", gender=GenderEnum.MALE)
    original = make_guest("王小明（舊）", gender=GenderEnum.MALE)
    record = create_record(client, admin_headers, [p1, p2, p3, duplicate])

    merged = data(
        client.post(f"/api/members/{duplicate.id}/merge", headers=admin_headers, json={"into_id": original.id})
    )
    assert merged["id"] == original.id
    assert db.session.get(Member, duplicate.id) is None
    assert db.session.get(MatchRecord, record["id"]).player4_id == original.id


def test_merge_rejects_players_from_same_match_and_accounts(client, admin_headers, players):
    p1, p2, p3, p4 = players
    guest = make_guest("訪客")
    create_record(client, admin_headers, [p1, p2, p3, guest])
    error(client.post(f"/api/members/{guest.id}/merge", headers=admin_headers, json={"into_id": p1.id}), 409)
    error(client.post(f"/api/members/{p4.id}/merge", headers=admin_headers, json={"into_id": guest.id}), 409)
    error(client.post(f"/api/members/{guest.id}/merge", headers=admin_headers, json={"into_id": guest.id}), 409)


def test_roster_category_and_guest_promotion(client, admin_headers, orgs):
    team, _ = orgs
    guest = make_guest("對手")
    assert data(client.get(f"/api/members/{guest.id}"))["roster_category"] == "guest"

    promoted = data(
        client.put(
            f"/api/members/{guest.id}", headers=admin_headers, json={"is_guest": False, "organization_id": team.id}
        )
    )
    assert (promoted["is_guest"], promoted["roster_category"]) == (False, "team")
    error(client.put(f"/api/members/{guest.id}", headers=admin_headers, json={"is_guest": True}), 400)
