from app.enums import MatchCategoryEnum
from app.models import Match

from .conftest import data, error, make_guest, make_user
from .test_matches import create_record, doubles_payload, ratings


def make_event(client, headers, **fields):
    payload = {"name": "淡江盃", "start_date": "2025-03-01", **fields}
    return data(client.post("/api/events", headers=headers, json=payload), 201)


def test_event_crud_and_match_count(client, admin_headers, players):
    event = make_event(client, admin_headers, location="淡水")
    assert event["counts_toward_rating"] is True
    create_record(client, admin_headers, players, event_id=event["id"])

    events = data(client.get("/api/events"))
    assert [(e["name"], e["match_count"]) for e in events] == [("淡江盃", 1)]
    updated = data(client.put(f"/api/events/{event['id']}", headers=admin_headers, json={"name": "淡江盃 2025"}))
    assert updated["name"] == "淡江盃 2025"
    # 還有比賽時不能刪
    error(client.delete(f"/api/events/{event['id']}", headers=admin_headers), 409)


def test_matches_get_category_from_event(client, db, admin_headers, players):
    event = make_event(client, admin_headers)
    record = create_record(client, admin_headers, players, event_id=event["id"])
    assert record["category"] == "event"
    assert record["event"] == {"id": event["id"], "name": "淡江盃"}

    friendly = create_record(client, admin_headers, players, category="friendly")
    assert friendly["category"] == "friendly" and friendly["event"] is None
    assert create_record(client, admin_headers, players)["category"] == "internal"

    rows = data(client.get("/api/match-records", query_string={"category": "friendly"}))
    assert [r["id"] for r in rows] == [friendly["id"]]
    rows = data(client.get("/api/match-records", query_string={"event_id": event["id"]}))
    assert [r["id"] for r in rows] == [record["id"]]

    # 改成隊內就離開賽事
    moved = data(client.put(f"/api/match-records/{record['id']}", headers=admin_headers, json={"category": "internal"}))
    assert (moved["category"], moved["event"]) == ("internal", None)
    assert db.session.get(Match, moved["match_id"]).category == MatchCategoryEnum.INTERNAL


def test_event_category_requires_event(client, admin_headers, players):
    def post(**fields):
        return client.post("/api/match-records", headers=admin_headers, json=doubles_payload(players, **fields))

    error(post(category="event"), 400)
    error(post(event_id=99), 404)


def test_events_can_be_left_out_of_ratings(client, db, admin_headers, players):
    event = make_event(client, admin_headers, counts_toward_rating=False)
    create_record(client, admin_headers, players, event_id=event["id"])
    assert all(value is None for value in ratings(db).values())

    data(client.put(f"/api/events/{event['id']}", headers=admin_headers, json={"counts_toward_rating": True}))
    assert ratings(db)[players[0].id] is not None


def test_unfamiliar_guest_opponents_count_less(client, db, admin_headers, players):
    p1, p2, _, _ = players
    g1, g2 = make_guest("校外甲"), make_guest("校外乙")
    team = [p1, p2, g1, g2]

    # 對手起始分數都是 4.5、比分相同：對上陌生訪客只算 1/3，對上隊員照常
    create_record(client, admin_headers, team, a_games=0, b_games=4)
    against_guests = 5.0 - ratings(db)[p1.id]
    data(client.delete(f"/api/match-records/{data(client.get('/api/match-records'))[0]['id']}", headers=admin_headers))

    q1 = make_user("0930000011", name="隊員一").member_profile
    q2 = make_user("0930000012", name="隊員二").member_profile
    create_record(client, admin_headers, [p1, p2, q1, q2], a_games=0, b_games=4)
    against_members = 5.0 - ratings(db)[p1.id]
    assert 0 < against_guests < against_members
