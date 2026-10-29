from flask import Blueprint, send_from_directory

from ..services.avatar_service import avatar_dir

bp = Blueprint("uploads", __name__, url_prefix="/uploads")


@bp.get("/avatars/<path:filename>")
def avatar(filename: str):
    # send_from_directory 會拒絕跳出目錄的路徑
    return send_from_directory(avatar_dir(), filename, max_age=60 * 60 * 24 * 30)
