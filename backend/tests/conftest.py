import os

os.environ.setdefault("JWT_SECRET_KEY", "test-jwt-secret-key-with-enough-length")
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.pop("TEST_DATABASE_URL", None)

import pytest  # noqa: E402

from app import create_app  # noqa: E402
from app.enums import GenderEnum, UserRoleEnum  # noqa: E402
from app.extensions import db as _db  # noqa: E402
from app.models import Member, Organization, User  # noqa: E402

ADMIN_USERNAME = "0900000000"
ADMIN_PASSWORD = "admin-password"


@pytest.fixture()
def app():
    app = create_app("testing")
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def db(app):
    return _db


def make_user(username, password="password", role=UserRoleEnum.MEMBER, name=None, **member_kwargs):
    user = User(username=username, role=role, display_name=name or username)
    user.set_password(password)
    member = Member(user=user, name=name or username, **member_kwargs)
    _db.session.add_all([user, member])
    _db.session.commit()
    return user


def make_guest(name, created_by=None, **kwargs):
    guest = Member(name=name, is_guest=True, created_by_user_id=created_by, **kwargs)
    _db.session.add(guest)
    _db.session.commit()
    return guest


def make_org(name, short_name=None):
    org = Organization(name=name, short_name=short_name)
    _db.session.add(org)
    _db.session.commit()
    return org


def login(client, username, password):
    resp = client.post("/api/auth/login", json={"username": username, "password": password})
    assert resp.status_code == 200, resp.get_json()
    return resp.get_json()["data"]


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def admin(app):
    return make_user(ADMIN_USERNAME, ADMIN_PASSWORD, role=UserRoleEnum.ADMIN, name="管理員")


@pytest.fixture()
def admin_headers(client, admin):
    return auth_header(login(client, ADMIN_USERNAME, ADMIN_PASSWORD)["access_token"])


@pytest.fixture()
def member_user(app):
    return make_user("0911111111", "member-password", name="一般隊員")


@pytest.fixture()
def member_headers(client, member_user):
    return auth_header(login(client, "0911111111", "member-password")["access_token"])


@pytest.fixture()
def coach_headers(client):
    make_user("0912222222", "coach-password", role=UserRoleEnum.COACH, name="教練")
    return auth_header(login(client, "0912222222", "coach-password")["access_token"])


def data(resp, status=200):
    assert resp.status_code == status, resp.get_json()
    return resp.get_json()["data"]


def error(resp, status):
    assert resp.status_code == status, resp.get_json()
    return resp.get_json()["error"]


@pytest.fixture()
def players(app):
    """Four regular members for doubles matches: two male, two female."""
    p1 = make_user("0920000001", name="甲", gender=GenderEnum.MALE).member_profile
    p2 = make_user("0920000002", name="乙", gender=GenderEnum.MALE).member_profile
    p3 = make_user("0920000003", name="丙", gender=GenderEnum.FEMALE).member_profile
    p4 = make_user("0920000004", name="丁", gender=GenderEnum.FEMALE).member_profile
    return p1, p2, p3, p4
