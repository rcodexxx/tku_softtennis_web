from sqlalchemy import exists, or_

from ..models import MatchRecord


def involves_player(player_id):
    return or_(*(getattr(MatchRecord, f"player{n}_id") == player_id for n in range(1, 5)))


def involves_any_player(player_ids):
    return or_(*(getattr(MatchRecord, f"player{n}_id").in_(player_ids) for n in range(1, 5)))


def has_match_records(player_id):
    return exists().where(involves_player(player_id))
