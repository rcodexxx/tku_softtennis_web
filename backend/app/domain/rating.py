"""球員分數（類似 UTR，尺度 1–10）的計算，純函式，不碰資料庫。

一場比賽：
1. 隊伍分數 = 隊員賽前分數的平均
2. 依兩隊分差算出預期局數比例：差 1 分時，強隊預期拿 7 成局數
3. 實際局數比例和預期比較，換算成「這場比預期好幾分」（單場最多 ±1.5）
4. 每位球員的本場表現 = 自己的賽前分數 + 隊伍比預期好的分數（同隊兩人一樣）

個人分數 = 最近 20 場本場表現的加權平均（越新越重），再加上一筆起始分數當作 3 場的份量，
讓剛開始打的人分數不會大起大落。只看局數比例，所以輸給強隊但比分接近也會加分。
"""

import math
from collections.abc import Sequence

from ..enums import GenderEnum

MIN_RATING = 1.0
MAX_RATING = 10.0

# 起始分數：男女實力差距大，女生從比較低的分數開始，對戰男生時的預期才合理
STARTING_RATINGS = {GenderEnum.MALE: 5.0, GenderEnum.FEMALE: 4.0}
DEFAULT_STARTING_RATING = 4.5
STARTING_WEIGHT = 3.0

# 差 1 分 → 強隊預期拿 70% 的局數
SCALE = 1 / math.log(0.7 / 0.3)
MAX_SWING = 1.5
WINDOW = 20
# 少於這個場數的分數還不穩定，顯示為「評估中」
RATED_MATCHES = 5


def starting_rating(gender: GenderEnum | None) -> float:
    return STARTING_RATINGS.get(gender, DEFAULT_STARTING_RATING)


def team_rating(ratings: Sequence[float]) -> float:
    return sum(ratings) / len(ratings)


def expected_share(rating: float, opponent_rating: float) -> float:
    """分數 rating 的一方預期拿下的局數比例。"""
    return 1 / (1 + math.exp(-(rating - opponent_rating) / SCALE))


def swing(rating: float, opponent_rating: float, games_won: int, games_lost: int) -> float:
    """這場比預期好幾分（負數代表比預期差）。

    局數比例各加 0.5 局，避免 4-0 這種比分變成無限大；比賽打越多局，比例越可信。
    """
    actual = (games_won + 0.5) / (games_won + games_lost + 1)
    expected = expected_share(rating, opponent_rating)
    value = SCALE * (_logit(actual) - _logit(expected))
    return max(-MAX_SWING, min(MAX_SWING, value))


def rating_from(performances: Sequence[float], start: float) -> float:
    """由本場表現（舊到新）算出個人分數。"""
    recent = list(reversed(performances[-WINDOW:]))
    weights = [1 - index / (2 * WINDOW) for index in range(len(recent))]
    total = sum(p * w for p, w in zip(recent, weights, strict=True)) + start * STARTING_WEIGHT
    return clamp(total / (sum(weights) + STARTING_WEIGHT))


def clamp(value: float) -> float:
    return max(MIN_RATING, min(MAX_RATING, value))


def _logit(p: float) -> float:
    return math.log(p / (1 - p))
