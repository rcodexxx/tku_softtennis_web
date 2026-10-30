from datetime import date, timedelta

import pytest

from app.enums import GenderEnum
from app.models import Member

from .conftest import auth_header, data, error, login, make_guest, make_org, make_user
from .test_matches import create_record, ratings

TODAY = date.today().isoformat()


def start_season(client, headers, name, start_date=TODAY, roster=(), status=201):
    payload = {"name": name, "start_date": start_date, "roster": list(roster)}
    return client.post("/api/seasons", headers=headers, json=payload), status


def started(client, headers, name, **kwargs):
    resp, status = start_season(client, headers, name, **kwargs)
    return data(resp, status)


@pytest.fixture()
def orgs(app):
    team, alumni = make_org("淡江大學軟網隊"), make_org("校友會")
    app.config.update(TEAM_ORGANIZATION_ID=team.id, ALUMNI_ORGANIZATION_ID=alumni.id)
    return team, alumni


@pytest.fixture()
def team_players(orgs):
    team, _ = orgs
    return tuple(
        make_user(f"092000000{i}", name=name, gender=gender, organization_id=team.id).member_profile
        for i, (name, gender) in enumerate(
            [("甲", GenderEnum.MALE), ("乙", GenderEnum.MALE), ("丙", GenderEnum.FEMALE), ("丁", GenderEnum.FEMALE)],
            start=1,
        )
    )


def test_list_seasons_is_empty_at_first(client):
    assert data(client.get("/api/seasons")) == []


def test_only_admin_can_start_season(client, coach_headers):
    error(start_season(client, coach_headers, "115 學年度")[0], 403)


def test_new_season_resets_ratings_and_keeps_old_leaderboard(client, db, admin_headers, team_players):
    started(client, admin_headers, "113 學年度", start_date="2025-01-01")
    create_record(client, admin_headers, team_players)
    old_ratings = ratings(db)
    assert old_ratings[team_players[0].id] is not None

    season = started(client, admin_headers, "115 學年度")
    assert season["is_current"] is True
    assert season["match_count"] == 0
    # 新賽季還沒比賽，所有人回到起始分數
    assert all(value is None for value in ratings(db).values())
    assert data(client.get("/api/leaderboard", query_string={"min_matches": 1})) == []

    seasons = data(client.get("/api/seasons"))
    assert [s["name"] for s in seasons] == ["115 學年度", "113 學年度"]
    old = seasons[1]
    assert (old["is_current"], old["match_count"]) == (False, 1)
    assert old["end_date"] == (date.today() - timedelta(days=1)).isoformat()

    resp = client.get("/api/leaderboard", query_string={"season_id": old["id"]})
    rows = data(resp)
    assert resp.get_json()["meta"]["season"]["name"] == "113 學年度"
    assert {r["name"]: r["rating"] for r in rows} == {p.name: round(old_ratings[p.id], 2) for p in team_players}
    assert all(r["total_matches"] == 1 for r in rows)


def test_matches_in_new_season_only_count_there(client, db, admin_headers, team_players):
    started(client, admin_headers, "113 學年度", start_date="2025-01-01")
    create_record(client, admin_headers, team_players)
    started(client, admin_headers, "115 學年度")
    create_record(client, admin_headers, team_players, match_date=TODAY)

    rows = data(client.get("/api/leaderboard", query_string={"min_matches": 1}))
    assert all(r["total_matches"] == 1 for r in rows)
    stats = data(client.get(f"/api/members/{team_players[0].id}/stats"))
    assert stats["total_matches"] == 1
    assert data(client.get("/api/leaderboard/statistics"))["total_matches"] == 1


def test_profile_shows_performance_for_every_season(client, admin_headers, team_players):
    started(client, admin_headers, "113 學年度", start_date="2025-01-01")
    create_record(client, admin_headers, team_players)
    started(client, admin_headers, "115 學年度")
    create_record(client, admin_headers, team_players, match_date=TODAY)

    headers = auth_header(login(client, "0920000001", "password")["access_token"])
    matches = data(client.get("/api/profile/me/matches", headers=headers))
    assert len(matches) == 2
    # 兩個賽季的第一場都從起始分數 5.0 算起，所以表現一樣
    assert matches[0]["perspective"]["performance"] == matches[1]["perspective"]["performance"]


def test_roster_changes_apply_and_old_season_keeps_old_teams(client, db, admin_headers, orgs, team_players):
    team, alumni = orgs
    p1, p2, p3, _ = team_players
    started(client, admin_headers, "113 學年度", start_date="2025-01-01")
    create_record(client, admin_headers, team_players)

    roster = data(client.get("/api/seasons/roster", headers=admin_headers))
    assert {r["member"]["name"]: (r["status"], r["total_matches"]) for r in roster} == {
        "甲": ("team", 1),
        "乙": ("team", 1),
        "丙": ("team", 1),
        "丁": ("team", 1),
    }

    started(
        client,
        admin_headers,
        "115 學年度",
        roster=[{"member_id": p1.id, "status": "alumni"}, {"member_id": p2.id, "status": "left"}],
    )
    db.session.expire_all()
    assert db.session.get(Member, p1.id).organization_id == alumni.id
    assert db.session.get(Member, p2.id).leaved_date == date.today()
    assert db.session.get(Member, p3.id).organization_id == team.id

    current_team = data(client.get("/api/leaderboard", query_string={"scope": "team"}))
    assert {r["name"] for r in current_team} == {"丙", "丁"}
    combined = data(client.get("/api/leaderboard", query_string={"scope": "combined"}))
    assert {r["name"] for r in combined} == {"甲", "丙", "丁"}

    old_id = data(client.get("/api/seasons"))[1]["id"]
    old_team = data(client.get("/api/leaderboard", query_string={"scope": "team", "season_id": old_id}))
    assert {r["name"] for r in old_team} == {"甲", "乙", "丙", "丁"}


def test_start_season_validation(client, admin_headers, orgs):
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    resp, _ = start_season(client, admin_headers, "未來賽季", start_date=tomorrow)
    assert "start_date" in error(resp, 400)["details"]

    started(client, admin_headers, "115 學年度")
    resp, _ = start_season(client, admin_headers, "同一天", start_date=TODAY)
    assert "start_date" in error(resp, 400)["details"]

    error(start_season(client, admin_headers, "115 學年度", start_date="2020-01-01")[0], 400)


def test_start_season_rejects_duplicate_name_and_guests(client, admin_headers, orgs):
    started(client, admin_headers, "113 學年度", start_date="2025-01-01")
    error(start_season(client, admin_headers, "113 學年度")[0], 409)

    guest = make_guest("訪客", organization_id=orgs[0].id)
    resp, _ = start_season(client, admin_headers, "115 學年度", roster=[{"member_id": guest.id, "status": "left"}])
    error(resp, 400)
    assert len(data(client.get("/api/seasons"))) == 1


def test_unknown_season_is_404(client):
    error(client.get("/api/leaderboard", query_string={"season_id": 99}), 404)
