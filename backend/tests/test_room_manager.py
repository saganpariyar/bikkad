import pytest
from backend.engine.room_manager import RoomManager
from backend.engine.game_session import GameSession


def test_room_manager_create_and_unique_id():
    rm = RoomManager()
    room1 = rm.create_room(host_name="Sagan", game_name="game1", setup_mode="1-3 com")
    assert len(room1['game_id']) == 4 and room1['game_id'].isdigit()
    assert room1['host_name'] == "Sagan"
    assert room1['setup_mode'] == "1-3 com"
    assert room1['seats']['P1']['name'] == "Sagan"
    assert room1['seats']['P1']['type'] == "human"
    assert room1['seats']['P2']['type'] == "ai"
    assert room1['seats']['P3']['type'] == "ai"
    assert room1['seats']['P4']['type'] == "ai"

    room2 = rm.create_room(host_name="Aarav", game_name="game2", setup_mode="1-3 com")
    assert room1['game_id'] != room2['game_id']


def test_room_manager_2_2_com_and_join():
    rm = RoomManager()
    room = rm.create_room(host_name="Sagan", game_name="game1", setup_mode="2-2 com")
    assert room['seats']['P3']['type'] == "human"  # Open partner seat

    # Friend joins
    res = rm.join_room(room['game_id'], "Priya")
    assert res['success'] is True
    assert res['seat_id'] == "P3"
    assert room['seats']['P3']['name'] == "Priya"
    assert room['seats']['P3']['type'] == "human"


def test_room_manager_seat_reassignment_by_creator():
    rm = RoomManager()
    room = rm.create_room(host_name="Sagan", game_name="game1", setup_mode="3-1 com")
    gid = room['game_id']

    # Creator assigns custom players to P2, P3, P4
    rm.assign_seat(gid, "P2", "Vikram Human", "human")
    rm.assign_seat(gid, "P3", "Sneha Human", "human")
    rm.assign_seat(gid, "P4", "COM Bot Super", "ai")

    updated = rm.get_room(gid)
    assert updated['seats']['P2']['name'] == "Vikram Human"
    assert updated['seats']['P2']['type'] == "human"
    assert updated['seats']['P3']['name'] == "Sneha Human"
    assert updated['seats']['P3']['type'] == "human"
    assert updated['seats']['P4']['name'] == "COM Bot Super"
    assert updated['seats']['P4']['type'] == "ai"


def test_room_start_and_game_session():
    rm = RoomManager()
    room = rm.create_room(host_name="Sagan", game_name="game1", setup_mode="1-3 com")
    gid = room['game_id']

    started_room = rm.start_room(gid)
    assert started_room['status'] == 'playing'

    sess = GameSession(initial_dealer='P1', initial_score=0)
    sess.game_id = gid
    sess.player_names = {s_id: s_info['name'] for s_id, s_info in started_room['seats'].items()}
    sess.player_types = {s_id: s_info['type'] for s_id, s_info in started_room['seats'].items()}
    state = sess.start_new_round(mode="Regular")

    assert state['pot_card_count'] == 0
    assert state['pot_trick_count'] == 0
    assert state['game_id'] == gid
    assert state['player_names']['P1'] == "Sagan"


def test_trump_hider_selection_for_first_deal():
    """Verify player 1, 2, 3, 4 or random selection correctly sets eldest hand & trick leader."""
    rm = RoomManager()

    # 1. P1 selected to hide trump -> Dealer is P4 -> Eldest hand is P1
    d_p1 = rm.resolve_initial_dealer("P1")
    assert d_p1 == "P4"
    sess_p1 = GameSession(initial_dealer=d_p1, initial_score=0)
    st_p1 = sess_p1.start_new_round(mode="Regular")
    assert sess_p1.eldest_hand == "P1"
    assert st_p1["eldest_hand"] == "P1"
    assert st_p1["deal_stage"] == "SELECT_TRUMP"  # Human P1 gets 5 cards to hide trump

    # 2. P2 selected to hide trump -> Dealer is P1 -> Eldest hand is P2
    d_p2 = rm.resolve_initial_dealer("P2")
    assert d_p2 == "P1"
    sess_p2 = GameSession(initial_dealer=d_p2, initial_score=0)
    st_p2 = sess_p2.start_new_round(mode="Regular")
    assert sess_p2.eldest_hand == "P2"
    assert st_p2["eldest_hand"] == "P2"
    assert st_p2["current_turn_player"] == "P2"  # P2 leads trick 1

    # 3. P3 selected to hide trump -> Dealer is P2 -> Eldest hand is P3
    d_p3 = rm.resolve_initial_dealer("P3")
    assert d_p3 == "P2"
    sess_p3 = GameSession(initial_dealer=d_p3, initial_score=0)
    st_p3 = sess_p3.start_new_round(mode="Regular")
    assert sess_p3.eldest_hand == "P3"
    assert st_p3["eldest_hand"] == "P3"
    assert st_p3["current_turn_player"] == "P3"  # P3 leads trick 1

    # 4. P4 selected to hide trump -> Dealer is P3 -> Eldest hand is P4
    d_p4 = rm.resolve_initial_dealer("P4")
    assert d_p4 == "P3"
    sess_p4 = GameSession(initial_dealer=d_p4, initial_score=0)
    st_p4 = sess_p4.start_new_round(mode="Regular")
    assert sess_p4.eldest_hand == "P4"
    assert st_p4["eldest_hand"] == "P4"
    assert st_p4["current_turn_player"] == "P4"  # P4 leads trick 1

    # 5. Random selection
    d_rand = rm.resolve_initial_dealer("random")
    assert d_rand in ["P1", "P2", "P3", "P4"]


def test_room_manager_custom_seats_config():
    rm = RoomManager()
    # Creator chooses P2 to be human friend, P3 and P4 to be AI
    room = rm.create_room(
        host_name="Sagan",
        game_name="game1",
        seats_config={'P2': 'human', 'P3': 'ai', 'P4': 'ai'}
    )
    assert room['seats']['P1']['type'] == 'human'
    assert room['seats']['P2']['type'] == 'human'
    assert room['seats']['P3']['type'] == 'ai'
    assert room['seats']['P4']['type'] == 'ai'

    # Friend joins - should get P2
    res = rm.join_room(room['game_id'], "Priya")
    assert res['seat_id'] == 'P2'
    assert room['seats']['P2']['name'] == 'Priya'


def test_room_manager_same_name_player_join():
    rm = RoomManager()
    # Host is Sagan, P3 is human
    room = rm.create_room(
        host_name="Sagan",
        game_name="game1",
        seats_config={'P2': 'ai', 'P3': 'human', 'P4': 'ai'}
    )
    # Friend also named Sagan joins!
    res = rm.join_room(room['game_id'], "Sagan")
    # Must NOT get assigned to host seat P1!
    assert res['seat_id'] != 'P1'
    assert res['seat_id'] == 'P3'
    assert room['seats']['P3']['name'] == 'Sagan'
    assert room['seats']['P1']['name'] == 'Sagan'
    assert room['seats']['P1']['is_host'] is True

