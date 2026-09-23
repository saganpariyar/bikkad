import pytest
from backend.engine.ladder_score import LadderScoreManager, get_partner, get_next_opponent


def test_ladder_regular_scoring():
    # Dealer P1 (Team A) at 0 points
    ladder = LadderScoreManager(initial_dealer='P1', initial_score=0)
    
    # Lead Team B wins 9 tricks
    delta, raw_score, note = ladder.calculate_round_result("Regular", {'Team A': 4, 'Team B': 9})
    assert delta == +9
    assert raw_score == 9

    next_dealer, starting_score, status = ladder.process_rotation(raw_score)
    assert next_dealer == 'P1'  # Burdened at 9, remains dealer
    assert starting_score == 9


def test_ladder_dealer_free_transition():
    # Dealer P1 (Team A) at 9 points
    ladder = LadderScoreManager(initial_dealer='P1', initial_score=9)
    
    # Dealer Team A wins 7 tricks (>= 5 met) -> -18 points!
    delta, raw_score, note = ladder.calculate_round_result("Regular", {'Team A': 7, 'Team B': 6})
    assert delta == -18
    assert raw_score == -9  # 9 - 18 = -9 <= 0 (FREE!)

    next_dealer, starting_score, status = ladder.process_rotation(raw_score)
    assert next_dealer == 'P2'  # Pass to OPPONENT P2!
    assert starting_score == 9


def test_ladder_52_cap_out_rollover():
    # Dealer P1 (Team A) at 45 points
    ladder = LadderScoreManager(initial_dealer='P1', initial_score=45)
    
    # Lead Team B wins 9 tricks -> +9 points!
    delta, raw_score, note = ladder.calculate_round_result("Regular", {'Team A': 4, 'Team B': 9})
    assert delta == +9
    assert raw_score == 54  # 45 + 9 = 54 >= 52 (BUST!)

    next_dealer, starting_score, status = ladder.process_rotation(raw_score)
    assert next_dealer == 'P3'  # Pass to PARTNER P3!
    assert starting_score == 2   # Remainder: 54 - 52 = 2 points!


def test_double_tera_fail_instant_bust():
    # Dealer P1 (Team A) at 27 points declares Double Tera and fails
    ladder = LadderScoreManager(initial_dealer='P1', initial_score=27)
    
    # Declarer P1 fails (Team B took tricks)
    delta, raw_score, note = ladder.calculate_round_result("Double Tera", {'Team A': 4, 'Team B': 9}, declarer_id='P1')
    assert delta == +52
    assert raw_score == 79  # 27 + 52 = 79 >= 52 (BUST!)

    next_dealer, starting_score, status = ladder.process_rotation(raw_score)
    assert next_dealer == 'P3'  # Pass to PARTNER P3!
    assert starting_score == 27  # Remainder: 79 - 52 = 27 points!


def test_ladder_dealer_at_0_wins_opponent_to_18():
    """
    User scenario: Dealer at 0 and wins -> -18 -> 0 - 18 = -18 -> opponent goes to 18!
    """
    ladder = LadderScoreManager(initial_dealer='P4', initial_score=0)
    # Dealer Team B (P4) wins 5 tricks (or 8 tricks) -> -18 points
    delta, raw_score, note = ladder.calculate_round_result("Regular", {'Team A': 5, 'Team B': 8})
    assert delta == -18
    assert raw_score == -18

    next_dealer, starting_score, status = ladder.process_rotation(raw_score)
    assert next_dealer == 'P1'  # Pass to OPPONENT P1!
    assert starting_score == 18  # Opponent goes to 18!


def test_ladder_dealer_at_18_wins_continues_at_0():
    """
    User rule: Deal cannot pass at 0 point. At 0 deal needs to continue.
    Only when score goes strictly less than 0 does it pass to opponent.
    Dealer at 18 and wins -> -18 -> 18 - 18 = 0 -> dealer continues at 0 points!
    """
    ladder = LadderScoreManager(initial_dealer='P1', initial_score=18)
    delta, raw_score, note = ladder.calculate_round_result("Regular", {'Team A': 5, 'Team B': 0})
    assert delta == -18
    assert raw_score == 0

    next_dealer, starting_score, status = ladder.process_rotation(raw_score)
    assert next_dealer == 'P1'  # Remains dealer! Deal does NOT pass at 0!
    assert starting_score == 0  # Continues dealing at 0 points!
    assert "continues as Dealer at 0 points" in status


def test_ladder_opponent_tera_loss_when_dealer_at_0():
    """
    User scenario: Team A has Tera and loses while Team B is dealer at 0.
    Dealer Team B gets -26 -> raw_score = -26 -> opponent goes directly to 26!
    """
    ladder = LadderScoreManager(initial_dealer='P4', initial_score=0)  # P4 is Team B
    # Declarer P1 (Team A) fails Tera
    delta, raw_score, note = ladder.calculate_round_result("Tera", {'Team A': 4, 'Team B': 1}, declarer_id='P1')
    assert delta == -26
    assert raw_score == -26

    next_dealer, starting_score, status = ladder.process_rotation(raw_score)
    assert next_dealer == 'P1'  # Pass to OPPONENT P1!
    assert starting_score == 26  # Opponent goes directly to 26!


def test_ladder_opponent_double_tera_loss_when_dealer_at_0():
    """
    Team A declares Double Tera and loses while Team B is dealer at 0.
    Dealer Team B gets -52 -> raw_score = -52 -> next dealer P1 gets 52 penalty (instant Coat)
    and passes to partner P3 at 0!
    """
    ladder = LadderScoreManager(initial_dealer='P4', initial_score=0)  # P4 is Team B
    delta, raw_score, note = ladder.calculate_round_result("Double Tera", {'Team A': 2, 'Team B': 1}, declarer_id='P1')
    assert delta == -52
    assert raw_score == -52

    next_dealer, starting_score, status = ladder.process_rotation(raw_score)
    assert next_dealer == 'P3'  # Instant coat on P1 passes to PARTNER P3!
    assert starting_score == 0
