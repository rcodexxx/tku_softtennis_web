import os

from flask import Flask

from .api import register_blueprints
from .commands import register_commands
from .config import config_by_name
from .core.errors import register_error_handlers
from .core.logging import configure_logging
from .extensions import cors, db, jwt, migrate


def create_app(config_name: str | None = None) -> Flask:
    config_name = config_name or os.environ.get("FLASK_CONFIG", "default")
    if config_name not in config_by_name:
        raise ValueError(f"Unknown FLASK_CONFIG: {config_name!r}")

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    for key in ("SQLALCHEMY_DATABASE_URI", "JWT_SECRET_KEY"):
        if not app.config.get(key):
            raise RuntimeError(f"{key} is not configured.")

    app.config["UPLOAD_FOLDER"] = app.config["UPLOAD_FOLDER"] or os.path.join(app.instance_path, "uploads")
    configure_logging(app)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": app.config["CORS_ALLOWED_ORIGINS"]}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
    )

    from .core import auth  # noqa: F401  註冊 JWT callbacks

    register_error_handlers(app)
    register_blueprints(app)
    register_commands(app)

    @app.shell_context_processor
    def shell_context():
        from . import models

        return {"db": db, **{name: getattr(models, name) for name in models.__all__}}

    app.logger.info("App created with config %r", config_name)
    return app
