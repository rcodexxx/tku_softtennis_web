from sqlalchemy import select

from ..core.db import get_or_404
from ..core.errors import ConflictError, NotFoundError
from ..extensions import db
from ..models import Board, Member


def list_boards() -> list[Board]:
    return list(db.session.scalars(select(Board).order_by(Board.id)))


def get_board(board_id: int) -> Board:
    return get_or_404(Board, board_id, "找不到指定的榜單。")


def create_board(data: dict) -> Board:
    board = Board(name=data["name"])
    _apply(board, data)
    db.session.add(board)
    db.session.commit()
    return board


def update_board(board_id: int, data: dict) -> Board:
    board = get_board(board_id)
    _apply(board, data)
    db.session.commit()
    return board


def delete_board(board_id: int) -> None:
    db.session.delete(get_board(board_id))
    db.session.commit()


def _apply(board: Board, data: dict) -> None:
    if "name" in data:
        taken = db.session.scalar(select(Board.id).where(Board.name == data["name"], Board.id != board.id))
        if taken:
            raise ConflictError(f"榜單「{data['name']}」已存在。")
        board.name = data["name"]
    if "member_ids" in data:
        ids = set(data["member_ids"])
        members = list(db.session.scalars(select(Member).where(Member.id.in_(ids))))
        if len(members) != len(ids):
            raise NotFoundError("有球員不存在。")
        board.members = members
