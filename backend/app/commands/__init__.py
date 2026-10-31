from flask import Flask

from .admin import init_admin, list_admins, reset_admin_password
from .demo import demo_seed
from .ratings import rating_stats, recalculate_all_ratings

COMMANDS = (init_admin, list_admins, reset_admin_password, recalculate_all_ratings, rating_stats, demo_seed)


def register_commands(app: Flask) -> None:
    for command in COMMANDS:
        app.cli.add_command(command)
