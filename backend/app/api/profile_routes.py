# backend/app/api/profile_routes.py
from flask import current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from marshmallow import ValidationError as MarshmallowValidationError

from ..schemas.profile_schemas import ProfileUpdateSchema, UserProfileResponseSchema
from ..services.profile_service import ProfileService
from ..tools.exceptions import AppException, UserAlreadyExistsError, UserNotFoundError
from . import api_bp  # 假設您的 Blueprint 叫做 api_bp

# 實例化 Schemas
profile_update_schema = ProfileUpdateSchema()
user_profile_response_schema = UserProfileResponseSchema()


@api_bp.route("/profile/me", methods=["GET"])
@jwt_required()
def get_my_profile():
    """獲取當前登入使用者的個人資料。"""
    current_user_id = get_jwt_identity()
    try:
        user = ProfileService.get_user_profile(int(current_user_id))
        # 使用 UserProfileResponseSchema 序列化包含 User 和 Member 資訊的完整回應
        return jsonify(user_profile_response_schema.dump(user)), 200
    except UserNotFoundError as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        current_app.logger.error(f"Error getting profile for user ID {current_user_id}: {e}", exc_info=True)
        return jsonify({"error": "server_error", "message": "獲取個人資料時發生錯誤。"}), 500


@api_bp.route("/profile/me", methods=["PUT"])
@jwt_required()
def update_my_profile():
    """更新當前登入使用者的個人資料。"""
    current_user_id = get_jwt_identity()
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "missing_json", "message": "缺少 JSON 請求內容。"}), 400

    try:
        # 1. 使用 Schema 驗證請求數據，partial=True 允許部分更新
        validated_data = profile_update_schema.load(json_data, partial=True)
    except MarshmallowValidationError as err:
        return jsonify({"error": "validation_error", "message": "輸入數據有誤。", "details": err.messages}), 400

    try:
        # 2. 調用服務層來執行更新
        updated_user = ProfileService.update_user_profile(int(current_user_id), validated_data)

        # 3. 序列化並返回更新後的完整個人資料
        return (
            jsonify({"message": "個人資料已成功更新！", "profile": user_profile_response_schema.dump(updated_user)}),
            200,
        )

    except (UserNotFoundError, UserAlreadyExistsError) as e:
        # 處理已知的業務邏輯錯誤
        current_app.logger.warning(f"Failed to update profile for user ID {current_user_id}: {e.message}")
        return jsonify(e.to_dict()), e.status_code
    except AppException as e:
        # 處理其他已知的應用程式錯誤
        current_app.logger.error(f"Error updating profile for user ID {current_user_id}: {e.message}", exc_info=False)
        return jsonify(e.to_dict()), e.status_code
    except Exception:
        # 處理未預期的伺服器錯誤
        current_app.logger.error(f"Unexpected error updating profile for user ID {current_user_id}", exc_info=True)
        return jsonify({"error": "server_error", "message": "更新個人資料時發生未預期的錯誤。"}), 500


@api_bp.route("/profile/me/matches", methods=["GET"])
@jwt_required()
def get_my_matches():
    """獲取當前用戶的比賽記錄"""
    current_user_id = get_jwt_identity()

    try:
        user = ProfileService.get_user_profile(int(current_user_id))
        if not user.member_profile:
            return jsonify({"error": "no_member_profile", "message": "用戶未關聯球員資料"}), 400

        # 獲取查詢參數
        limit = request.args.get('limit', 10, type=int)
        page = request.args.get('page', 1, type=int)

        # 使用 MatchRecordService 獲取該球員的比賽記錄
        query_params = {
            'player_id': user.member_profile.id,
            'limit': limit,
            'page': page,
            'sort_by': 'match_date',
            'sort_order': 'desc'
        }

        from ..schemas.match_schemas import MatchRecordResponseSchema
        from ..services.match_service import MatchRecordService

        result = MatchRecordService.get_all_match_records(query_params)
        responses_schema = MatchRecordResponseSchema(many=True)

        if isinstance(result, dict) and 'items' in result:
            matches_data = responses_schema.dump(result['items'])

            # 為每場比賽添加用戶相關的額外信息
            for match in matches_data:
                match['user_perspective'] = _get_user_match_perspective(match, user.member_profile.id)

            return jsonify({
                "matches": matches_data,
                "pagination": {
                    "total": result['total'],
                    "page": result['page'],
                    "per_page": result['per_page'],
                    "pages": result['pages']
                }
            }), 200
        else:
            matches_data = responses_schema.dump(result)
            for match in matches_data:
                match['user_perspective'] = _get_user_match_perspective(match, user.member_profile.id)

            return jsonify({"matches": matches_data}), 200

    except Exception as e:
        current_app.logger.error(f"獲取用戶比賽記錄失敗 for user ID {current_user_id}: {e}", exc_info=True)
        return jsonify({"error": "server_error", "message": "獲取比賽記錄時發生錯誤"}), 500


def _get_user_match_perspective(match_data, user_member_id):
    """為比賽記錄添加用戶視角的信息"""

    try:
        # 獲取比賽基本信息
        player1_id = match_data.get('player1_id')
        player2_id = match_data.get('player2_id')
        player3_id = match_data.get('player3_id')
        player4_id = match_data.get('player4_id')

        a_games = match_data.get('a_games', 0)
        b_games = match_data.get('b_games', 0)
        side_a_outcome = match_data.get('side_a_outcome')

        # 記錄調試信息
        current_app.logger.debug(f"處理比賽 {match_data.get('id')}:")
        current_app.logger.debug(f"  players: [{player1_id}, {player2_id}] vs [{player3_id}, {player4_id}]")
        current_app.logger.debug(f"  scores: A={a_games}, B={b_games}")
        current_app.logger.debug(f"  side_a_outcome: {side_a_outcome}")
        current_app.logger.debug(f"  user_id: {user_member_id}")

        # 判斷用戶在哪一方
        user_in_side_a = user_member_id in [player1_id, player2_id]
        user_in_side_b = user_member_id in [player3_id, player4_id]

        current_app.logger.debug(f"  user_in_side_a: {user_in_side_a}, user_in_side_b: {user_in_side_b}")

        if not (user_in_side_a or user_in_side_b):
            current_app.logger.warning(f"用戶 {user_member_id} 不在比賽 {match_data.get('id')} 中")
            return None

        # 根據用戶所在方計算結果
        if user_in_side_a:
            # 用戶在A方
            user_side = 'A'
            user_score = a_games
            opponent_score = b_games

            # A方勝利的條件
            if side_a_outcome == 'WIN':
                user_won = True
            elif side_a_outcome == 'LOSS':
                user_won = False
            else:
                # 如果side_a_outcome不是WIN/LOSS，根據分數判斷
                user_won = a_games > b_games
                current_app.logger.warning(f"side_a_outcome未知: {side_a_outcome}，使用分數判斷")

            # 獲取對手信息
            opponents = []
            if match_data.get('player3'):
                opponents.append(match_data.get('player3'))
            if match_data.get('player4'):
                opponents.append(match_data.get('player4'))

        else:  # user_in_side_b
            # 用戶在B方
            user_side = 'B'
            user_score = b_games
            opponent_score = a_games

            # B方勝利的條件（A方失敗）
            if side_a_outcome == 'LOSS':
                user_won = True
            elif side_a_outcome == 'WIN':
                user_won = False
            else:
                # 如果side_a_outcome不是WIN/LOSS，根據分數判斷
                user_won = b_games > a_games
                current_app.logger.warning(f"side_a_outcome未知: {side_a_outcome}，使用分數判斷")

            # 獲取對手信息
            opponents = []
            if match_data.get('player1'):
                opponents.append(match_data.get('player1'))
            if match_data.get('player2'):
                opponents.append(match_data.get('player2'))

        # 格式化對手名稱
        opponent_names = []
        for opponent in opponents:
            if opponent and isinstance(opponent, dict) and opponent.get('name'):
                opponent_names.append(opponent['name'])

        opponent_names_str = ' / '.join(opponent_names) if opponent_names else '對手'

        result = {
            'user_side': user_side,
            'is_winner': user_won,
            'user_score': user_score,
            'opponent_score': opponent_score,
            'score_display': f"{user_score} - {opponent_score}",
            'opponent_names': opponent_names_str,
            'match_result': '勝利' if user_won else '失敗'
        }

        current_app.logger.debug(f"  計算結果: {result}")
        return result

    except Exception as e:
        current_app.logger.error(f"計算用戶視角時發生錯誤: {e}", exc_info=True)
        return None
