import os
from datetime import timedelta

from dotenv import load_dotenv

# 必須在讀取 os.environ 之前載入 .env；已存在的環境變數不會被覆蓋
load_dotenv()


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    # 相對路徑的 SQLite 會放在 backend/instance/ 底下
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///tkust.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    CORS_ALLOWED_ORIGINS = _split_csv(
        os.environ.get("CORS_ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
    )

    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "DEBUG")


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URL", "sqlite://")
    LOG_LEVEL = "WARNING"


class ProductionConfig(Config):
    pass


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
