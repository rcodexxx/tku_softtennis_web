"""每局比分與發球的計算（純函式）。

發球規則：第一局由 first_serve 方發球，之後每局輪替。
"""

from ..enums import MatchStartServeEnum

GameScores = list[tuple[int, int]]


def played_games(scores: GameScores) -> list[tuple[int, int, int]]:
    """回傳有比分的局：(局數, A 方得分, B 方得分)。"""
    return [(n, a, b) for n, (a, b) in enumerate(scores, start=1) if a > 0 or b > 0]


def has_detailed_scores(scores: GameScores) -> bool:
    return bool(played_games(scores))


def games_won(scores: GameScores) -> tuple[int, int]:
    a_won = sum(1 for _, a, b in played_games(scores) if a > b)
    b_won = sum(1 for _, a, b in played_games(scores) if b > a)
    return a_won, b_won


def game_winner(a_score: int, b_score: int) -> str | None:
    if a_score > b_score:
        return "A"
    if b_score > a_score:
        return "B"
    return None


def serve_side_for_game(first_serve: MatchStartServeEnum | None, game: int) -> MatchStartServeEnum | None:
    if first_serve is None:
        return None
    return first_serve if game % 2 == 1 else first_serve.other


def games_detail(scores: GameScores, first_serve: MatchStartServeEnum | None) -> list[dict]:
    details = []
    for game, a_score, b_score in played_games(scores):
        winner = game_winner(a_score, b_score)
        serve_side = serve_side_for_game(first_serve, game)
        details.append(
            {
                "game": game,
                "a_score": a_score,
                "b_score": b_score,
                "winner": winner,
                "serve_side": serve_side.value if serve_side else None,
            }
        )
    return details


def serve_advantage(scores: GameScores, first_serve: MatchStartServeEnum | None) -> dict | None:
    """各方發球局的勝率。"""
    if first_serve is None:
        return None
    stats = {side.value: {"serve_games": 0, "serve_wins": 0, "serve_win_rate": 0.0} for side in MatchStartServeEnum}
    for detail in games_detail(scores, first_serve):
        if detail["winner"] is None:
            continue
        side = stats[detail["serve_side"]]
        side["serve_games"] += 1
        server_letter = "A" if detail["serve_side"] == MatchStartServeEnum.SIDE_A else "B"
        if detail["winner"] == server_letter:
            side["serve_wins"] += 1
    for side in stats.values():
        if side["serve_games"]:
            side["serve_win_rate"] = round(side["serve_wins"] / side["serve_games"] * 100, 1)
    return stats
