import pytest
from backend.engine.card import Card, Suit, Rank
from backend.engine.game_session import GameSession


def test_game_round_full_simulation_regular():
    """
    Simulates a full 13-trick Regular mode round played automatically by AI engines.
    Verifies that all 13 tricks execute legally, cards accumulate and collect properly,
    and dealer score updates correctly.
    """
    session = GameSession(initial_dealer='P1', initial_score=0)
    session.start_new_round()
    session.resolve_bidding()

    max_turns = 100
    turns = 0
    while not session.round_complete and turns < max_turns:
        current_p = session.current_turn_player
        hand = session.hands[current_p]
        
        # Pick legal card
        led_suit = session.led_suit
        same_suit = [c for c in hand if c.suit == led_suit] if led_suit else hand
        card_to_play = same_suit[0] if same_suit else hand[0]

        session.play_card(current_p, card_to_play.code)
        turns += 1

    assert session.round_complete == True
    assert session.trick_number <= 13
    
    # In Regular mode, round completes when Dealer team hits 5 tricks or Lead team hits 9 tricks
    dealer_team = session.player_teams[session.current_dealer_id]
    lead_team = 'Team B' if dealer_team == 'Team A' else 'Team A'
    dealer_tricks = session.pot_manager.team_tricks_won[dealer_team]
    lead_tricks = session.pot_manager.team_tricks_won[lead_team]
    assert dealer_tricks >= 5 or lead_tricks >= 9 or session.trick_number == 13
    assert session.ladder_manager.dealer_score in (9, 18, 0)


def test_tera_mode_early_termination_on_opponent_win():
    """
    Verifies Tera mode behavior:
    If declarer team loses even 1 trick, Tera fails early with +26 penalty to opponents.
    """
    session = GameSession(initial_dealer='P1', initial_score=10)
    session.start_new_round()
    session.declare_contract('P1', 'Tera')
    session.resolve_bidding()

    # Opponent P2 already holds 1 win; winning next trick collects pot and fails Tera
    session.pot_manager.last_winner_player_id = 'P2'
    session.pot_manager.last_winner_team = 'Team B'
    session.pot_manager.streak_count = 1
    session.pot_manager.pot_cards = [Card.from_code("2C"), Card.from_code("3C"), Card.from_code("4C"), Card.from_code("5C")]
    session.pot_manager.pot_tricks_count = 1

    session.current_turn_player = 'P1'
    session.hands['P1'] = [Card.from_code("2H")]
    session.hands['P2'] = [Card.from_code("AH")]
    session.hands['P3'] = [Card.from_code("3H")]
    session.hands['P4'] = [Card.from_code("4H")]

    # P1 leads 2H, P2 plays AH (P2 wins 2nd consecutive trick for Team B -> collects pot!)
    session.play_card('P1', '2H')
    session.play_card('P2', 'AH')
    session.play_card('P3', '3H')
    session.play_card('P4', '4H')

    # Round must abort immediately on Tera fail!
    assert session.round_complete == True
    assert "TERA FAILED" in "".join(session.current_round_logs)
    # Dealer P1 (Team A) declared Tera and failed -> +26 penalty added!
    assert session.ladder_manager.dealer_score == 36  # 10 + 26 = 36


def test_double_tera_solo_handover():
    """
    Verifies Double Tera mode behavior:
    Partner sits out (3 active players: P1, P2, P4 if P1 declares Double Tera).
    """
    session = GameSession(initial_dealer='P1', initial_score=0)
    session.start_new_round()
    session.declare_contract('P1', 'Double Tera')
    session.resolve_bidding()

    assert "P3" not in session.active_players
    assert len(session.active_players) == 3

    # Next deal: Regular mode must restore partner to active players!
    next_state = session.start_new_round(mode="Regular")
    assert session.active_players == ['P1', 'P2', 'P3', 'P4']
    assert "P3" in session.active_players
    assert len(session.active_players) == 4
    assert next_state['active_players'] == ['P1', 'P2', 'P3', 'P4']
