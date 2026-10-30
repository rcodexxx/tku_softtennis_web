from flask import Blueprint

from ..core.auth import staff_required
from ..core.requests import load_json
from ..core.responses import created, ok
from ..schemas.board import BoardInputSchema, BoardSchema
from ..services import board_service

# 自訂榜單目前只給幹部用
bp = Blueprint("boards", __name__, url_prefix="/boards")

board_schema = BoardSchema()


@bp.get("")
@staff_required
def list_boards():
    return ok(board_schema.dump(board_service.list_boards(), many=True))


@bp.post("")
@staff_required
def create_board():
    board = board_service.create_board(load_json(BoardInputSchema()))
    return created(board_schema.dump(board), message="榜單已建立。")


@bp.put("/<int:board_id>")
@staff_required
def update_board(board_id: int):
    board = board_service.update_board(board_id, load_json(BoardInputSchema(), partial=True))
    return ok(board_schema.dump(board), message="榜單已更新。")


@bp.delete("/<int:board_id>")
@staff_required
def delete_board(board_id: int):
    board_service.delete_board(board_id)
    return ok(message="榜單已刪除。")
