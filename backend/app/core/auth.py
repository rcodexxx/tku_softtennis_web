"""認證與權限。

角色權限對應前端 usePermissions.js：
- STAFF（admin / coach / cadre）：管理會員、訪客、記錄與編輯比賽
- ADMIN：刪除會員、刪除比賽、管理組織
"""

from functools import wraps

from flask_jwt_extended import current_user, jwt_required

from ..enums import UserRoleEnum
from ..extensions import db, jwt
from ..models import User
from .errors import PermissionDeniedError, error_response

STAFF_ROLES = (UserRoleEnum.ADMIN, UserRoleEnum.COACH, UserRoleEnum.CADRE)
ADMIN_ROLES = (UserRoleEnum.ADMIN,)


def get_current_user() -> User:
    return current_user


def login_required(fn):
    return jwt_required()(fn)


def roles_required(*roles: UserRoleEnum):
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            if current_user.role not in roles:
                raise PermissionDeniedError()
            return fn(*args, **kwargs)

        return wrapper

    return decorator


staff_required = roles_required(*STAFF_ROLES)
admin_required = roles_required(*ADMIN_ROLES)


def is_staff(user: User) -> bool:
    return user.role in STAFF_ROLES


@jwt.user_lookup_loader
def _load_user(_jwt_header, jwt_data):
    user = db.session.get(User, int(jwt_data["sub"]))
    return user if user and user.is_active else None


@jwt.user_lookup_error_loader
def _user_lookup_error(_jwt_header, _jwt_data):
    return error_response(401, "user_inactive", "帳號不存在或已被停用。")


@jwt.expired_token_loader
def _expired_token(_jwt_header, _jwt_data):
    return error_response(401, "token_expired", "登入已過期，請重新登入。")


@jwt.invalid_token_loader
def _invalid_token(_reason):
    return error_response(401, "invalid_token", "認證 Token 無效。")


@jwt.unauthorized_loader
def _missing_token(_reason):
    return error_response(401, "unauthorized", "請先登入。")


@jwt.needs_fresh_token_loader
def _needs_fresh_token(_jwt_header, _jwt_data):
    return error_response(401, "fresh_token_required", "請重新登入後再試。")
