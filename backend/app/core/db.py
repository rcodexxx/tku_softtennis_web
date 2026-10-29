from ..extensions import db
from .errors import NotFoundError


def get_or_404(model, ident, message: str | None = None):
    obj = db.session.get(model, ident)
    if obj is None:
        raise NotFoundError(message)
    return obj
