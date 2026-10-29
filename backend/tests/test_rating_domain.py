import pytest

from app.domain import rating
from app.domain.rating import Participant, Rating, rate_match
from app.enums import GenderEnum

MALE, FEMALE = GenderEnum.MALE, GenderEnum.FEMALE


def team(*specs):
    return [Participant(pid, Rating(), gender) for pid, gender in specs]


def test_winner_gains_and_loser_drops():
    result = rate_match(team((1, None)), team((2, None)), 4, 2, side_a_won=True)
    assert result[1].mu > rating.DEFAULT_MU > result[2].mu
    assert result[1].sigma < rating.DEFAULT_SIGMA


def test_bigger_margin_moves_ratings_more():
    close = rate_match(team((1, None)), team((2, None)), 4, 3, side_a_won=True)
    blowout = rate_match(team((1, None)), team((2, None)), 4, 0, side_a_won=True)
    assert blowout[1].mu - rating.DEFAULT_MU > close[1].mu - rating.DEFAULT_MU


def test_female_beating_male_gets_bonus():
    plain = rate_match(team((1, None)), team((2, None)), 4, 2, side_a_won=True)
    gendered = rate_match(team((1, FEMALE)), team((2, MALE)), 4, 2, side_a_won=True)
    assert gendered[1].mu == pytest.approx(plain[1].mu + rating.FEMALE_WIN_BONUS)
    # 男生輸給女生：先額外扣分
    assert gendered[2].mu == pytest.approx(plain[2].mu - rating.MALE_LOSS_PENALTY)


def test_female_losing_to_male_is_mitigated():
    plain = rate_match(team((1, None)), team((2, None)), 4, 2, side_a_won=True)
    gendered = rate_match(team((1, MALE)), team((2, FEMALE)), 4, 2, side_a_won=True)
    plain_loss = rating.DEFAULT_MU - plain[2].mu
    assert rating.DEFAULT_MU - gendered[2].mu == pytest.approx(plain_loss * (1 - rating.FEMALE_LOSS_MITIGATION))
    plain_gain = plain[1].mu - rating.DEFAULT_MU
    assert gendered[1].mu - rating.DEFAULT_MU == pytest.approx(plain_gain * (1 - rating.MALE_WIN_REDUCTION))


def test_no_women_no_adjustment():
    plain = rate_match(team((1, None)), team((2, None)), 4, 2, side_a_won=True)
    males = rate_match(team((1, MALE)), team((2, MALE)), 4, 2, side_a_won=True)
    assert males[1] == plain[1] and males[2] == plain[2]


@pytest.mark.parametrize(
    ("sigma", "level"), [(8.0, "新手"), (7.0, "新手"), (6.0, "初級"), (4.0, "中級"), (2.5, "高級"), (1.0, "資深")]
)
def test_experience_level(sigma, level):
    assert rating.experience_level(Rating(25, sigma)) == level
    low, high = rating.experience_sigma_range(level)
    assert low <= sigma < high


def test_dimension_bounds():
    assert rating.consistency_rating(Rating(25, 9)) == 0
    assert rating.consistency_rating(Rating(25, 0.5)) == 100
    assert rating.rating_confidence(Rating(25, rating.MAX_SIGMA)) == 0
    assert rating.conservative_score(Rating(30, 2)) == 26


def test_win_probability_is_symmetric():
    a, b = Rating(30, 3), Rating(25, 3)
    assert rating.win_probability(a, b) > 0.5
    assert rating.win_probability(a, b) + rating.win_probability(b, a) == pytest.approx(1)
