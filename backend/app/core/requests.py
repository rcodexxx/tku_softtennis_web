from flask import request
from marshmallow import Schema

from .errors import ValidationError


def load_json(schema: Schema, *, partial: bool = False) -> dict:
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        raise ValidationError("請求內容必須是 JSON 物件。")
    return schema.load(payload, partial=partial)


def load_args(schema: Schema) -> dict:
    return schema.load(request.args.to_dict())
