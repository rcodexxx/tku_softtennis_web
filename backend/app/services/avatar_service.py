"""球員頭像：本人或幹部以上可以上傳、刪除。檔案存在 UPLOAD_FOLDER/avatars。"""

import uuid
from pathlib import Path

from flask import current_app
from werkzeug.datastructures import FileStorage

from ..core.auth import is_staff
from ..core.errors import PermissionDeniedError, ValidationError
from ..extensions import db
from ..models import Member, User
from . import member_service

MAX_BYTES = 3 * 1024 * 1024
# 以檔頭判斷實際格式，不信任副檔名與 Content-Type
SIGNATURES = {
    b"\xff\xd8\xff": "jpg",
    b"\x89PNG\r\n\x1a\n": "png",
    b"GIF87a": "gif",
    b"GIF89a": "gif",
}


def avatar_dir() -> Path:
    return Path(current_app.config["UPLOAD_FOLDER"]) / "avatars"


def avatar_url(filename: str | None) -> str | None:
    return f"/api/uploads/avatars/{filename}" if filename else None


def save_avatar(actor: User, member_id: int, file: FileStorage | None) -> Member:
    member = _get_editable_member(actor, member_id)
    if file is None or not file.filename:
        raise ValidationError("請選擇要上傳的圖片。", details={"file": ["請選擇要上傳的圖片。"]})

    content = file.read(MAX_BYTES + 1)
    if len(content) > MAX_BYTES:
        raise ValidationError("圖片不能超過 3MB。", details={"file": ["圖片不能超過 3MB。"]})
    extension = _detect_format(content)
    if extension is None:
        raise ValidationError(
            "只接受 JPG、PNG、WebP 或 GIF 圖片。", details={"file": ["只接受 JPG、PNG、WebP 或 GIF 圖片。"]}
        )

    directory = avatar_dir()
    directory.mkdir(parents=True, exist_ok=True)
    filename = f"{member.id}-{uuid.uuid4().hex[:12]}.{extension}"
    (directory / filename).write_bytes(content)

    old = member.avatar_filename
    member.avatar_filename = filename
    db.session.commit()
    delete_file(old)
    return member


def remove_avatar(actor: User, member_id: int) -> Member:
    member = _get_editable_member(actor, member_id)
    old = member.avatar_filename
    member.avatar_filename = None
    db.session.commit()
    delete_file(old)
    return member


def delete_file(filename: str | None) -> None:
    if filename:
        (avatar_dir() / filename).unlink(missing_ok=True)


def _get_editable_member(actor: User, member_id: int) -> Member:
    member = member_service.get_member(member_id)
    if member.user_id != actor.id and not is_staff(actor):
        raise PermissionDeniedError("只能修改自己的頭像。")
    return member


def _detect_format(content: bytes) -> str | None:
    if content[:4] == b"RIFF" and content[8:12] == b"WEBP":
        return "webp"
    return next((ext for signature, ext in SIGNATURES.items() if content.startswith(signature)), None)
