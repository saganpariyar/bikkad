import pytest
from backend.engine.card import Card, Suit
from backend.engine.game_session import GameSession


def test_early_win_regular_dealer_5_tricks():
    """
    Scenario from user: Dealer (Team B) needs only 5 tricks.
    At Trick 8, Team B wins its 2nd consecutive trick -> collects 8 cards (2 tricks)
    to reach 6 tricks (24 cards) >= 5 -> Early Win triggered immediately!
    """
    session = GameSession(initial_dealer='P4', initial_score=0)  # P4 is Team B
    session.start_new_round(mode="Regular")
    session.resolve_bidding()
    if session.deal_stage == "SELECT_TRUMP":
        session.select_hidden_trump(session.hands[session.eldest_hand][0].code)

    # Team B previously collected 16 cards (4 tricks), Team A 8 cards (2 tricks)
    session.pot_manager.team_cards_collected['Team B'] = 16
    session.pot_manager.team_tricks_won['Team B'] = 4
    session.pot_manager.team_cards_collected['Team A'] = 8
    session.pot_manager.team_tricks_won['Team A'] = 2
    session.trick_number = 8
    # Trick 7 was won by Team B (streak 1), so pot has 4 cards
    session.pot_manager.pot_cards = [Card.from_code("2C"), Card.from_code("3C"), Card.from_code("4C"), Card.from_code("5C")]
    session.pot_manager.pot_tricks_count = 1
    session.pot_manager.last_winner_player_id = 'P2'
    session.pot_manager.last_winner_team = 'Team B'
    session.pot_manager.streak_count = 1

    # Play trick 8 where Team B (P2) wins (2nd consecutive win!)
    session.current_turn_player = 'P1'
    session.hands['P1'] = [Card.from_code("2H")]
    session.hands['P2'] = [Card.from_code("AH")]
    session.hands['P3'] = [Card.from_code("3H")]
    session.hands['P4'] = [Card.from_code("4H")]

    session.play_card('P1', '2H')
    session.play_card('P2', 'AH')
    session.play_card('P3', '3H')
    session.play_card('P4', '4H')

    # Round must end immediately at trick 8!
    assert session.round_complete is True
    assert session.trick_number == 8
    assert session.pot_manager.team_tricks_won['Team B'] == 6
    assert session.pot_manager.team_cards_collected['Team B'] == 24
    assert any("EARLY WIN: Dealer Team B clinched deal with 6 tricks at Trick 08" in log for log in session.current_round_logs)

    # Ladder score: Dealer Team B was at 0 and won -> raw score = 0 - 18 = -18
    # Next dealer is Opponent (Team A, P1) starting at 18!
    assert session.ladder_manager.dealer_id == 'P1'
    assert session.ladder_manager.dealer_score == 18


def test_early_win_regular_lead_9_tricks():
    """
    Lead team needs 9 tricks to win.
    When Lead team (Team B) collects pot to reach >= 9 tricks, deal clinches immediately.
    """
    session = GameSession(initial_dealer='P1', initial_score=0)  # P1 is Team A dealer -> Team B is lead
    session.start_new_round(mode="Regular")
    if session.deal_stage == "SELECT_TRUMP":
        session.select_hidden_trump(session.hands[session.eldest_hand][0].code)

    session.pot_manager.team_cards_collected['Team B'] = 32
    session.pot_manager.team_tricks_won['Team B'] = 8
    session.pot_manager.team_cards_collected['Team A'] = 4
    session.pot_manager.team_tricks_won['Team A'] = 1
    session.trick_number = 10
    session.pot_manager.pot_cards = [Card.from_code("2C"), Card.from_code("3C"), Card.from_code("4C"), Card.from_code("5C")]
    session.pot_manager.pot_tricks_count = 1
    session.pot_manager.last_winner_player_id = 'P2'
    session.pot_manager.last_winner_team = 'Team B'
    session.pot_manager.streak_count = 1

    # Team B wins trick 10 (2nd consecutive win -> scoops 8 cards = 2 tricks -> 10 tricks >= 9)
    session.current_turn_player = 'P1'
    session.hands['P1'] = [Card.from_code("2S")]
    session.hands['P2'] = [Card.from_code("AS")]
    session.hands['P3'] = [Card.from_code("3S")]
    session.hands['P4'] = [Card.from_code("4S")]

    session.play_card('P1', '2S')
    session.play_card('P2', 'AS')
    session.play_card('P3', '3S')
    session.play_card('P4', '4S')

    assert session.round_complete is True
    assert session.pot_manager.team_tricks_won['Team B'] == 10
    assert any("EARLY WIN: Lead Team B clinched deal with 10 tricks at Trick 10" in log for log in session.current_round_logs)

    # Lead Team B won -> Dealer Team A lost (+9 penalty) -> Dealer P1 score = 0 + 9 = 9
    assert session.ladder_manager.dealer_id == 'P1'
    assert session.ladder_manager.dealer_score == 9


def test_no_early_win_on_single_non_consecutive_trick():
    """
    Regression test for user issue:
    Both teams have 4 tricks (16 cards).
    At Trick 9, Team B wins a single trick (streak 1, not consecutive).
    Team B must NOT collect the pot, must NOT be awarded a 5th trick,
    and Early Win must NOT trigger! Round must continue to Trick 10!
    """
    session = GameSession(initial_dealer='P4', initial_score=0)  # P4 is Team B
    session.start_new_round(mode="Regular")
    if session.deal_stage == "SELECT_TRUMP":
        session.select_hidden_trump(session.hands[session.eldest_hand][0].code)

    session.pot_manager.team_cards_collected['Team A'] = 16
    session.pot_manager.team_tricks_won['Team A'] = 4
    session.pot_manager.team_cards_collected['Team B'] = 16
    session.pot_manager.team_tricks_won['Team B'] = 4
    session.trick_number = 9

    # Trick 8 was won by Team A (P1)
    session.pot_manager.last_winner_player_id = 'P1'
    session.pot_manager.last_winner_team = 'Team A'
    session.pot_manager.streak_count = 1
    session.pot_manager.pot_cards = []
    session.pot_manager.pot_tricks_count = 0

    # Team B (P2) wins trick 9 (Win 1, NOT consecutive for P2!)
    session.current_turn_player = 'P1'
    session.hands['P1'] = [Card.from_code("6C"), Card.from_code("2D")]
    session.hands['P2'] = [Card.from_code("10C"), Card.from_code("3D")]
    session.hands['P3'] = [Card.from_code("3C"), Card.from_code("4D")]
    session.hands['P4'] = [Card.from_code("4C"), Card.from_code("5D")]

    session.play_card('P1', '6C')
    session.play_card('P2', '10C')  # 10C wins
    session.play_card('P3', '3C')
    session.play_card('P4', '4C')

    # Round must NOT be complete!
    assert session.round_complete is False
    assert session.trick_number == 10
    # Team B tricks remain 4 (NOT 5!) and cards collected remain 16
    assert session.pot_manager.team_tricks_won['Team B'] == 4
    assert session.pot_manager.team_cards_collected['Team B'] == 16
    assert len(session.pot_manager.pot_cards) == 4
    assert session.pot_manager.streak_count == 1
    assert session.pot_manager.last_winner_player_id == 'P2'
    assert session.pot_manager.last_winner_team == 'Team B'


def test_no_pot_collection_on_alternating_partners():
    """
    Rule: Double Sir requires 2 consecutive wins by the SAME individual player.
    If Partner P2 wins Trick 1, then Partner P4 wins Trick 2:
    - P2's streak resets.
    - P4 has streak 1.
    - Pot is NOT collected (8 cards remain in pot).
    If P4 wins Trick 3:
    - P4 achieves 2 consecutive wins (P4 streak 2).
    - Team B collects all 12 cards (3 tricks)!
    """
    session = GameSession(initial_dealer='P4', initial_score=0)  # P4 is Team B
    session.start_new_round(mode="Regular")
    if session.deal_stage == "SELECT_TRUMP":
        session.select_hidden_trump(session.hands[session.eldest_hand][0].code)

    # Trick 1: P2 wins with AC
    session.current_turn_player = 'P1'
    session.hands['P1'] = [Card.from_code("2C"), Card.from_code("2H"), Card.from_code("2S")]
    session.hands['P2'] = [Card.from_code("AC"), Card.from_code("3H"), Card.from_code("3S")]
    session.hands['P3'] = [Card.from_code("4C"), Card.from_code("4H"), Card.from_code("4S")]
    session.hands['P4'] = [Card.from_code("5C"), Card.from_code("AH"), Card.from_code("AS")]

    session.play_card('P1', '2C')
    session.play_card('P2', 'AC')
    session.play_card('P3', '4C')
    session.play_card('P4', '5C')

    assert session.pot_manager.last_winner_player_id == 'P2'
    assert session.pot_manager.streak_count == 1
    assert len(session.pot_manager.pot_cards) == 4
    assert session.pot_manager.team_cards_collected['Team B'] == 0

    # Trick 2: P4 (partner of P2) wins with AH (P2 plays 3H)
    # Different player won! P2 streak broken; P4 starts streak 1.
    session.play_card('P2', '3H')
    session.play_card('P3', '4H')
    session.play_card('P4', 'AH')
    session.play_card('P1', '2H')

    assert session.pot_manager.last_winner_player_id == 'P4'
    assert session.pot_manager.streak_count == 1
    assert len(session.pot_manager.pot_cards) == 8  # Pot NOT collected!
    assert session.pot_manager.team_cards_collected['Team B'] == 0

    # Trick 3: P4 wins AGAIN with AS (2nd consecutive win by P4!)
    session.play_card('P4', 'AS')
    session.play_card('P1', '2S')
    session.play_card('P2', '3S')
    session.play_card('P3', '4S')

    # Now P4 has won 2 in a row -> Team B collects all 12 cards (3 tricks)!
    assert len(session.pot_manager.pot_cards) == 0
    assert session.pot_manager.team_cards_collected['Team B'] == 12
    assert session.pot_manager.team_tricks_won['Team B'] == 3
    assert session.pot_manager.last_winner_player_id is None
    assert session.pot_manager.streak_count == 0


def test_early_win_tera_fail_opponent_win():
    """
    In Tera, declarer must take all 13 tricks.
    Tera fails when opponents actually collect tricks (2 consecutive wins by the same opponent).
    """
    session = GameSession(initial_dealer='P4', initial_score=0)  # P4 Team B
    session.start_new_round(mode="Regular")
    if session.deal_stage == "SELECT_TRUMP":
        session.select_hidden_trump(session.hands['P1'][0].code)
    session.declare_contract('P1', 'Tera')  # P1 Team A declares Tera
    session.resolve_bidding()
    session.set_runtime_trump(Suit.DIAMONDS)

    # Opponent P2 already has 1 pending win
    session.pot_manager.last_winner_player_id = 'P2'
    session.pot_manager.last_winner_team = 'Team B'
    session.pot_manager.streak_count = 1
    session.pot_manager.pot_cards = [Card.from_code("2C"), Card.from_code("3C"), Card.from_code("4C"), Card.from_code("5C")]
    session.pot_manager.pot_tricks_count = 1

    session.current_turn_player = 'P1'
    session.hands['P1'] = [Card.from_code("2D")]
    session.hands['P2'] = [Card.from_code("AD")]
    session.hands['P3'] = [Card.from_code("3D")]
    session.hands['P4'] = [Card.from_code("4D")]

    session.play_card('P1', '2D')
    session.play_card('P2', 'AD')  # P2 wins 2nd consecutive trick -> Team B collects pot!
    session.play_card('P3', '3D')
    session.play_card('P4', '4D')

    assert session.round_complete is True
    assert any("TERA FAILED! Opponents (Team B) collected 8 cards" in log for log in session.current_round_logs)
    # Dealer was Team B at 0. Team A declared Tera and lost -> delta = -26 to dealer -> raw score = -26.
    # Next dealer is Opponent (Team A, P1) starting directly at 26!
    assert session.ladder_manager.dealer_id == 'P1'
    assert session.ladder_manager.dealer_score == 26


def test_tera_survives_isolated_opponent_hand_win():
    """
    User rule: In Bikkad Double Sir, an in-between single hand won by opponents does NOT fail Tera!
    Opponents must win consecutive tricks to collect the pot.
    If an opponent wins an isolated trick, cards stay in the pot and Tera continues.
    """
    session = GameSession(initial_dealer='P4', initial_score=0)  # P4 Team B
    session.start_new_round(mode="Regular")
    if session.deal_stage == "SELECT_TRUMP":
        session.select_hidden_trump(session.hands['P1'][0].code)
    session.declare_contract('P1', 'Tera')  # P1 Team A declares Tera
    session.resolve_bidding()
    session.set_runtime_trump(Suit.DIAMONDS)

    # Trick 1: P1 (declarer) wins with KD
    session.current_turn_player = 'P1'
    session.hands['P1'] = [Card.from_code("KD"), Card.from_code("2H"), Card.from_code("JH"), Card.from_code("QH")]
    session.hands['P2'] = [Card.from_code("9D"), Card.from_code("5H"), Card.from_code("6H"), Card.from_code("7H")]
    session.hands['P3'] = [Card.from_code("5D"), Card.from_code("8H"), Card.from_code("9H"), Card.from_code("10H")]
    session.hands['P4'] = [Card.from_code("2D"), Card.from_code("AH"), Card.from_code("3H"), Card.from_code("4H")]

    session.play_card('P1', 'KD')
    session.play_card('P2', '9D')
    session.play_card('P3', '5D')
    session.play_card('P4', '2D')

    assert session.round_complete is False
    assert len(session.pot_manager.pot_cards) == 4
    assert session.pot_manager.last_winner_player_id == 'P1'

    # Trick 2: Opponent P4 wins with AH (isolated in-between win, NOT consecutive!)
    # Pot must accumulate to 8 cards and Tera must NOT abort!
    session.play_card('P1', '2H')
    session.play_card('P2', '5H')
    session.play_card('P3', '8H')
    session.play_card('P4', 'AH')

    assert session.round_complete is False  # TERA DID NOT FAIL!
    assert len(session.pot_manager.pot_cards) == 8
    assert session.pot_manager.last_winner_player_id == 'P4'
    assert session.pot_manager.team_cards_collected['Team B'] == 0

    # Trick 3: Declarer P1 wins with JH (breaks P4's streak!)
    session.play_card('P4', '3H')
    session.play_card('P1', 'JH')
    session.play_card('P2', '6H')
    session.play_card('P3', '9H')

    assert session.round_complete is False
    assert len(session.pot_manager.pot_cards) == 12
    assert session.pot_manager.last_winner_player_id == 'P1'

    # Trick 4: Declarer P1 wins with QH (P1 streak 2!) -> Team A collects all 16 cards!
    session.play_card('P1', 'QH')
    session.play_card('P2', '7H')
    session.play_card('P3', '10H')
    session.play_card('P4', '4H')

    # Team A successfully collected 16 cards (4 tricks)!
    assert session.round_complete is False
    assert session.pot_manager.team_cards_collected['Team A'] == 16
    assert session.pot_manager.team_tricks_won['Team A'] == 4
    assert session.pot_manager.team_cards_collected['Team B'] == 0


def test_early_win_double_tera_fail():
    """
    In Double Tera, declarer plays solo without partner.
    If opponents collect pot (2 consecutive wins), deal terminates immediately.
    """
    session = GameSession(initial_dealer='P4', initial_score=0)  # P4 Team B
    session.start_new_round(mode="Regular")
    if session.deal_stage == "SELECT_TRUMP":
        session.select_hidden_trump(session.hands['P1'][0].code)
    session.declare_contract('P1', 'Double Tera')  # P1 Team A declares Double Tera
    session.resolve_bidding()
    session.set_runtime_trump(Suit.HEARTS)

    # Opponent P2 already has 1 win
    session.pot_manager.last_winner_player_id = 'P2'
    session.pot_manager.last_winner_team = 'Team B'
    session.pot_manager.streak_count = 1
    session.pot_manager.pot_cards = [Card.from_code("2C"), Card.from_code("3C"), Card.from_code("4C")]
    session.pot_manager.pot_tricks_count = 1

    session.current_turn_player = 'P1'
    session.hands['P1'] = [Card.from_code("2H")]
    session.hands['P2'] = [Card.from_code("AH")]
    session.hands['P4'] = [Card.from_code("4H")]

    session.play_card('P1', '2H')
    session.play_card('P2', 'AH')  # P2 Team B wins 2nd consecutive trick -> collects pot!
    session.play_card('P4', '4H')

    assert session.round_complete is True
    assert any("DOUBLE TERA FAILED! Opponents (Team B) collected" in log for log in session.current_round_logs)
    # Dealer Team B on 0 -> delta = -52 -> raw score = -52 -> P1 gets 52 penalty (instant Coat) -> passes to partner P3 at 0!
    assert session.ladder_manager.dealer_id == 'P3'
    assert session.ladder_manager.dealer_score == 0
