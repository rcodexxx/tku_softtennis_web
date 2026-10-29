from datetime import UTC, datetime

from sqlalchemy import Enum


def enum_column(enum_cls, name: str) -> Enum:
    """以 enum 的 value（而非 name）存入資料庫。"""
    return Enum(enum_cls, name=name, values_callable=lambda members: [m.value for m in members])


def utcnow() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)
