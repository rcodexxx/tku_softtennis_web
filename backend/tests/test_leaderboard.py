from .conftest import data, error, make_guest
from .test_matches import create_record


def test_leaderboard_ranks_and_match_stats(client, admin_headers, players):
    create_record(client, admin_headers, players)
    resp = client.get("/api/leaderboard", query_string={"min_matches": 1})
    rows = data(resp)
    assert resp.get_json()["meta"]["total"] == 4
    assert [r["rank"] for r in rows] == [1, 2, 3, 4]
    by_name = {r["name"]: r for r in rows}
    assert (by_name["甲"]["wins"], by_name["甲"]["losses"]) == (1, 0)
    assert by_name["丙"]["win_rate"] == 0.0
    assert by_name["甲"]["last_match_date"] == "2025-03-01"
    assert rows[0]["conservative_score"] >= rows[-1]["conservative_score"]


def test_leaderboard_min_matches_filters_out_new_players(client, players):
    make_guest("新訪客")
    assert len(data(client.get("/api/leaderboard"))) == 5
    assert len(data(client.get("/api/leaderboard", query_string={"min_matches": 1}))) == 0


def test_leaderboard_excludes_guests_on_request(client, players):
    make_guest("新訪客")
    rows = data(client.get("/api/leaderboard", query_string={"include_guests": "false"}))
    assert all(not r["is_guest"] for r in rows)


def test_leaderboard_sort_by_win_rate(client, admin_headers, players):
    create_record(client, admin_headers, players)
    rows = data(client.get("/api/leaderboard", query_string={"sort_by": "win_rate", "min_matches": 1}))
    assert rows[0]["win_rate"] == 100.0


def test_leaderboard_pagination(client, players):
    resp = client.get("/api/leaderboard", query_string={"per_page": 3, "page": 2})
    assert [r["rank"] for r in data(resp)] == [4]
    assert resp.get_json()["meta"]["pages"] == 2


def test_leaderboard_rejects_bad_params(client):
    error(client.get("/api/leaderboard", query_string={"sort_by": "nope"}), 400)


def test_leaderboard_experience_filter(client, players):
    assert len(data(client.get("/api/leaderboard", query_string={"experience_level": "新手"}))) == 4
    assert len(data(client.get("/api/leaderboard", query_string={"experience_level": "資深"}))) == 0


def test_statistics(client, admin_headers, players):
    create_record(client, admin_headers, players)
    stats = data(client.get("/api/leaderboard/statistics"))
    assert stats["total_members"] == 5  # 4 位球員 + 管理員
    assert stats["total_matches"] == 1
    assert stats["experience_distribution"]


def test_compare_players(client, admin_headers, players):
    create_record(client, admin_headers, players)
    p1, _, p3, _ = players
    result = data(client.get(f"/api/leaderboard/compare/{p1.id}/{p3.id}"))
    assert result["comparison"]["is_likely_stronger"] is True
    assert result["comparison"]["predicted_win_probability"] > 0.5
    assert result["member1"]["wins"] == 1


def test_compare_same_player_rejected(client, players):
    error(client.get(f"/api/leaderboard/compare/{players[0].id}/{players[0].id}"), 400)
