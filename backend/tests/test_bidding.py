import pytest
from backend.engine.game_session import GameSession


def test_bidding_resolution_priority_hidden_trump():
    """
    Tests bidding resolution:
    - P1 (Team A, hidden trump setter) bids Tera.
    - P2 (Team B) also bids Tera.
    - Result: P1 wins priority because P1's team holds/set hidden trump!
    """
    session = GameSession(initial_dealer='P4', initial_score=0)  # P1 is eldest hand & trump setter
    session.start_new_round(mode="Regular")
    if session.deal_stage == "SELECT_TRUMP":
        session.select_hidden_trump(session.hands['P1'][0].code)

    assert session.hidden_trump_setter == 'P1'
    
    session.declare_contract('P1', 'Tera')
    session.declare_contract('P2', 'Tera')

    state = session.resolve_bidding()
    assert state['mode'] == 'Tera'
    assert state['declarer_id'] == 'P1'  # P1 wins tie-breaker!


def test_bidding_resolution_higher_contract_level():
    """
    Tests bidding resolution:
    - P2 (Team B) bids Tera.
    - P3 (Team A) bids Double Tera.
    - Result: Double Tera wins because Double Tera > Tera.
    """
    session = GameSession(initial_dealer='P1', initial_score=0)
    session.start_new_round(mode="Regular")
    if session.deal_stage == "SELECT_TRUMP":
        session.select_hidden_trump(session.hands['P1'][0].code)

    session.declare_contract('P2', 'Tera')
    session.declare_contract('P3', 'Double Tera')

    state = session.resolve_bidding()
    assert state['mode'] == 'Double Tera'
    assert state['declarer_id'] == 'P3'


def test_bidding_continuous_match_flow():
    """
    Tests bidding phase in a continuous multi-round match.
    """
    session = GameSession(initial_dealer='P1', initial_score=0)
    
    # Round 1
    session.start_new_round(mode="Regular")
    if session.deal_stage == "SELECT_TRUMP":
        session.select_hidden_trump(session.hands['P1'][0].code)
    session.resolve_bidding()
    assert session.mode == "Regular"

    # Round 2 - Next deal
    session.start_new_round(mode="Regular")
    if session.deal_stage == "SELECT_TRUMP":
        session.select_hidden_trump(session.hands['P1'][0].code)
    session.declare_contract('P1', 'Tera')
    session.resolve_bidding()

    assert session.mode == "Tera"
    assert session.declarer_id == "P1"
    assert session.round_number == 2


def test_tera_declaration_mid_trick1_restores_cards_and_sets_declarer_lead():
    """
    User scenario:
    - Dealer is P4, so P1 is eldest hand. Let's make dealer P2 so P3 is eldest hand!
    - Trick 1 starts with P3 leading. P3 plays a card, P4 plays a card.
    - At this point P3 has 12 cards, P4 has 12 cards, current trick has 2 cards.
    - P1 declares 'Tera' before playing their card.
    - Verification:
      1. All players (including P3 and P4) have all 13 cards restored!
      2. The table trick is cleared (empty).
      3. P1 (declarer) leads Trick 1 (current_turn_player == 'P1').
      4. Hidden trump is removed.
      5. Announcement banner data is populated.
    """
    session = GameSession(initial_dealer='P2', initial_score=0)
    session.start_new_round(mode="Regular")
    if session.deal_stage == "SELECT_TRUMP":
        session.select_hidden_trump(session.hands['P1'][0].code)

    assert session.eldest_hand == 'P3'
    assert session.current_turn_player == 'P3'

    # P3 plays first card of Trick 1
    p3_card = session.hands['P3'][0].code
    session.play_card('P3', p3_card)
    assert len(session.hands['P3']) == 11  # 12 initial (1 hidden) - 1 played = 11

    # P4 plays second card of Trick 1
    p4_card = session.hands['P4'][0].code
    session.play_card('P4', p4_card)
    assert len(session.hands['P4']) == 12
    assert len(session.current_trick) == 2

    # Now P1 declares Tera
    session.declare_contract('P1', 'Tera')
    state = session.resolve_bidding()

    # Assertions
    assert state['mode'] == 'Tera'
    assert state['declarer_id'] == 'P1'
    assert state['current_turn_player'] == 'P1'  # P1 plays first!
    assert state['current_trick'] == []  # Trick cleared!
    assert state['trick_number'] == 1
    assert state['hidden_trump_card'] is None  # No hidden trump in Tera!

    # Everyone must have their full 13 cards back!
    assert len(state['hands']['P1']) == 13
    assert len(state['hands']['P2']) == 13
    assert len(state['hands']['P3']) == 13
    assert len(state['hands']['P4']) == 13

    # Announcement must exist
    assert state['announcement'] is not None
    assert session.player_names['P1'] in state['announcement']['title']


def test_new_game_endpoint_creation_and_reset():
    """
    Tests /api/new_game endpoint logic:
    - Custom game name (e.g. 'game1')
    - Custom player name for Sagan
    - Resets dealer score to 0
    """
    from fastapi.testclient import TestClient
    from backend.server import app

    client = TestClient(app)
    res = client.post("/api/new_game", json={
        "game_name": "game1",
        "player_names": {
            "P1": "Sagan (South - Team A)",
            "P2": "Vikram (West - Team B)",
            "P3": "Arjun (North - Team A)",
            "P4": "Sneha (East - Team B)"
        }
    })
    assert res.status_code == 200
    data = res.json()
    assert data['game_name'] == "game1"
    assert data['player_names']['P1'] == "Sagan (South - Team A)"
    assert data['dealer_score'] == 0
    assert data['round_number'] == 1



