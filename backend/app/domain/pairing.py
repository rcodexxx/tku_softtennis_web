"""練習日排組：從到場的人排出下一輪的雙打對戰。純函式，不碰資料庫。

做法參考常見的球會排組工具：
1. 打得最少（休息最多）的人先上場，人數不夠一面場地的就休息
2. 每四個人一組，從三種分邊方式裡挑成本最低的：
   - rotate（輪換）：盡量不要跟搭過的人再搭，其次兩邊實力接近
   - balanced（平均）：先讓兩邊實力接近，其次才避免重複搭檔
"""

import random
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field

MODES = ("rotate", "balanced")
# (同隊重複搭檔的成本權重, 兩邊分差的成本權重)
WEIGHTS = {"rotate": (10.0, 1.0), "balanced": (1.0, 10.0)}

Pair = tuple[int, int]


def pair_key(a: int, b: int) -> Pair:
    return (a, b) if a < b else (b, a)


@dataclass(frozen=True)
class Court:
    side_a: Pair
    side_b: Pair


@dataclass
class Round:
    courts: list[Court] = field(default_factory=list)
    resting: list[int] = field(default_factory=list)


def next_round(
    players: Sequence[int],
    ratings: Mapping[int, float],
    played: Mapping[int, int],
    partnered: Mapping[Pair, int],
    courts: int,
    mode: str = "rotate",
    seed: int = 0,
) -> Round:
    """排下一輪：played 是今天每人打過幾場，partnered 是今天每組搭過幾次。"""
    rng = random.Random(seed)
    order = list(players)
    rng.shuffle(order)
    # 打得少的先上；同樣場數的隨機（上面已經洗過牌）
    order.sort(key=lambda pid: played.get(pid, 0))
    playing_count = min(courts, len(order) // 4) * 4
    playing, resting = order[:playing_count], order[playing_count:]

    if mode == "balanced":
        # 實力相近的四個人一組，比賽才會接近
        playing.sort(key=lambda pid: -ratings.get(pid, 0.0))
    groups = [playing[i : i + 4] for i in range(0, len(playing), 4)]
    return Round([_best_split(group, ratings, partnered, mode) for group in groups], sorted(resting))


def _best_split(group: list[int], ratings: Mapping[int, float], partnered: Mapping[Pair, int], mode: str) -> Court:
    a, b, c, d = group
    repeat_weight, diff_weight = WEIGHTS[mode]

    def cost(court: Court) -> float:
        repeats = partnered.get(pair_key(*court.side_a), 0) + partnered.get(pair_key(*court.side_b), 0)
        diff = abs(_team(court.side_a, ratings) - _team(court.side_b, ratings))
        return repeat_weight * repeats + diff_weight * diff

    options = [Court((a, b), (c, d)), Court((a, c), (b, d)), Court((a, d), (b, c))]
    return min(options, key=cost)


def _team(pair: Pair, ratings: Mapping[int, float]) -> float:
    return sum(ratings.get(pid, 0.0) for pid in pair) / 2
