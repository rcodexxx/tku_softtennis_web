from marshmallow import ValidationError, fields, validate, validates_schema

from ..domain import scoring
from ..enums import (
    CourtEnvironmentEnum,
    CourtSurfaceEnum,
    MatchFormatEnum,
    MatchOutcomeEnum,
    MatchStartServeEnum,
    MatchTimeSlotEnum,
    MatchTypeEnum,
)
from ..models.match_record import MAX_GAMES
from .common import BaseSchema, EnumField, InputSchema, PageQuerySchema
from .member import PlayerBriefSchema


class GameScoreSchema(InputSchema):
    a_score = fields.Int(required=True, validate=validate.Range(min=0))
    b_score = fields.Int(required=True, validate=validate.Range(min=0))


class MatchRecordInputSchema(InputSchema):
    match_date = fields.Date(required=True)
    match_type = EnumField(MatchTypeEnum, required=True)
    match_format = EnumField(MatchFormatEnum, required=True)

    player1_id = fields.Int(required=True, validate=validate.Range(min=1))
    player2_id = fields.Int(allow_none=True, validate=validate.Range(min=1))
    player3_id = fields.Int(required=True, validate=validate.Range(min=1))
    player4_id = fields.Int(allow_none=True, validate=validate.Range(min=1))

    # 只給總局數，或給每局比分（此時總局數由比分計算）
    a_games = fields.Int(validate=validate.Range(min=0))
    b_games = fields.Int(validate=validate.Range(min=0))
    games = fields.List(fields.Nested(GameScoreSchema), validate=validate.Length(max=MAX_GAMES))
    first_serve_side = EnumField(MatchStartServeEnum, allow_none=True)

    time_slot = EnumField(MatchTimeSlotEnum, allow_none=True)
    court_surface = EnumField(CourtSurfaceEnum, allow_none=True)
    court_environment = EnumField(CourtEnvironmentEnum, allow_none=True)
    total_points = fields.Int(allow_none=True, validate=validate.Range(min=0))
    duration_minutes = fields.Int(allow_none=True, validate=validate.Range(min=1, max=600))
    youtube_url = fields.Url(allow_none=True)
    notes = fields.Str(allow_none=True, validate=validate.Length(max=500))

    @validates_schema
    def validate_record(self, data, partial=False, **kwargs):
        # 部分更新時，完整性檢查交給 service（需要合併既有資料）
        if partial:
            return
        validate_players(data)
        validate_scores(data)


def validate_players(data: dict) -> None:
    ids = [data.get(f"player{n}_id") for n in range(1, 5)]
    chosen = [pid for pid in ids if pid]
    if len(chosen) != len(set(chosen)):
        raise ValidationError("同一位球員不能重複出現在比賽中。")
    if data.get("match_type") == MatchTypeEnum.SINGLES:
        if ids[1] or ids[3]:
            raise ValidationError("單打只能選擇 2 位球員。")
    elif data.get("match_type") is not None and not all(ids):
        raise ValidationError("雙打必須選擇 4 位球員。")


def validate_scores(data: dict) -> None:
    games = data.get("games")
    if games and scoring.has_detailed_scores([(g["a_score"], g["b_score"]) for g in games]):
        a_won, b_won = scoring.games_won([(g["a_score"], g["b_score"]) for g in games])
        for key, computed in (("a_games", a_won), ("b_games", b_won)):
            if data.get(key) is not None and data[key] != computed:
                raise ValidationError(f"總局數 {data[key]} 與每局比分計算結果 {computed} 不一致。", field_name=key)
    elif data.get("a_games") is None or data.get("b_games") is None:
        raise ValidationError("請提供總局數或每局比分。")


class MatchRecordSchema(BaseSchema):
    id = fields.Int()
    match_id = fields.Int()
    match_date = fields.Date(attribute="match.match_date")
    match_type = EnumField(MatchTypeEnum, attribute="match.match_type")
    match_format = EnumField(MatchFormatEnum, attribute="match.match_format")
    time_slot = EnumField(MatchTimeSlotEnum, attribute="match.match_time_slot", allow_none=True)
    court_surface = EnumField(CourtSurfaceEnum, attribute="match.court_surface", allow_none=True)
    court_environment = EnumField(CourtEnvironmentEnum, attribute="match.court_environment", allow_none=True)
    total_points = fields.Int(attribute="match.total_points", allow_none=True)
    duration_minutes = fields.Int(attribute="match.duration_minutes", allow_none=True)
    youtube_url = fields.Str(attribute="match.youtube_url", allow_none=True)
    notes = fields.Str(attribute="match.notes", allow_none=True)

    player1_id = fields.Int()
    player2_id = fields.Int(allow_none=True)
    player3_id = fields.Int()
    player4_id = fields.Int(allow_none=True)
    player1 = fields.Nested(PlayerBriefSchema)
    player2 = fields.Nested(PlayerBriefSchema, allow_none=True)
    player3 = fields.Nested(PlayerBriefSchema)
    player4 = fields.Nested(PlayerBriefSchema, allow_none=True)

    a_games = fields.Int()
    b_games = fields.Int()
    side_a_outcome = EnumField(MatchOutcomeEnum)
    first_serve_side = EnumField(MatchStartServeEnum, allow_none=True)
    has_detailed_scores = fields.Function(lambda r: scoring.has_detailed_scores(r.game_scores))
    games = fields.Function(lambda r: scoring.games_detail(r.game_scores, r.first_serve_side))
    serve_advantage = fields.Function(lambda r: scoring.serve_advantage(r.game_scores, r.first_serve_side))


class MatchQuerySchema(PageQuerySchema):
    sort_by = fields.Str(load_default="match_date", validate=validate.OneOf(["match_date", "total_games", "id"]))
    start_date = fields.Date()
    end_date = fields.Date()
    match_type = EnumField(MatchTypeEnum)
    match_format = EnumField(MatchFormatEnum)
    player_id = fields.Int(validate=validate.Range(min=1))
