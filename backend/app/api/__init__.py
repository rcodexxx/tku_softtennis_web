from flask import Blueprint, Flask

from . import auth, boards, events, guests, leaderboard, matches, members, organizations, profile, seasons, uploads


def register_blueprints(app: Flask) -> None:
    api = Blueprint("api", __name__, url_prefix="/api")
    for module in (
        auth,
        profile,
        organizations,
        members,
        guests,
        matches,
        events,
        leaderboard,
        seasons,
        boards,
        uploads,
    ):
        api.register_blueprint(module.bp)
    app.register_blueprint(api)
