import io

from app.models import Member

from .conftest import auth_header, data, error, login

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64
WEBP = b"RIFF\x00\x00\x00\x00WEBPVP8 " + b"\x00" * 32


def upload(client, headers, member_id, content=PNG, filename="avatar.png"):
    return client.post(
        f"/api/members/{member_id}/avatar",
        headers=headers,
        data={"file": (io.BytesIO(content), filename)},
        content_type="multipart/form-data",
    )


def test_member_uploads_own_avatar_and_it_is_served(client, db, players):
    headers = auth_header(login(client, "0920000001", "password")["access_token"])
    member = data(upload(client, headers, players[0].id))
    assert member["avatar_url"].startswith(f"/api/uploads/avatars/{players[0].id}-")
    assert member["avatar_url"].endswith(".png")

    served = client.get(member["avatar_url"])
    assert served.status_code == 200
    assert served.data == PNG

    me = data(client.get("/api/auth/me", headers=headers))
    assert me["avatar_url"] == member["avatar_url"]


def test_replacing_avatar_deletes_old_file(client, app, players):
    headers = auth_header(login(client, "0920000001", "password")["access_token"])
    first = data(upload(client, headers, players[0].id))["avatar_url"]
    second = data(upload(client, headers, players[0].id, WEBP, "a.webp"))["avatar_url"]
    assert second.endswith(".webp")
    assert client.get(first).status_code == 404
    assert client.get(second).status_code == 200


def test_cannot_upload_for_someone_else(client, players):
    headers = auth_header(login(client, "0920000001", "password")["access_token"])
    error(upload(client, headers, players[1].id), 403)


def test_staff_can_upload_for_members(client, coach_headers, players):
    data(upload(client, coach_headers, players[1].id))


def test_rejects_non_image(client, admin_headers, players):
    err = error(upload(client, admin_headers, players[0].id, b"<script>alert(1)</script>", "x.png"), 400)
    assert "file" in err["details"]
    error(upload(client, admin_headers, players[0].id, b"\xff\xd8\xff" + b"\x00" * (3 * 1024 * 1024)), 400)


def test_remove_avatar(client, db, admin_headers, players):
    url = data(upload(client, admin_headers, players[0].id))["avatar_url"]
    member = data(client.delete(f"/api/members/{players[0].id}/avatar", headers=admin_headers))
    assert member["avatar_url"] is None
    assert client.get(url).status_code == 404
    assert db.session.get(Member, players[0].id).avatar_filename is None


def test_avatar_path_traversal_is_blocked(client):
    assert client.get("/api/uploads/avatars/../../app.db").status_code == 404
