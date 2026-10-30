import pytest

from app.domain import rating
from app.enums import GenderEnum


def test_starting_rating_depends_on_gender():
    assert rating.starting_rating(GenderEnum.MALE) == 5.0
    assert rating.starting_rating(GenderEnum.FEMALE) == 4.0
    assert rating.starting_rating(None) == rating.DEFAULT_STARTING_RATING


def test_a_division_starts_like_one_gender_step_higher():
    assert rating.starting_rating(GenderEnum.MALE, a_division=True) == 6.0
    assert rating.starting_rating(GenderEnum.FEMALE, a_division=True) == 5.0


def test_one_point_gap_expects_seventy_percent_of_games():
    assert rating.expected_share(6.0, 5.0) == pytest.approx(0.7)
    assert rating.expected_share(5.0, 5.0) == pytest.approx(0.5)
    assert rating.expected_share(5.0, 6.0) == pytest.approx(0.3)


def test_swing_follows_games_not_just_winner():
    assert rating.swing(5.0, 5.0, 4, 0) > rating.swing(5.0, 5.0, 4, 3) > 0
    assert rating.swing(5.0, 5.0, 3, 4) == pytest.approx(-rating.swing(5.0, 5.0, 4, 3))


def test_close_loss_to_much_stronger_team_still_gains():
    assert rating.swing(4.0, 5.5, 3, 4) > 0


def test_swing_is_capped():
    assert rating.swing(1.0, 9.0, 5, 0) == rating.MAX_SWING
    assert rating.swing(9.0, 1.0, 0, 5) == -rating.MAX_SWING


def test_rating_is_weighted_towards_recent_matches():
    assert rating.rating_from([], 5.0) == 5.0
    improving = rating.rating_from([4.0, 6.0], 5.0)
    declining = rating.rating_from([6.0, 4.0], 5.0)
    assert improving > 5.0 > declining


def test_rating_only_uses_window_and_stays_in_range():
    old = [1.0] * 30
    assert rating.rating_from(old + [8.0] * rating.WINDOW, 8.0) == pytest.approx(8.0)
    assert rating.rating_from([10.0] * 5, 10.0) == rating.MAX_RATING
