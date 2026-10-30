from types import SimpleNamespace

import pytest

from app.models import Match, MatchRecord, Member

from .conftest import data, error, make_user

DETAILED_GAMES = [
    {"a_score": 4, "b_score": 2},
    {"a_score": 1, "b_score": 4},
    {"a_score": 4, "b_score": 0},
    {"a_score": 4, "b_score": 3},
    {"a_score": 4, "b_score": 1},
]


def doubles_payload(players, a_games=4, b_games=2, **extra):
    p1, p2, p3, p4 = players
    payload = {
        "match_date": "2025-03-01",
        "match_type": "doubles",
        "match_format": "games_7",
        "player1_id": p1.id,
        "player2_id": p2.id,
        "player3_id": p3.id,
        "player4_id": p4.id,
        "a_games": a_games,
        "b_games": b_games,
    }
    payload.update(extra)
    return {key: value for key, value in payload.items() if value is not None}


def create_record(client, headers, players, **kwargs):
    return data(client.post("/api/match-records", headers=headers, json=doubles_payload(players, **kwargs)), 201)


def ratings(db):
    db.session.expire_all()
    return {m.id: (m.mu, m.sigma) for m in db.session.query(Member)}


def test_create_match_record_updates_ratings(client, db, coach_headers, players):
    record = create_record(client, coach_headers, players)
    assert record["side_a_outcome"] == "win"
    assert record["match_type"] == "doubles"
    assert record["player1"]["name"] == "甲"
    assert record["has_detailed_scores"] is False

    p1, _, p3, _ = (db.session.get(Member, p.id) for p in players)
    assert p1.mu > 25.0
    assert p3.mu < 25.0
    assert p1.sigma < 25.0 / 3


def test_regular_member_cannot_record_match(client, member_headers, players):
    error(client.post("/api/match-records", headers=member_headers, json=doubles_payload(players)), 403)


def test_singles_rejects_four_players(client, admin_headers, players):
    error(
        client.post("/api/match-records", headers=admin_headers, json=doubles_payload(players, match_type="singles")),
        400,
    )


def test_doubles_requires_four_players(client, admin_headers, players):
    payload = doubles_payload(players)
    del payload["player4_id"]
    error(client.post("/api/match-records", headers=admin_headers, json=payload), 400)


def test_rejects_duplicate_players(client, admin_headers, players):
    p1, p2, p3, _ = players
    error(client.post("/api/match-records", headers=admin_headers, json=doubles_payload((p1, p2, p3, p1))), 400)


def test_rejects_unknown_player(client, admin_headers, players):
    p1, p2, p3, _ = players
    unknown = SimpleNamespace(id=999)
    error(client.post("/api/match-records", headers=admin_headers, json=doubles_payload((p1, p2, p3, unknown))), 404)


def test_requires_totals_or_game_scores(client, admin_headers, players):
    payload = doubles_payload(players)
    del payload["a_games"], payload["b_games"]
    error(client.post("/api/match-records", headers=admin_headers, json=payload), 400)


def test_create_with_game_scores_computes_totals(client, admin_headers, players):
    payload = doubles_payload(players, a_games=None, b_games=None, games=DETAILED_GAMES, first_serve_side="side_a")
    record = data(client.post("/api/match-records", headers=admin_headers, json=payload), 201)
    assert (record["a_games"], record["b_games"]) == (4, 1)
    assert record["has_detailed_scores"] is True
    assert [g["serve_side"] for g in record["games"]] == ["side_a", "side_b", "side_a", "side_b", "side_a"]
    assert record["serve_advantage"]["side_a"] == {"serve_games": 3, "serve_wins": 3, "serve_win_rate": 100.0}
    assert record["serve_advantage"]["side_b"] == {"serve_games": 2, "serve_wins": 1, "serve_win_rate": 50.0}


def test_rejects_inconsistent_totals(client, admin_headers, players):
    payload = doubles_payload(players, a_games=4, b_games=0, games=DETAILED_GAMES)
    assert "b_games" in error(client.post("/api/match-records", headers=admin_headers, json=payload), 400)["details"]


def test_list_records_paginated_filtered_and_sorted(client, admin_headers, players):
    create_record(client, admin_headers, players)
    create_record(client, admin_headers, players, a_games=1, b_games=4, match_date="2025-04-01")

    resp = client.get("/api/match-records", query_string={"per_page": 1})
    assert data(resp)[0]["match_date"] == "2025-04-01"
    assert resp.get_json()["meta"] == {"page": 1, "per_page": 1, "total": 2, "pages": 2}

    resp = client.get("/api/match-records", query_string={"start_date": "2025-03-15", "sort_order": "asc"})
    assert [r["match_date"] for r in data(resp)] == ["2025-04-01"]

    resp = client.get("/api/match-records", query_string={"player_id": players[0].id, "sort_order": "asc"})
    assert [r["match_date"] for r in data(resp)] == ["2025-03-01", "2025-04-01"]


def test_get_record(client, admin_headers, players):
    record_id = create_record(client, admin_headers, players)["id"]
    assert data(client.get(f"/api/match-records/{record_id}"))["id"] == record_id
    error(client.get("/api/match-records/999"), 404)


def test_update_record_flips_outcome(client, db, admin_headers, players):
    record_id = create_record(client, admin_headers, players)["id"]
    record = data(
        client.put(f"/api/match-records/{record_id}", headers=admin_headers, json={"a_games": 1, "b_games": 4})
    )
    assert record["side_a_outcome"] == "loss"
    assert db.session.get(Member, players[0].id).mu < 25.0


def test_update_metadata_only(client, admin_headers, players):
    record_id = create_record(client, admin_headers, players)["id"]
    record = data(
        client.put(
            f"/api/match-records/{record_id}",
            headers=admin_headers,
            json={"notes": "冠軍賽", "court_surface": "hard_court"},
        )
    )
    assert record["notes"] == "冠軍賽"
    assert record["court_surface"] == "hard_court"
    assert (record["a_games"], record["b_games"]) == (4, 2)


def test_update_switch_to_singles_must_clear_partners(client, admin_headers, players):
    record_id = create_record(client, admin_headers, players)["id"]
    error(client.put(f"/api/match-records/{record_id}", headers=admin_headers, json={"match_type": "singles"}), 400)
    record = data(
        client.put(
            f"/api/match-records/{record_id}",
            headers=admin_headers,
            json={"match_type": "singles", "player2_id": None, "player4_id": None},
        )
    )
    assert record["player2_id"] is None and record["match_type"] == "singles"


def test_update_totals_clears_old_game_scores(client, admin_headers, players):
    payload = doubles_payload(players, a_games=None, b_games=None, games=DETAILED_GAMES)
    record_id = data(client.post("/api/match-records", headers=admin_headers, json=payload), 201)["id"]
    record = data(
        client.put(f"/api/match-records/{record_id}", headers=admin_headers, json={"a_games": 2, "b_games": 4})
    )
    assert record["has_detailed_scores"] is False
    assert record["side_a_outcome"] == "loss"


def test_delete_record_removes_match_and_resets_ratings(client, db, admin_headers, players):
    record_id = create_record(client, admin_headers, players)["id"]
    assert data(client.delete(f"/api/match-records/{record_id}", headers=admin_headers)) is None
    assert db.session.get(MatchRecord, record_id) is None
    assert db.session.query(Match).count() == 0
    for mu, sigma in ratings(db).values():
        assert mu == pytest.approx(25.0)
        assert sigma == pytest.approx(25.0 / 3)


def test_only_admin_deletes_record(client, admin_headers, coach_headers, players):
    record_id = create_record(client, admin_headers, players)["id"]
    error(client.delete(f"/api/match-records/{record_id}", headers=coach_headers), 403)


def test_editing_and_reverting_a_match_restores_all_ratings(client, db, admin_headers, players):
    p1, p2, p3, p4 = players
    p5 = make_user("0920000005", name="戊").member_profile
    create_record(client, admin_headers, players)
    second = create_record(client, admin_headers, (p1, p5, p3, p4), match_date="2025-03-02")
    create_record(client, admin_headers, (p2, p5, p3, p4), match_date="2025-03-03", a_games=1, b_games=4)
    before = ratings(db)

    for a_games, b_games in [(1, 4), (4, 2)]:
        data(
            client.put(
                f"/api/match-records/{second['id']}",
                headers=admin_headers,
                json={"a_games": a_games, "b_games": b_games},
            )
        )

    after = ratings(db)
    for member_id, (mu, sigma) in before.items():
        assert after[member_id] == (pytest.approx(mu), pytest.approx(sigma))


def test_backdated_match_triggers_full_recalculation(client, db, admin_headers, players):
    """先輸入晚的比賽、再補登早的比賽，結果要和照時間順序輸入相同。"""
    later = {"match_date": "2025-05-01", "a_games": 4, "b_games": 1}
    earlier = {"match_date": "2025-04-01", "a_games": 0, "b_games": 4}

    create_record(client, admin_headers, players, **later)
    create_record(client, admin_headers, players, **earlier)
    out_of_order = ratings(db)

    for record in db.session.query(MatchRecord).all():
        client.delete(f"/api/match-records/{record.id}", headers=admin_headers)
    create_record(client, admin_headers, players, **earlier)
    create_record(client, admin_headers, players, **later)
    in_order = ratings(db)

    for member_id, (mu, sigma) in in_order.items():
        assert out_of_order[member_id] == (pytest.approx(mu), pytest.approx(sigma))


def test_filter_by_multiple_players_and_result(client, admin_headers, players):
    p1, p2, p3, p4 = players
    p5 = make_user("0920000005", name="戊").member_profile
    create_record(client, admin_headers, players)  # 甲乙 勝 丙丁
    create_record(client, admin_headers, (p1, p5, p3, p4), a_games=1, b_games=4)  # 甲戊 敗
    create_record(client, admin_headers, (p3, p4, p1, p2), a_games=4, b_games=1)  # 丙丁 勝 甲乙

    def ids(**params):
        return sorted(r["id"] for r in data(client.get("/api/match-records", query_string=params)))

    all_ids = ids()
    assert len(ids(player_ids=f"{p1.id},{p2.id}")) == 2
    assert len(ids(player_ids=f"{p1.id},{p5.id}")) == 1
    assert ids(player_ids=str(p1.id), result="win") == [all_ids[0]]
    assert ids(player_ids=str(p1.id), result="loss") == all_ids[1:]
    assert len(ids(player_ids=str(p3.id), result="win")) == 2


def test_filter_rejects_bad_player_ids(client):
    error(client.get("/api/match-records", query_string={"player_ids": "1,abc"}), 400)


def test_batch_create_matches_in_order_ratings(client, db, coach_headers, admin_headers, players):
    """批次建立（日期亂序）的結果要和照時間順序一場一場建立相同。"""
    later = doubles_payload(players, match_date="2025-05-01", a_games=4, b_games=1)
    earlier = doubles_payload(players, match_date="2025-04-01", a_games=0, b_games=4)

    resp = client.post("/api/match-records/batch", headers=coach_headers, json={"records": [later, earlier]})
    created = data(resp, 201)
    assert [r["match_date"] for r in created] == ["2025-05-01", "2025-04-01"]
    assert created[1]["side_a_outcome"] == "loss"
    assert "2 場" in resp.get_json()["message"]
    batched = ratings(db)

    for record in db.session.query(MatchRecord).all():
        client.delete(f"/api/match-records/{record.id}", headers=admin_headers)
    create_record(client, admin_headers, players, match_date="2025-04-01", a_games=0, b_games=4)
    create_record(client, admin_headers, players, match_date="2025-05-01", a_games=4, b_games=1)
    for member_id, (mu, sigma) in ratings(db).items():
        assert batched[member_id] == (pytest.approx(mu), pytest.approx(sigma))


def test_batch_create_is_all_or_nothing(client, db, admin_headers, players):
    good = doubles_payload(players)
    bad = doubles_payload(players, player4_id=players[0].id)
    body = error(client.post("/api/match-records/batch", headers=admin_headers, json={"records": [good, bad]}), 400)
    assert "1" in body["details"]["records"]
    assert db.session.query(MatchRecord).count() == 0

    missing = doubles_payload(players, player4_id=9999)
    error(client.post("/api/match-records/batch", headers=admin_headers, json={"records": [good, missing]}), 404)
    assert db.session.query(MatchRecord).count() == 0


def test_batch_create_requires_staff_and_records(client, admin_headers, member_headers, players):
    body = {"records": [doubles_payload(players)]}
    error(client.post("/api/match-records/batch", headers=member_headers, json=body), 403)
    error(client.post("/api/match-records/batch", headers=admin_headers, json={"records": []}), 400)
