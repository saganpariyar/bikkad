import pytest
from backend.engine.card import Card, Suit, Rank, Deck
from backend.engine.trick_evaluator import get_legal_cards, evaluate_trick, can_open_trump
from backend.engine.pot_manager import PotManager
from backend.engine.game_session import GameSession


def test_5_5_3_dealing_and_hidden_trump_selection():
    """
    Verifies 3-stage dealing (5 -> 5 -> 3 = 13 cards) and 5-card hidden trump selection.
    """
    session = GameSession(initial_dealer='P4', initial_score=0)
    # Dealer P4 -> Eldest Hand P1 (Human)
    state = session.start_new_round(mode="Regular")

    assert state['deal_stage'] == "SELECT_TRUMP"
    assert state['eldest_hand'] == "P1"
    assert len(state['hands']['P1']) == 5  # Initial 5 cards dealt

    # P1 selects 1 card from initial 5 cards to hide as trump
    card_to_hide = state['hands']['P1'][0]['code']
    next_state = session.select_hidden_trump(card_to_hide)

    assert next_state['deal_stage'] == "READY"
    assert next_state['hidden_trump_card']['code'] == card_to_hide
    # While trump is hidden under saucer, setter holds 12 cards (hidden card is removed from active hand)
    assert len(next_state['hands']['P1']) == 12
    assert not any(c['code'] == card_to_hide for c in next_state['hands']['P1'])
    # Other players have full 13 cards
    assert len(next_state['hands']['P2']) == 13
    assert len(next_state['hands']['P3']) == 13
    assert len(next_state['hands']['P4']) == 13

    # When trump is revealed / opened, the hidden card returns to the setter's active hand!
    session.open_trump('P1', force=True)
    revealed_state = session.get_state()
    assert len(revealed_state['hands']['P1']) == 13
    assert any(c['code'] == card_to_hide for c in revealed_state['hands']['P1'])


def test_deck_batches():
    deck = Deck(seed=42)
    deck.shuffle()
    b1 = deck.deal_batch1()
    b2 = deck.deal_batch2()
    b3 = deck.deal_batch3()

    assert len(b1[0]) == 5
    assert len(b2[0]) == 5
    assert len(b3[0]) == 3
    assert len(b1[0]) + len(b2[0]) + len(b3[0]) == 13


def test_dealer_eldest_hand_trick_leader_flow():
    session = GameSession(initial_dealer='P1', initial_score=0)
    session.start_new_round(mode="Regular")

    assert session.ladder_manager.dealer_id == 'P1'
    assert session.eldest_hand == 'P2'
    assert session.hidden_trump_setter == 'P2'
    assert session.current_turn_player == 'P2'


def test_must_follow_suit():
    hand = [Card.from_code("AS"), Card.from_code("10S"), Card.from_code("5H")]
    legal = get_legal_cards(hand, Suit.SPADES)
    assert len(legal) == 2
    assert all(c.suit == Suit.SPADES for c in legal)

    legal_void = get_legal_cards(hand, Suit.DIAMONDS)
    assert len(legal_void) == 3


def test_evaluate_trick_lead_suit_winner():
    plays = [
        ('P2', Card.from_code("KS")),
        ('P3', Card.from_code("8S")),
        ('P4', Card.from_code("9S")),
        ('P1', Card.from_code("3S"))
    ]
    winner, card = evaluate_trick(plays, Suit.SPADES, Suit.DIAMONDS, trump_revealed=False)
    assert winner == 'P2'
    assert card.code == "KS"


def test_evaluate_trick_trump_cut():
    plays = [
        ('P2', Card.from_code("AS")),
        ('P3', Card.from_code("3S")),
        ('P4', Card.from_code("2D")),  # Trump cut!
        ('P1', Card.from_code("9S"))
    ]
    winner, card = evaluate_trick(plays, Suit.SPADES, Suit.DIAMONDS, trump_revealed=True)
    assert winner == 'P4'
    assert card.code == "2D"


def test_pot_manager_2_consecutive_wins():
    pot = PotManager()
    player_teams = {'P1': 'Team A', 'P3': 'Team A', 'P2': 'Team B', 'P4': 'Team B'}
    cards_t1 = [Card.from_code("2S"), Card.from_code("3S"), Card.from_code("4S"), Card.from_code("5S")]
    cards_t2 = [Card.from_code("2H"), Card.from_code("3H"), Card.from_code("4H"), Card.from_code("5H")]

    collected, team, count, reason = pot.add_trick('P2', cards_t1, 1, player_teams)
    assert not collected
    assert len(pot.pot_cards) == 4
    assert pot.streak_count == 1
    assert pot.last_winner_player_id == 'P2'

    # Same individual player P2 wins trick 2 -> 2 consecutive wins by P2!
    collected, team, count, reason = pot.add_trick('P2', cards_t2, 2, player_teams)
    assert collected
    assert team == 'Team B'
    assert count == 8


def test_pot_manager_13th_trick_sweep():
    pot = PotManager()
    player_teams = {'P1': 'Team A', 'P3': 'Team A', 'P2': 'Team B', 'P4': 'Team B'}
    cards_t13 = [Card.from_code("2S"), Card.from_code("3S"), Card.from_code("4S"), Card.from_code("5S")]

    collected, team, count, reason = pot.add_trick('P1', cards_t13, 13, player_teams)
    assert collected
    assert team == 'Team A'
    assert reason == "13th_sweep"


def test_hidden_trump_card_removed_from_hand_and_returned_on_show():
    """
    User scenario:
    - Eldest Hand (P1) hides Ace of Hearts ('AH' / 'laal ka ikka').
    - Verification:
      1. 'AH' is removed from P1's active hand while trump is hidden (12 cards in hand).
      2. P1 CANNOT play 'AH' while it's hidden under the saucer (raises ValueError).
      3. When trump is opened / shown (via open_trump or demand_cut), 'AH' returns to P1's hand (13 cards).
      4. 'AH' is now available in P1's hand and can be legally played!
    """
    session = GameSession(initial_dealer='P4', initial_score=0)
    session.start_new_round(mode="Regular")

    # Locate AH across deals and swap with P1's first card to guarantee no duplicates
    for p in ('P1', 'P2', 'P3', 'P4'):
        for i, c in enumerate(session.phase1_deals[p]):
            if c.code == "AH":
                session.phase1_deals[p][i] = session.phase1_deals['P1'][0]
                session.phase1_deals['P1'][0] = Card.from_code("AH")
                break
        for i, c in enumerate(session.remaining_deals[p]):
            if c.code == "AH":
                session.remaining_deals[p][i] = session.phase1_deals['P1'][0]
                session.phase1_deals['P1'][0] = Card.from_code("AH")
                break

    st = session.select_hidden_trump("AH")

    # 1. AH is hidden under saucer, NOT in active hand
    assert session.hidden_trump_card.code == "AH"
    assert session.trump_revealed is False
    assert len(session.hands['P1']) == 12
    assert not any(c.code == "AH" for c in session.hands['P1'])

    # 2. Trying to play AH while hidden must fail
    with pytest.raises(ValueError, match="Card AH not in"):
        session.play_card('P1', 'AH')

    # 3. P1 opens trump (e.g. asking for show or demanding cut)
    opened = session.open_trump('P1', force=True)
    assert opened is True
    assert session.trump_revealed is True

    # 4. AH has now returned to P1's hand!
    assert len(session.hands['P1']) == 13
    assert any(c.code == "AH" for c in session.hands['P1'])

    # 5. P1 can now play AH as the trick leader!
    st2 = session.play_card('P1', 'AH')
    assert len(st2['current_trick']) == 1
    assert st2['current_trick'][0]['card']['code'] == "AH"

