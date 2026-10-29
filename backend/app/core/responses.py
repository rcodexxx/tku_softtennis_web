"""成功回應的統一格式：

    {"data": ..., "meta": {...}, "message": "..."}

meta 與 message 只在有值時出現。
"""

from flask import jsonify


def ok(data=None, *, message: str | None = None, meta: dict | None = None, status: int = 200):
    body = {"data": data}
    if meta is not None:
        body["meta"] = meta
    if message is not None:
        body["message"] = message
    return jsonify(body), status


def created(data=None, *, message: str | None = None):
    return ok(data, message=message, status=201)
