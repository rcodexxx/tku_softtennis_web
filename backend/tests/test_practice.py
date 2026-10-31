from .conftest import data, error, make_user
from .test_matches import create_record


def make_session(client, headers, players, **fields):
    payload = {"session_date": "2025-03-01", "player_ids": [p.id for p in players], **fields}
    return data(client.post("/api/practice-sessions", headers=headers, json=payload), 201)


def test_practice_day_round_and_summary(client, admin_headers, players):
    extra = [make_user(f"09400000{i:02d}", name=f"球員{i}").member_profile for i in range(4)]
    session = make_session(client, admin_headers, list(players) + extra, location="淡水")
    assert len(session["attendees"]) == 8

    round_ = data(
        client.get(
            f"/api/practice-sessions/{session['id']}/next-round", headers=admin_headers, query_string={"courts": 2}
        )
    )
    assert len(round_["courts"]) == 2 and round_["resting"] == []

    create_record(client, admin_headers, players, session_id=session["id"])
    detail = data(client.get(f"/api/practice-sessions/{session['id']}"))
    assert detail["match_count"] == 1
    lines = {line["player"]["name"]: line for line in detail["summary"]["lines"]}
    assert (lines["甲"]["wins"], lines["丙"]["losses"]) == (1, 1)
    assert lines["甲"]["rating_change"] is not None
    assert detail["summary"]["pairs"][0]["wins"] == 1

    # 打過的人下一輪先休息
    round_ = data(
        client.get(
            f"/api/practice-sessions/{session['id']}/next-round", headers=admin_headers, query_string={"courts": 1}
        )
    )
    playing = {pid for court in round_["courts"] for pid in court["side_a"] + court["side_b"]}
    assert playing == {p.id for p in extra}


def test_practice_requires_staff_and_valid_players(client, admin_headers, member_headers, players):
    error(client.post("/api/practice-sessions", headers=member_headers, json={"session_date": "2025-03-01"}), 403)
    payload = {"session_date": "2025-03-01", "player_ids": [999]}
    error(client.post("/api/practice-sessions", headers=admin_headers, json=payload), 404)


def test_front_positions_and_pair_board(client, admin_headers, players):
    p1, p2, p3, p4 = players
    create_record(client, admin_headers, players, a_front_id=p2.id, b_front_id=p4.id)
    create_record(client, admin_headers, players, a_games=4, b_games=1, match_date="2025-03-02")
    pairs = data(client.get("/api/leaderboard/pairs"))
    top = pairs[0]
    assert {p["name"] for p in top["players"]} == {"甲", "乙"}
    assert (top["matches"], top["wins"]) == (2, 2)
    assert top["fronts"] == {str(p2.id): 1}
    assert top["chemistry"] == 0.0  # 只跟同一位搭檔打過，表現就等於自己的平均
    assert data(client.get("/api/leaderboard/pairs", query_string={"min_matches": 3})) == []

    bad = {"a_front_id": p3.id}
    error(
        client.put(
            f"/api/match-records/{create_record(client, admin_headers, players)['id']}", headers=admin_headers, json=bad
        ),
        400,
    )
