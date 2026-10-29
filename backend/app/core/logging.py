import logging

from flask import Flask

LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s %(module)s:%(lineno)d %(message)s"


def configure_logging(app: Flask) -> None:
    level = getattr(logging, str(app.config["LOG_LEVEL"]).upper(), logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    app.logger.handlers = [handler]
    app.logger.setLevel(level)
    app.logger.propagate = False
