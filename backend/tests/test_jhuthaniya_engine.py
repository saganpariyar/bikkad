import pytest
from backend.engine.jhuthaniya.jhuthaniya_session import JhuthaniyaSession, build_full_deck


def test_deck_52_cards():
    deck = build_full_deck()
    assert len(deck) == 52
    # Ensure all cards unique
    assert len(set(deck)) == 52


def test_jhuthaniya_dealer_rotation_clockwise():
    session = JhuthaniyaSession(game_id="test_jhuth", num_players=4)

    # Deal 1
    assert session.deal_number == 1
    assert session.dealer == "P1"
    assert session.dealer_index == 0
    # First turn should be player to the left of dealer (clockwise): P2
    assert session.current_turn == "P2"
    # 52 cards among 4 players = 13 each
    for pid in session.players:
        assert len(session.hands[pid]) == 13

    # State verification
    d1 = session.to_dict("P1")
    assert d1["dealer"] == "P1"
    assert d1["deal_number"] == 1
    assert d1["players"]["P1"]["is_dealer"] is True
    assert d1["players"]["P2"]["is_dealer"] is False

    # Deal 2
    session.new_game()
    assert session.deal_number == 2
    assert session.dealer == "P2"
    assert session.dealer_index == 1
    assert session.current_turn == "P3"
    d2 = session.to_dict("P1")
    assert d2["dealer"] == "P2"
    assert d2["players"]["P2"]["is_dealer"] is True
    assert d2["players"]["P1"]["is_dealer"] is False

    # Deal 3
    session.new_game()
    assert session.deal_number == 3
    assert session.dealer == "P3"
    assert session.dealer_index == 2
    assert session.current_turn == "P4"

    # Deal 4
    session.new_game()
    assert session.deal_number == 4
    assert session.dealer == "P4"
    assert session.dealer_index == 3
    assert session.current_turn == "P1"

    # Deal 5 (Wraps back to P1)
    session.new_game()
    assert session.deal_number == 5
    assert session.dealer == "P1"
    assert session.dealer_index == 0
    assert session.current_turn == "P2"


def test_tikdi_dealer_rotation_clockwise():
    from backend.engine.tikdi.tikdi_session import TikdiSession
    session = TikdiSession(game_id="test_tikdi_rot")

    # Round 1: Dealer = P1, Chooser = P2, Bystander = P3
    assert session.round_number == 1
    assert session.dealer == "P1"
    assert session.trump_chooser == "P2"
    assert session.bystander == "P3"
    assert session.quotas == {"P2": 5, "P3": 3, "P1": 2}

    # Round 2
    session.next_round()
    assert session.round_number == 2
    assert session.dealer == "P2"
    assert session.trump_chooser == "P3"
    assert session.bystander == "P1"
    assert session.quotas == {"P3": 5, "P1": 3, "P2": 2}

    # Round 3
    session.next_round()
    assert session.round_number == 3
    assert session.dealer == "P3"
    assert session.trump_chooser == "P1"
    assert session.bystander == "P2"
    assert session.quotas == {"P1": 5, "P2": 3, "P3": 2}

    # Round 4 (Wraps back to P1)
    session.next_round()
    assert session.round_number == 4
    assert session.dealer == "P1"
    assert session.trump_chooser == "P2"
    assert session.bystander == "P3"
    assert session.quotas == {"P2": 5, "P3": 3, "P1": 2}


def test_jhuthaniya_player_counts_2_to_7():
    for n in range(2, 8):
        sess = JhuthaniyaSession(game_id=f"test_n_{n}", num_players=n)
        assert sess.num_players == n
        assert len(sess.players) == n
        total_cards = sum(len(sess.hands[p]) for p in sess.players)
        expected_deck_size = 104 if n >= 6 else 52
        assert total_cards == expected_deck_size
        st = sess.to_dict("P1")
        assert len(st["players"]) == n
        assert len(st["active_players"]) == n


def test_jhuthaniya_next_player_only_and_locked_rank():
    sess = JhuthaniyaSession(game_id="test_opt_a", num_players=3)
    # Dealer is P1, lead turn is P2
    assert sess.current_turn == "P2"
    assert sess.trick_leader == "P2"
    assert sess.current_round_rank is None
    d = sess.to_dict("P1")
    assert d["can_choose_rank"] is True
    assert d["current_round_rank"] is None

    # 1. Lead P2 plays with declared rank "10"
    p2_card = sess.hands["P2"][0]
    res1 = sess.play_cards("P2", [p2_card], "10", 1)
    assert res1["success"] is True
    assert sess.current_round_rank == "10"

    # Only immediate next active player (P3) is in challenge_order!
    assert sess.challenge_order == ["P3"]
    # P1 should NOT be allowed to decide since it's only next player's decision
    res_p1 = sess.make_decision("P1", "pass")
    assert res_p1["success"] is False

    # P3 passes -> Immediately advances to P3's turn
    res_p3 = sess.make_decision("P3", "pass")
    assert res_p3["success"] is True
    assert sess.phase == "PLAYING"
    assert sess.current_turn == "P3"

    # 2. Follower P3 tries to play declaring "K" -> MUST FAIL!
    p3_card = sess.hands["P3"][0]
    res_fail = sess.play_cards("P3", [p3_card], "K", 1)
    assert res_fail["success"] is False
    assert "locked to 10" in res_fail["error"].lower()

    # 3. Follower P3 plays declaring "10" -> SUCCEEDS!
    res2 = sess.play_cards("P3", [p3_card], "10", 1)
    assert res2["success"] is True
    assert sess.current_round_rank == "10"
    # Only P1 is next player to decide
    assert sess.challenge_order == ["P1"]

    # P1 challenges P3
    res_ch = sess.make_decision("P1", "challenge", card_index=0)
    assert res_ch["resolved"] is True
    # Challenge resolved -> pot is picked up, rank unlocks for next leader!
    assert sess.center_pot == []
    assert sess.current_round_rank is None


def test_jhuthaniya_card_position_inspection():
    """
    Tests user scenario:
    Player plays 3 cards as Q (e.g. Q, K, Q).
    Next player inspects position 0 (Q) -> fails -> challenger takes pot.
    Next player inspects position 1 (K) -> succeeds -> claimant takes pot.
    """
    # 1. Inspection of matching card (fail to prove bluff)
    sess1 = JhuthaniyaSession(game_id="test_inspect_fail", num_players=3)
    p3_initial_count = len(sess1.hands["P3"])
    sess1.hands["P2"] = ["QD", "KS", "QH", "2C"]
    # P2 plays 3 cards claiming Q
    sess1.play_cards("P2", ["QD", "KS", "QH"], "Q", 3)
    assert sess1.challenge_order == ["P3"]
    # P3 inspects position 0 (QD -> Queen)
    res1 = sess1.make_decision("P3", "challenge", card_index=0)
    assert res1["success"] is True
    res_info1 = res1["resolution"]
    assert res_info1["verdict"] == "CHALLENGE_FAILED"
    assert res_info1["loser"] == "P3"
    # Challenger P3 takes all 3 cards from center pot
    assert len(sess1.hands["P3"]) == p3_initial_count + 3
    assert sess1.center_pot == []
    # Honest claimant P2 retains lead
    assert sess1.trick_leader == "P2"
    assert sess1.current_turn == "P2"

    # 2. Inspection of non-matching card (succeed in catching bluff)
    sess2 = JhuthaniyaSession(game_id="test_inspect_success", num_players=3)
    sess2.hands["P2"] = ["QD", "KS", "QH", "2C"]
    sess2.play_cards("P2", ["QD", "KS", "QH"], "Q", 3)
    assert sess2.challenge_order == ["P3"]
    # P3 inspects position 1 (KS -> King != Queen)
    res2 = sess2.make_decision("P3", "challenge", card_index=1)
    assert res2["success"] is True
    res_info2 = res2["resolution"]
    assert res_info2["verdict"] == "CAUGHT_BLUFF"
    assert res_info2["loser"] == "P2"
    # Bluffer P2 takes back all cards in pot
    assert "KS" in sess2.hands["P2"]
    assert sess2.center_pot == []
    # Successful challenger P3 becomes new leader
    assert sess2.trick_leader == "P3"
    assert sess2.current_turn == "P3"


def test_jhuthaniya_leader_rank_change_cycle():
    """
    Tests:
    Leader (P2) leads "Q".
    Followers (P3, P1) must follow "Q".
    When turn comes back to Leader (P2), P2 can change rank to "K"!
    Leader only changes when pot becomes empty.
    """
    sess = JhuthaniyaSession(game_id="test_leader_cycle", num_players=3)
    assert sess.trick_leader == "P2"
    assert sess.current_turn == "P2"

    # P2 leads "Q"
    c2 = sess.hands["P2"][0]
    sess.play_cards("P2", [c2], "Q", 1)
    assert sess.current_round_rank == "Q"
    sess.make_decision("P3", "pass")

    # P3 follows "Q"
    assert sess.current_turn == "P3"
    assert sess.to_dict("P3")["can_choose_rank"] is False
    c3 = sess.hands["P3"][0]
    sess.play_cards("P3", [c3], "Q", 1)
    sess.make_decision("P1", "pass")

    # P1 follows "Q"
    assert sess.current_turn == "P1"
    assert sess.to_dict("P1")["can_choose_rank"] is False
    c1 = sess.hands["P1"][0]
    sess.play_cards("P1", [c1], "Q", 1)
    sess.make_decision("P2", "pass")

    # Turn returns to Leader P2! Pot has 3 cards, but P2 IS THE LEADER!
    assert sess.current_turn == "P2"
    assert sess.trick_leader == "P2"
    # Leader has privilege to change rank!
    assert sess.to_dict("P2")["can_choose_rank"] is True

    # P2 changes rank to "K" -> SUCCEEDS!
    c2_next = sess.hands["P2"][0]
    res_change = sess.play_cards("P2", [c2_next], "K", 1)
    assert res_change["success"] is True
    assert sess.current_round_rank == "K"



