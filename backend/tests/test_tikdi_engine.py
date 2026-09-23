import pytest
from backend.engine.card import Card, Suit, Rank
from backend.engine.tikdi.tikdi_deck import create_tikdi_deck, TikdiDeck
from backend.engine.tikdi.tikdi_session import TikdiSession
from backend.engine.tikdi.tikdi_ai import select_tikdi_trump, evaluate_trick_winner


def test_tikdi_deck_composition():
    deck = create_tikdi_deck()
    assert len(deck) == 30

    # Verify Heart & Spade have 8 cards each (includes 7)
    hearts = [c for c in deck if c.suit == Suit.HEARTS]
    spades = [c for c in deck if c.suit == Suit.SPADES]
    assert len(hearts) == 8
    assert len(spades) == 8
    assert any(c.rank == Rank.SEVEN for c in hearts)
    assert any(c.rank == Rank.SEVEN for c in spades)

    # Verify Clubs & Diamonds have 7 cards each (no 7)
    clubs = [c for c in deck if c.suit == Suit.CLUBS]
    diamonds = [c for c in deck if c.suit == Suit.DIAMONDS]
    assert len(clubs) == 7
    assert len(diamonds) == 7
    assert not any(c.rank == Rank.SEVEN for c in clubs)
    assert not any(c.rank == Rank.SEVEN for c in diamonds)

    # Verify no 2-6 cards in any suit
    ranks_present = {c.rank.value for c in deck}
    assert all(r >= 7 for r in ranks_present)
    assert not any(r in ranks_present for r in [2, 3, 4, 5, 6])


def test_tikdi_session_dealing_and_trump():
    session = TikdiSession(game_id="test_tikdi")
    # Initial state: Stage 1 (5 cards dealt)
    assert session.phase == "TRUMP_SELECTION"
    assert session.dealer == "P1"
    assert session.trump_chooser == "P2"
    assert session.bystander == "P3"
    assert session.quotas == {"P2": 5, "P3": 3, "P1": 2}

    for p in session.players:
        assert len(session.hands[p]) == 5

    # Trump Chooser declares trump
    success = session.select_trump("S", player="P2")
    assert success is True
    assert session.trump_suit == "S"

    # Hands should now have 10 cards each (5 + 3 + 2 = 10)
    for p in session.players:
        assert len(session.hands[p]) == 10

    assert session.phase == "TRICK_PLAYING"
    assert session.current_turn == "P2"  # Trump Chooser leads Trick 1


def test_tikdi_trick_evaluation():
    # Suit led is Diamonds, trump is Spades
    # Card 1: 9D, Card 2: KD, Card 3: 8S (Trump cut)
    trick = [
        {"player": "P2", "card": Card(Rank.NINE, Suit.DIAMONDS)},
        {"player": "P3", "card": Card(Rank.KING, Suit.DIAMONDS)},
        {"player": "P1", "card": Card(Rank.EIGHT, Suit.SPADES)},
    ]
    win_idx, win_card = evaluate_trick_winner(trick, trump_suit="S")
    assert win_idx == 2
    assert win_card.code == "8S"


def test_simulation_round_1_playback():
    """
    Executes a complete 10-trick round validating the official rules and scoring tally:
    Player A (P2 / Trump Chooser, Quota 5): Won 6 -> +1
    Player B (P3 / Non-Dealer, Quota 3): Won 2 -> -1
    Player C (P1 / Dealer, Quota 2): Won 2 -> 0
    """
    session = TikdiSession(game_id="sim_r1")
    # Set custom hands matching Round 1 simulation where P2 is void in diamonds
    session.hands["P2"] = [
        Card.from_code("AS"), Card.from_code("KS"), Card.from_code("QS"), Card.from_code("10S"),
        Card.from_code("AH"), Card.from_code("QH"), Card.from_code("JH"), Card.from_code("10C"),
        Card.from_code("JC"), Card.from_code("9C")
    ]
    session.hands["P3"] = [
        Card.from_code("JS"), Card.from_code("8S"), Card.from_code("7S"), Card.from_code("10H"),
        Card.from_code("8H"), Card.from_code("KD"), Card.from_code("JD"), Card.from_code("10D"),
        Card.from_code("AC"), Card.from_code("QC")
    ]
    session.hands["P1"] = [
        Card.from_code("9S"), Card.from_code("KH"), Card.from_code("9H"), Card.from_code("7H"),
        Card.from_code("AD"), Card.from_code("QD"), Card.from_code("8D"), Card.from_code("9D"),
        Card.from_code("KC"), Card.from_code("8C")
    ]

    session.trump_suit = "S"
    session.phase = "TRICK_PLAYING"
    session.current_turn = "P2"

    sim_plays = [
        # Trick 1: P2 leads AS, P3 plays 7S, P1 plays 9S -> P2 wins
        [("P2", "AS"), ("P3", "7S"), ("P1", "9S"), "P2"],
        # Trick 2: P2 leads KS, P3 plays 8S, P1 discards 7H -> P2 wins
        [("P2", "KS"), ("P3", "8S"), ("P1", "7H"), "P2"],
        # Trick 3: P2 leads AH, P3 plays 8H, P1 plays KH -> P2 wins
        [("P2", "AH"), ("P3", "8H"), ("P1", "KH"), "P2"],
        # Trick 4: P2 leads 9C, P3 plays AC, P1 plays 8C -> P3 wins
        [("P2", "9C"), ("P3", "AC"), ("P1", "8C"), "P3"],
        # Trick 5: P3 leads KD, P1 plays AD, P2 cuts with 10S! -> P2 wins
        [("P3", "KD"), ("P1", "AD"), ("P2", "10S"), "P2"],
        # Trick 6: P2 leads QS, P3 plays JS, P1 discards 9D -> P2 wins
        [("P2", "QS"), ("P3", "JS"), ("P1", "9D"), "P2"],
        # Trick 7: P2 leads QH, P3 plays 10H, P1 plays 9H -> P2 wins
        [("P2", "QH"), ("P3", "10H"), ("P1", "9H"), "P2"],
        # Trick 8: P2 leads 10C, P3 plays QC, P1 plays KC -> P1 wins
        [("P2", "10C"), ("P3", "QC"), ("P1", "KC"), "P1"],
        # Trick 9: P1 leads QD, P2 plays JC, P3 plays JD -> P1 wins
        [("P1", "QD"), ("P2", "JC"), ("P3", "JD"), "P1"],
        # Trick 10: P1 leads 8D, P2 discards JH, P3 plays 10D -> P3 wins
        [("P1", "8D"), ("P2", "JH"), ("P3", "10D"), "P3"],
    ]

    for trick_idx, (p_a, p_b, p_c, expected_winner) in enumerate(sim_plays, 1):
        for player, code in [p_a, p_b, p_c]:
            res = session.play_card(player, code)
            assert res["success"] is True

        last_trick = session.trick_history[-1]
        assert last_trick["winner"] == expected_winner

    assert session.phase == "ROUND_OVER"
    assert session.tricks_won["P2"] == 6
    assert session.tricks_won["P3"] == 2
    assert session.tricks_won["P1"] == 2

    assert session.round_summary["net_scores"] == {
        "P2": 1,   # Quota 5 -> +1
        "P3": -1,  # Quota 3 -> -1
        "P1": 0    # Quota 2 -> 0
    }

    # P2 is owed 1 card by P3 for next round
    assert session.debts["P2"]["P3"] == 1


def test_automated_bot_full_round():
    """Verifies that 3 AI bots can play an entire round of Tikdi autonomously from dealing to round end."""
    session = TikdiSession(game_id="bot_match")
    session.player_types = {"P1": "ai", "P2": "ai", "P3": "ai"}

    # Run bot loop until round finishes
    steps = 0
    max_steps = 100
    while session.phase != "ROUND_OVER" and steps < max_steps:
        step_res = session.step_bot()
        assert step_res["action"] != "none"
        steps += 1

    assert session.round_summary is not None


def test_tikdi_quota_adjustment_mode():
    """Verifies that in quota_adjustment mode, debts create a PENALTY_ADJUSTMENT pause phase."""
    session = TikdiSession(game_id="quota_adj_test", penalty_mode="quota_adjustment")
    # Simulate P2 surplus of 1 trick against P3
    session.debts["P2"]["P3"] = 1
    session.next_round()  # Dealer rotates P1 -> P2, Chooser becomes P3, Bystander P1

    # Base quotas should be standard 5/3/2 (NOT adjusted yet)
    assert session.quotas["P3"] == 5  # Chooser
    assert session.quotas["P1"] == 3  # Bystander
    assert session.quotas["P2"] == 2  # Dealer

    # After trump selection, should enter PENALTY_ADJUSTMENT phase (NOT trick play)
    session.select_trump("H", player="P3")
    assert session.phase == "PENALTY_ADJUSTMENT"
    assert session.penalty_queue == []

    # Verify pending adjustments show correct data
    assert len(session.pending_adjustments) == 1
    adj = session.pending_adjustments[0]
    assert adj["creditor"] == "P2"
    assert adj["debtor"] == "P3"
    assert adj["count"] == 1

    # Verify adjusted_quotas preview shows the future values
    assert session.adjusted_quotas["P2"] == 3  # 2+1
    assert session.adjusted_quotas["P3"] == 4  # 5-1
    assert session.adjusted_quotas["P1"] == 3  # unchanged

    # After acknowledging, quotas should be applied and game enters TRICK_PLAYING
    success = session.acknowledge_adjustment(player="P3")
    assert success is True
    assert session.phase == "TRICK_PLAYING"
    assert session.quotas["P2"] == 3
    assert session.quotas["P3"] == 4
    assert session.quotas["P1"] == 3
    assert sum(session.quotas.values()) == 10
    # Debts should be cleared
    assert all(not ds for ds in session.debts.values())


def test_tikdi_card_swap_penalty_queue():
    """Verifies that when debtor chooses card_swap, penalty queue is populated for PENALTY_RESOLUTION."""
    session = TikdiSession(game_id="card_swap_test", penalty_mode="choice")
    session.debts["P1"]["P2"] = 1
    session.next_round()
    session.select_trump("S", player=session.trump_chooser)

    assert session.phase == "DEBT_SETTLEMENT_CHOICE"
    assert session.current_turn == "P2"  # Debtor who had less tricks chooses
    success = session.make_debt_choice("P2", "card_swap")
    assert success is True

    assert session.phase == "PENALTY_RESOLUTION"
    assert session.current_penalty is not None
    pen = session.current_penalty
    assert pen["puller"] == "P1"
    assert pen["target"] == "P2"
    assert pen["creditor"] == "P1"
    assert pen["debtor"] == "P2"
    assert pen["step"] == "PULL"


def test_tikdi_per_debtor_independent_choices():
    """Verifies that 1 player may say I don't want tash khichahi (give extra tricks) and other may choose tash khichahi."""
    session = TikdiSession(game_id="multi_choice_test", penalty_mode="choice")
    # P3 won +3 extra tricks. P1 owed 1 trick, P2 owed 2 tricks.
    session.debts["P3"]["P1"] = 1
    session.debts["P3"]["P2"] = 2
    session.next_round()
    session.select_trump("S", player=session.trump_chooser)

    assert session.phase == "DEBT_SETTLEMENT_CHOICE"
    # P1 (debtor) chooses Extra Tricks (does NOT want Tash Khinchai)
    assert session.current_turn == "P1"
    session.make_debt_choice("P1", "quota_adjustment")

    # P2 (debtor) chooses Tash Khinchai (card swap)
    assert session.current_turn == "P2"
    session.make_debt_choice("P2", "card_swap")

    # P1's debt became extra tricks in quota: P1 needs +1, P3 needs -1
    # P2's debt became card swap in penalty queue: 2 card pulls (1 in current, 1 in queue)
    assert session.phase == "PENALTY_RESOLUTION"
    assert session.current_penalty is not None
    assert session.current_penalty["debtor"] == "P2"
    assert session.current_penalty["creditor"] == "P3"
    assert len(session.penalty_queue) == 1
    assert session.penalty_queue[0]["debtor"] == "P2"


