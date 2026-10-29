import pytest

from .conftest import auth_header, data, error, login
from .test_matches import create_record


@pytest.fixture()
def p1_headers(client, players):
    return auth_header(login(client, "0920000001", "password")["access_token"])


def test_get_my_profile(client, p1_headers):
    profile = data(client.get("/api/profile/me", headers=p1_headers))
    assert profile["username"] == "0920000001"
    assert profile["member"]["name"] == "甲"


def test_update_my_profile(client, p1_headers):
    profile = data(client.put("/api/profile/me", headers=p1_headers, json={"display_name": "阿甲", "position": "back"}))
    assert profile["display_name"] == "阿甲"
    assert profile["member"]["position"] == "back"


def test_update_my_profile_email_taken(client, db, players, p1_headers):
    players[1].user.email = "taken@example.com"
    db.session.commit()
    error(client.put("/api/profile/me", headers=p1_headers, json={"email": "taken@example.com"}), 409)


def test_profile_cannot_change_role(client, db, players, p1_headers):
    client.put("/api/profile/me", headers=p1_headers, json={"role": "admin"})
    db.session.refresh(players[0].user)
    assert players[0].user.role.value == "member"


def test_my_matches_include_perspective(client, admin_headers, players, p1_headers):
    create_record(client, admin_headers, players)
    resp = client.get("/api/profile/me/matches", headers=p1_headers)
    match = data(resp)[0]
    assert match["perspective"] == {
        "side": "A",
        "is_winner": True,
        "my_games": 4,
        "opponent_games": 2,
        "opponent_names": ["丙", "丁"],
    }
    assert resp.get_json()["meta"]["total"] == 1


def test_my_matches_from_side_b(client, admin_headers, players):
    create_record(client, admin_headers, players)
    headers = auth_header(login(client, "0920000003", "password")["access_token"])
    perspective = data(client.get("/api/profile/me/matches", headers=headers))[0]["perspective"]
    assert (perspective["side"], perspective["is_winner"], perspective["my_games"]) == ("B", False, 2)
