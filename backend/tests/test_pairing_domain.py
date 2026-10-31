from app.domain.pairing import next_round, pair_key


def everyone(round_):
    return [pid for court in round_.courts for pid in court.side_a + court.side_b]


def test_fills_courts_and_rests_the_rest():
    round_ = next_round(list(range(1, 11)), {}, {}, {}, courts=2)
    assert len(round_.courts) == 2
    assert len(round_.resting) == 2
    assert sorted(everyone(round_) + round_.resting) == list(range(1, 11))


def test_players_who_played_least_go_first():
    played = {1: 3, 2: 3, 3: 0, 4: 0, 5: 0, 6: 0}
    round_ = next_round([1, 2, 3, 4, 5, 6], {}, played, {}, courts=1)
    assert sorted(everyone(round_)) == [3, 4, 5, 6]
    assert round_.resting == [1, 2]


def test_rotate_avoids_repeat_partners():
    partnered = {pair_key(1, 2): 2, pair_key(3, 4): 2, pair_key(1, 3): 1, pair_key(2, 4): 1}
    court = next_round([1, 2, 3, 4], {}, {}, partnered, courts=1, mode="rotate").courts[0]
    assert {pair_key(*court.side_a), pair_key(*court.side_b)} == {pair_key(1, 4), pair_key(2, 3)}


def test_balanced_pairs_strongest_with_weakest():
    ratings = {1: 7.0, 2: 6.0, 3: 5.0, 4: 4.0}
    court = next_round([1, 2, 3, 4], ratings, {}, {}, courts=1, mode="balanced").courts[0]
    assert {pair_key(*court.side_a), pair_key(*court.side_b)} == {pair_key(1, 4), pair_key(2, 3)}


def test_not_enough_players_for_a_court():
    round_ = next_round([1, 2, 3], {}, {}, {}, courts=2)
    assert round_.courts == [] and round_.resting == [1, 2, 3]
