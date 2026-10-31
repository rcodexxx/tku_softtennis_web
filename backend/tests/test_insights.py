from .conftest import data, error
from .test_matches import create_record


def test_insights_list_partners_opponents_and_trend(client, admin_headers, players):
    p1, p2, p3, p4 = players
    create_record(client, admin_headers, players, a_games=4, b_games=2)
    create_record(client, admin_headers, [p1, p3, p2, p4], a_games=1, b_games=4, match_date="2025-03-02")

    result = data(client.get(f"/api/members/{p1.id}/insights"))
    assert (result["member"]["name"], result["wins"], result["losses"]) == ("甲", 1, 1)
    assert [point["won"] for point in result["trend"]] == [True, False]

    partners = {entry["player"]["name"]: (entry["wins"], entry["losses"]) for entry in result["partners"]}
    assert partners == {"乙": (1, 0), "丙": (0, 1)}
    opponents = {entry["player"]["name"]: (entry["matches"], entry["win_rate"]) for entry in result["opponents"]}
    # 丁兩場都是對手；乙、丙各一場
    assert opponents["丁"] == (2, 50.0)
    assert result["opponents"][0]["player"]["name"] == "丁"


def test_insights_for_player_without_matches(client, players):
    result = data(client.get(f"/api/members/{players[0].id}/insights"))
    assert (result["wins"], result["losses"], result["partners"], result["seasons"]) == (0, 0, [], [])
    assert result["rating"] == 5.0
    error(client.get("/api/members/999/insights"), 404)


def test_insights_season_history(client, admin_headers, players):
    data(
        client.post("/api/seasons", headers=admin_headers, json={"name": "113 學年度", "start_date": "2025-01-01"}), 201
    )
    create_record(client, admin_headers, players)
    history = data(client.get(f"/api/members/{players[0].id}/insights"))["seasons"]
    assert [(h["season_name"], h["matches"], h["is_current"]) for h in history] == [("113 學年度", 1, True)]
    assert history[0]["rank"] in (1, 2)
