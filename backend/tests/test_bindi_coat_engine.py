import pytest
try:
    from backend.engine.bindi_coat.bindi_coat_session import BindiCoatSession
except ImportError:
    from engine.bindi_coat.bindi_coat_session import BindiCoatSession


def test_bindi_coat_blind_mode():
    # By default, first dealer is P4 (West), so Trump Placer is P1 (South, human)
    sess = BindiCoatSession(
        game_id="test_bc_1",
        player_types={"P1": "human", "P2": "ai", "P3": "ai", "P4": "ai"},
    )

    assert sess.trump_placer == "P1"
    assert sess.phase == "BANDH_HUKUM_SELECTION"
    assert len(sess.hands["P1"]) == 5

    # Check to_dict masks the hand during BANDH_HUKUM_SELECTION
    state = sess.to_dict("P1")
    assert state["phase"] == "BANDH_HUKUM_SELECTION"
    assert state["my_hand"] == ["BACK", "BACK", "BACK", "BACK", "BACK"]
    assert state["bandh_hukum"]["revealed"] is False
    assert state["bandh_hukum"]["trump_suit"] is None
    assert state["bandh_hukum"]["card"] is None

    # Pick 2nd face-down card (index 1) blindly
    original_hand = list(sess.hands["P1"])
    chosen_card = original_hand[1]

    res = sess.select_bandh_hukum("P1", card_index=1)
    assert res["success"] is True
    assert sess.bandh_hukum_card == chosen_card
    assert sess.trump_suit == chosen_card[-1]
    assert sess.phase == "PLAYING"

    # Now all cards are dealt
    # P1 placed 1 card, so P1 has 4 + 8 = 12 cards in hand (and 1 hidden on table)
    assert len(sess.hands["P1"]) == 12
    # Other players have 5 + 8 = 13 cards in hand
    assert len(sess.hands["P2"]) == 13
    assert len(sess.hands["P3"]) == 13
    assert len(sess.hands["P4"]) == 13

    # In PLAYING phase, my_hand is revealed to P1
    state_playing = sess.to_dict("P1")
    assert state_playing["phase"] == "PLAYING"
    assert "BACK" not in state_playing["my_hand"]
    assert len(state_playing["my_hand"]) == 12

    # Still hidden to everyone until void trigger
    assert state_playing["bandh_hukum"]["revealed"] is False
    assert state_playing["bandh_hukum"]["trump_suit"] is None
    assert state_playing["bandh_hukum"]["card"] is None


def test_bindi_coat_ai_placer():
    # When P1 is AI, AI automatically selects Bandh Hukum blindly and advances to PLAYING
    sess = BindiCoatSession(
        game_id="test_bc_2",
        player_types={"P1": "ai", "P2": "ai", "P3": "ai", "P4": "ai"},
    )
    assert sess.trump_placer == "P1"
    assert sess.phase == "PLAYING"
    assert sess.bandh_hukum_card is not None
    assert sess.trump_suit is not None
    assert sess.trump_revealed is False
