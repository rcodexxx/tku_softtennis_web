"""TrueSkill 評分計算（純函式，不碰資料庫）。

一場比賽的評分更新流程：
1. 依局數差距調整 beta：比分越懸殊，評分變動越大
2. 用 TrueSkill 計算兩隊的新評分
3. 場上有女生時套用性別調整
"""

import math
from dataclasses import dataclass

import trueskill

from ..enums import GenderEnum

DEFAULT_MU = 25.0
DEFAULT_SIGMA = 25.0 / 3

# 四維度評分參數
CONSERVATIVE_K = 2.0
MAX_SIGMA = 8.33
MIN_SIGMA = 1.0

# 性別調整參數
FEMALE_WIN_BONUS = 0.6  # 女生贏男生：額外加分
MALE_WIN_REDUCTION = 0.3  # 男生贏有女生的隊伍：加分減少比例
MALE_LOSS_PENALTY = 0.4  # 男生輸給有女生的隊伍：額外扣分
FEMALE_LOSS_MITIGATION = 0.5  # 女生輸給男生：扣分減輕比例
MIXED_TEAM_MALE_LOSS_MITIGATION = 0.3  # 男生與女隊友一起輸球：扣分減輕比例

# (等級, sigma 下限) 由低經驗到高經驗；sigma 越小代表經驗越多
EXPERIENCE_LEVELS = [("新手", 7.0), ("初級", 5.0), ("中級", 3.0), ("高級", 2.0), ("資深", 0.0)]

_BASE_ENV = trueskill.TrueSkill(mu=DEFAULT_MU, sigma=DEFAULT_SIGMA, draw_probability=0)


@dataclass(frozen=True)
class Rating:
    mu: float = DEFAULT_MU
    sigma: float = DEFAULT_SIGMA


@dataclass(frozen=True)
class Participant:
    id: int
    rating: Rating
    gender: GenderEnum | None = None


def rate_match(
    side_a: list[Participant], side_b: list[Participant], a_games: int, b_games: int, side_a_won: bool
) -> dict[int, Rating]:
    """回傳這場比賽所有參賽者的新評分。"""
    env = trueskill.TrueSkill(
        mu=_BASE_ENV.mu,
        sigma=_BASE_ENV.sigma,
        beta=_dynamic_beta(a_games, b_games),
        tau=_BASE_ENV.tau,
        draw_probability=0,
    )
    team_a = {p.id: env.create_rating(mu=p.rating.mu, sigma=p.rating.sigma) for p in side_a}
    team_b = {p.id: env.create_rating(mu=p.rating.mu, sigma=p.rating.sigma) for p in side_b}
    new_a, new_b = env.rate([team_a, team_b], ranks=[0, 1] if side_a_won else [1, 0])

    mu = {pid: r.mu for pid, r in {**new_a, **new_b}.items()}
    sigma = {pid: r.sigma for pid, r in {**new_a, **new_b}.items()}

    winners, losers = (side_a, side_b) if side_a_won else (side_b, side_a)
    _apply_gender_adjustments(mu, winners, losers)
    return {pid: Rating(mu[pid], sigma[pid]) for pid in mu}


def _dynamic_beta(a_games: int, b_games: int) -> float:
    total = a_games + b_games
    if total == 0:
        return _BASE_ENV.beta
    margin = abs(a_games - b_games) / total
    return _BASE_ENV.beta * (1 - margin * 0.5)


_GAINS, _LOSSES = 1, -1


def _apply_gender_adjustments(mu: dict[int, float], winners: list[Participant], losers: list[Participant]) -> None:
    """依序套用性別調整；每一步都以前一步的結果為基礎，與既有資料的計算方式一致。"""
    winning_females, winning_males = _of_gender(winners, GenderEnum.FEMALE), _of_gender(winners, GenderEnum.MALE)
    losing_females, losing_males = _of_gender(losers, GenderEnum.FEMALE), _of_gender(losers, GenderEnum.MALE)
    if not (winning_females or losing_females):
        return

    if winning_females and losing_males:
        _add(mu, winning_females, FEMALE_WIN_BONUS)
    if winning_males and losing_females:
        _shrink(mu, winning_males, MALE_WIN_REDUCTION, _GAINS)
    if losing_males and winning_females:
        _add(mu, losing_males, -MALE_LOSS_PENALTY)
    if losing_females and winning_males:
        _shrink(mu, losing_females, FEMALE_LOSS_MITIGATION, _LOSSES)
    if losing_females and losing_males:
        # 這裡的扣分包含上一步的 MALE_LOSS_PENALTY
        _shrink(mu, losing_males, MIXED_TEAM_MALE_LOSS_MITIGATION, _LOSSES)


def _of_gender(team: list[Participant], gender: GenderEnum) -> list[Participant]:
    return [p for p in team if p.gender == gender]


def _add(mu: dict[int, float], players: list[Participant], amount: float) -> None:
    for p in players:
        mu[p.id] += amount


def _shrink(mu: dict[int, float], players: list[Participant], factor: float, direction: int) -> None:
    """把加分 (_GAINS) 或扣分 (_LOSSES) 縮小 factor 比例。"""
    for p in players:
        change = mu[p.id] - p.rating.mu
        if change * direction > 0:
            mu[p.id] -= change * factor


# ===== 四維度評分 =====


def conservative_score(rating: Rating) -> float:
    """官方排名分數：mu - k * sigma。"""
    return rating.mu - CONSERVATIVE_K * rating.sigma


def consistency_rating(rating: Rating) -> int:
    """穩定度（0-100），sigma 越小越穩定。"""
    if rating.sigma >= MAX_SIGMA:
        return 0
    if rating.sigma <= MIN_SIGMA:
        return 100
    return int(100 * (MAX_SIGMA - rating.sigma) / (MAX_SIGMA - MIN_SIGMA))


def rating_confidence(rating: Rating) -> int:
    """評分可信度（0-100）。"""
    if rating.sigma >= MAX_SIGMA:
        return 0
    return int(max(0, min(100, (1 - rating.sigma / MAX_SIGMA) * 100)))


def experience_level(rating: Rating) -> str:
    for level, min_sigma in EXPERIENCE_LEVELS:
        if rating.sigma >= min_sigma:
            return level
    return EXPERIENCE_LEVELS[-1][0]


def experience_sigma_range(level: str) -> tuple[float, float]:
    """回傳某經驗等級的 sigma 範圍 [low, high)。"""
    upper = math.inf
    for name, min_sigma in EXPERIENCE_LEVELS:
        if name == level:
            return min_sigma, upper
        upper = min_sigma
    raise ValueError(f"unknown experience level: {level}")


def is_experienced(rating: Rating) -> bool:
    return rating.sigma < MAX_SIGMA * 0.6


def win_probability(a: Rating, b: Rating) -> float:
    """a 擊敗 b 的預測機率。"""
    denominator = math.sqrt(2 * _BASE_ENV.beta**2 + a.sigma**2 + b.sigma**2)
    return _BASE_ENV.cdf((a.mu - b.mu) / denominator)
