from flask_jwt_extended import create_access_token, create_refresh_token
from sqlalchemy import or_, select

from ..core.errors import AuthenticationError, ConflictError, ValidationError
from ..enums import UserRoleEnum
from ..extensions import db
from ..models import Member, User


def issue_tokens(user: User) -> dict:
    identity = str(user.id)
    return {
        "access_token": create_access_token(identity=identity),
        "refresh_token": create_refresh_token(identity=identity),
        "user": user,
    }


def register(phone_number: str) -> User:
    """以手機號碼快速註冊，初始密碼與手機號碼相同。"""
    if db.session.scalar(select(User).where(User.username == phone_number)):
        raise ConflictError(f"手機號碼 {phone_number} 已被註冊。")

    suffix = phone_number[-4:]
    user = User(username=phone_number, role=UserRoleEnum.MEMBER, display_name=f"用戶_{suffix}")
    user.set_password(phone_number)
    db.session.add_all([user, Member(user=user, name=f"隊員_{suffix}")])
    db.session.commit()
    return user


def authenticate(username: str, password: str) -> User:
    user = db.session.scalar(select(User).where(or_(User.username == username, User.email == username)))
    if user is None or not user.check_password(password):
        raise AuthenticationError("帳號或密碼錯誤。", code="invalid_credentials")
    if not user.is_active:
        raise AuthenticationError("此帳號已被停用。", code="user_inactive")
    return user


def change_password(user: User, old_password: str, new_password: str) -> None:
    if not user.check_password(old_password):
        raise AuthenticationError("舊密碼不正確。", code="incorrect_password")
    if old_password == new_password:
        raise ValidationError("新密碼不能與舊密碼相同。", details={"new_password": ["新密碼不能與舊密碼相同。"]})
    user.set_password(new_password)
    db.session.commit()
