from flask import Blueprint, Flask

from . import auth, guests, leaderboard, matches, members, organizations, profile


def register_blueprints(app: Flask) -> None:
    api = Blueprint("api", __name__, url_prefix="/api")
    for module in (auth, profile, organizations, members, guests, matches, leaderboard):
        api.register_blueprint(module.bp)
    app.register_blueprint(api)
