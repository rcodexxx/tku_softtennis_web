"""應用程式錯誤與全域錯誤處理。

所有錯誤回應的格式統一為：
    {"error": {"code": "...", "message": "...", "details": {...}}}
"""

from flask import Flask, current_app, jsonify, request
from marshmallow import ValidationError as SchemaValidationError
from werkzeug.exceptions import HTTPException

from ..extensions import db


class AppError(Exception):
    status_code = 400
    code = "bad_request"
    message = "請求無效。"

    def __init__(self, message: str | None = None, *, code: str | None = None, details=None):
        super().__init__(message or self.message)
        self.message = message or self.message
        self.code = code or self.code
        self.details = details


class ValidationError(AppError):
    status_code = 400
    code = "validation_error"
    message = "輸入資料有誤。"


class AuthenticationError(AppError):
    status_code = 401
    code = "unauthorized"
    message = "請先登入。"


class PermissionDeniedError(AppError):
    status_code = 403
    code = "forbidden"
    message = "您沒有執行此操作的權限。"


class NotFoundError(AppError):
    status_code = 404
    code = "not_found"
    message = "找不到指定的資源。"


class ConflictError(AppError):
    status_code = 409
    code = "conflict"
    message = "資料與現有內容衝突。"


def error_response(status_code: int, code: str, message: str, details=None):
    body = {"code": code, "message": message}
    if details is not None:
        body["details"] = details
    return jsonify(error=body), status_code


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(AppError)
    def handle_app_error(error: AppError):
        db.session.rollback()
        return error_response(error.status_code, error.code, error.message, error.details)

    @app.errorhandler(SchemaValidationError)
    def handle_schema_error(error: SchemaValidationError):
        db.session.rollback()
        details = error.messages if isinstance(error.messages, dict) else {"_schema": error.messages}
        return error_response(400, ValidationError.code, ValidationError.message, details)

    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException):
        code = (error.name or "http_error").lower().replace(" ", "_")
        return error_response(error.code or 500, code, error.description or "請求無法處理。")

    @app.errorhandler(Exception)
    def handle_unexpected(error: Exception):
        db.session.rollback()
        current_app.logger.exception("Unhandled exception on %s %s", request.method, request.path)
        return error_response(500, "internal_error", "伺服器發生未預期的錯誤。")
