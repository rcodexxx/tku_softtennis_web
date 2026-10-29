import click
from sqlalchemy import select

from ..enums import UserRoleEnum
from ..extensions import db
from ..models import Member, User
from ..schemas.auth import PASSWORD_MIN_LENGTH


@click.command("init-admin")
@click.option("--username", prompt="管理員帳號", help="登入帳號（手機號碼）")
@click.option("--email", prompt="管理員 Email（可留空）", default="", help="電子郵件")
@click.option("--name", prompt="管理員姓名", help="顯示名稱")
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True, help="密碼")
def init_admin(username: str, email: str, name: str, password: str):
    """建立管理員帳號；帳號已存在時改為升級成管理員並重設密碼。"""
    if len(password) < PASSWORD_MIN_LENGTH:
        raise click.ClickException(f"密碼長度至少需要 {PASSWORD_MIN_LENGTH} 個字元。")

    email = email or None
    if email and db.session.scalar(select(User).where(User.email == email, User.username != username)):
        raise click.ClickException(f"Email {email} 已被其他使用者使用。")

    user = db.session.scalar(select(User).where(User.username == username))
    if user:
        click.confirm(f"使用者 {username} 已存在，要將其設為管理員並重設密碼嗎？", abort=True)
    else:
        user = User(username=username)
        db.session.add_all([user, Member(user=user, name=name)])

    user.email = email
    user.display_name = name
    user.role = UserRoleEnum.ADMIN
    user.is_active = True
    user.set_password(password)
    db.session.commit()
    click.secho(f"管理員 {username} 已就緒。", fg="green")


@click.command("list-admins")
def list_admins():
    """列出所有管理員帳號。"""
    admins = db.session.scalars(select(User).where(User.role == UserRoleEnum.ADMIN).order_by(User.id)).all()
    if not admins:
        click.secho("沒有任何管理員帳號。", fg="yellow")
        return
    for admin in admins:
        status = click.style("啟用", fg="green") if admin.is_active else click.style("停用", fg="red")
        click.echo(
            f"{admin.id:>4}  {admin.username:<12} {admin.display_name or '':<12} {admin.email or '-':<24} {status}"
        )


@click.command("reset-admin-password")
@click.option("--username", prompt="管理員帳號")
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
def reset_admin_password(username: str, password: str):
    """重設管理員密碼。"""
    if len(password) < PASSWORD_MIN_LENGTH:
        raise click.ClickException(f"密碼長度至少需要 {PASSWORD_MIN_LENGTH} 個字元。")
    admin = db.session.scalar(select(User).where(User.username == username, User.role == UserRoleEnum.ADMIN))
    if admin is None:
        raise click.ClickException(f"找不到管理員帳號 {username}。")
    admin.set_password(password)
    db.session.commit()
    click.secho(f"管理員 {username} 的密碼已重設。", fg="green")
