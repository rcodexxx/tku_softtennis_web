from flask import Blueprint
from flask_jwt_extended import create_access_token, jwt_required

from ..core.auth import get_current_user, login_required
from ..core.requests import load_json
from ..core.responses import created, ok
from ..schemas.auth import AuthUserSchema, ChangePasswordSchema, LoginSchema, RegisterSchema, TokenSchema
from ..services import auth_service

bp = Blueprint("auth", __name__, url_prefix="/auth")

token_schema = TokenSchema()
user_schema = AuthUserSchema()


@bp.post("/register")
def register():
    data = load_json(RegisterSchema())
    user = auth_service.register(data["phone_number"])
    return created(
        token_schema.dump(auth_service.issue_tokens(user)),
        message="註冊成功！初始密碼與手機號碼相同，請盡快修改密碼。",
    )


@bp.post("/login")
def login():
    data = load_json(LoginSchema())
    user = auth_service.authenticate(data["username"], data["password"])
    return ok(token_schema.dump(auth_service.issue_tokens(user)))


@bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    user = get_current_user()
    return ok({"access_token": create_access_token(identity=str(user.id))})


@bp.get("/me")
@login_required
def me():
    return ok(user_schema.dump(get_current_user()))


@bp.post("/change-password")
@login_required
def change_password():
    data = load_json(ChangePasswordSchema())
    auth_service.change_password(get_current_user(), data["old_password"], data["new_password"])
    return ok(message="密碼已更新。")
