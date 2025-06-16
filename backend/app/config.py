import datetime
import os


class Config:
    APP_VERSION = "1.0.0"
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(hours=1)  # Access Token 有效期
    JWT_REFRESH_TOKEN_EXPIRES = datetime.timedelta(days=30)  # Refresh Token 有效期

    # WTF_CSRF_ENABLED = False
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True  # 可選，顯示執行的 SQL


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("TEST_DATABASE_URL") or "sqlite:///:memory:"
    )
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    pass


class RatingCalculationConfig(Config):
    TRUESKILL_CONSERVATIVE_K = 2.0
    TRUESKILL_MAX_SIGMA = 8.33
    TRUESKILL_MIN_SIGMA = 1.0
    TRUESKILL_EXP_THRESHOLD = 10


config_by_name = dict(
    development=DevelopmentConfig,
    testing=TestingConfig,
    production=ProductionConfig,
    default=DevelopmentConfig,
)
