import pytest
from backend.engine.card import Card, Suit
from backend.engine.game_session import GameSession


def test_double_tera_success_solo_win():
    """Bug 1: Double Tera victory must record Double Tera SUCCESS and swing +26/-26 points."""
    session = GameSession(initial_dealer='P1', initial_score=27)
    session.start_new_round(mode="Double Tera", declarer_id='P1')
    
    # Partner P3 sits out
    assert 'P3' not in session.active_players
    assert session.active_players == ['P1', 'P2', 'P4']
    
    # Declarer P1 sets trump HEARTS
    session.set_runtime_trump('H')
    
    # Simulate P1 winning tricks and sweeping pot
    # P1 wins all 39 cards (13 tricks * 3 players)
    # Opponents win 0 tricks
    cards = [Card.from_code('AS'), Card.from_code('KS'), Card.from_code('QS')]
    for trk in range(1, 14):
        session.current_trick = [('P1', cards[0]), ('P2', cards[1]), ('P4', cards[2])]
        session.pot_manager.add_trick('P1', cards, trk, session.player_teams)
    
    # Round ends
    session._end_round()
    assert session.round_complete is True
    # Active players must still show partner P3 sitting out in round summary
    assert 'P3' not in session.active_players
    
    # Check ladder result
    last_hist = session.game_history[-1]
    assert "Double Tera SUCCESS" in last_hist['note']
    assert last_hist['delta'] == -26  # Dealer P1 clears 26 points burden
    assert last_hist['new_score'] == 1


def test_demand_runtime_trump_by_other_player():
    """Bug 2: In Tera or Double Tera, another player who is void can demand trump from declarer."""
    session = GameSession(initial_dealer='P1', initial_score=0)
    session.start_new_round(mode="Tera", declarer_id='P1')
    
    # Trick 1: P1 leads Spades
    session.led_suit = Suit.SPADES
    session.current_trick = [('P1', Card.from_code('AS'))]
    session.current_turn_player = 'P2'
    
    # Give P2 hand with NO spades (void in spades)
    session.hands['P2'] = [Card.from_code('10H'), Card.from_code('KD')]
    # Give declarer P1 hand
    session.hands['P1'] = [Card.from_code('AH'), Card.from_code('KH')]
    
    # P2 demands trump from P1 (P1 is human)
    state = session.demand_runtime_trump('P2')
    assert session.trump_selection_pending_from == 'P1'
    assert session.trump_demanded_by == 'P2'
    assert session.must_play_trump_player == 'P2'
    
    # Declarer P1 selects runtime trump Hearts
    session.set_runtime_trump('H')
    assert session.trump_suit == Suit.HEARTS
    assert session.trump_revealed is True
    assert session.must_play_trump_player == 'P2'


def test_must_play_trump_after_asking_trump():
    """Bug 4: After asking/opening trump, player MUST play a trump card if held."""
    session = GameSession(initial_dealer='P1', initial_score=0)
    session.start_new_round(mode="Regular")
    session.hidden_trump_card = Card.from_code('AH')
    session.hidden_trump_setter = 'P1'
    session.trump_suit = Suit.HEARTS
    session.deal_stage = "READY"
    
    # P1 leads Diamonds
    session.led_suit = Suit.DIAMONDS
    session.current_trick = [('P1', Card.from_code('AD'))]
    session.current_turn_player = 'P2'
    
    # P2 has no Diamonds, but has 10 of Hearts (Trump) and King of Clubs (non-trump)
    session.hands['P2'] = [Card.from_code('10H'), Card.from_code('KC')]
    
    # P2 opens trump (demands cut)
    session.open_trump('P2')
    assert session.trump_revealed is True
    assert session.must_play_trump_player == 'P2'
    
    # P2 tries to play KC (non-trump) -> MUST FAIL!
    with pytest.raises(ValueError, match="Must play a trump card"):
        session.play_card('P2', 'KC')
        
    # P2 plays 10H (trump) -> MUST SUCCEED!
    session.play_card('P2', '10H')
    assert session.must_play_trump_player is None


def test_can_play_any_if_no_trump_after_asking():
    """Bug 4: If player asked trump but has NO trump card in hand, they can play any legal card."""
    session = GameSession(initial_dealer='P1', initial_score=0)
    session.start_new_round(mode="Regular")
    session.hidden_trump_card = Card.from_code('AH')
    session.hidden_trump_setter = 'P1'
    session.trump_suit = Suit.HEARTS
    session.deal_stage = "READY"
    
    session.led_suit = Suit.DIAMONDS
    session.current_trick = [('P1', Card.from_code('AD'))]
    session.current_turn_player = 'P2'
    
    # P2 has no Diamonds and no Hearts (no trump!)
    session.hands['P2'] = [Card.from_code('KC'), Card.from_code('QS')]
    
    session.open_trump('P2')
    # Since P2 has no trump card, playing KC is legal
    session.play_card('P2', 'KC')
    assert session.must_play_trump_player is None
