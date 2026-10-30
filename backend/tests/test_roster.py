from datetime import date

from app.enums import GenderEnum
from app.models import Member

from .conftest import data, error, make_guest


def put_roster(client, headers, roster, status=200):
    return data(client.put("/api/members/roster", headers=headers, json={"roster": roster}), status)


def test_graduation_moves_to_alumni_without_leaving(client, db, admin_headers, orgs, team_players):
    _, alumni = orgs
    p1 = team_players[0]
    put_roster(client, admin_headers, [{"member_id": p1.id, "status": "alumni"}])
    db.session.expire_all()
    member = db.session.get(Member, p1.id)
    assert (member.organization_id, member.leaved_date) == (alumni.id, None)
    roster = {r["member"]["name"]: r["status"] for r in data(client.get("/api/members/roster", headers=admin_headers))}
    assert roster["甲"] == "alumni"


def test_left_players_stay_active_and_can_return(client, db, admin_headers, orgs, team_players):
    team, _ = orgs
    p2 = team_players[1]
    put_roster(client, admin_headers, [{"member_id": p2.id, "status": "left"}])
    db.session.expire_all()
    member = db.session.get(Member, p2.id)
    assert member.leaved_date == date.today()
    assert member.organization_id == team.id
    # 還是活躍的球員，記錄比賽時選得到
    assert "乙" in {m["name"] for m in data(client.get("/api/members"))}
    assert data(client.get("/api/members/roster", headers=admin_headers))[-1]["status"] == "left"

    put_roster(client, admin_headers, [{"member_id": p2.id, "status": "team"}])
    db.session.expire_all()
    assert db.session.get(Member, p2.id).leaved_date is None


def test_roster_rejects_guests_and_members(client, member_headers, admin_headers, orgs):
    guest = make_guest("訪客", organization_id=orgs[0].id)
    error(
        client.put(
            "/api/members/roster", headers=admin_headers, json={"roster": [{"member_id": guest.id, "status": "left"}]}
        ),
        400,
    )
    error(
        client.put(
            "/api/members/roster", headers=member_headers, json={"roster": [{"member_id": 1, "status": "team"}]}
        ),
        403,
    )
    error(client.put("/api/members/roster", headers=admin_headers, json={"roster": []}), 400)


def test_a_division_starts_one_point_higher(client, db, admin_headers, orgs, team_players):
    p1, _, p3, _ = team_players
    data(client.put(f"/api/members/{p1.id}", headers=admin_headers, json={"is_a_division": True}))
    data(client.put(f"/api/members/{p3.id}", headers=admin_headers, json={"is_a_division": True}))
    members = {m["name"]: m for m in data(client.get("/api/members"))}
    assert (members["甲"]["rating"], members["甲"]["is_a_division"]) == (6.0, True)
    assert members["丙"]["rating"] == 5.0
    assert members["乙"]["rating"] == 5.0
    assert db.session.get(Member, p3.id).gender == GenderEnum.FEMALE
