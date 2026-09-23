from fastapi.testclient import TestClient
from backend.server import app

client = TestClient(app)

def post(endpoint, data):
    path = endpoint.replace("http://127.0.0.1:8000", "")
    res = client.post(path, json=data)
    assert res.status_code == 200, f"POST failed: {res.text}"
    return res.json()

def get(endpoint):
    path = endpoint.replace("http://127.0.0.1:8000", "")
    res = client.get(path)
    assert res.status_code == 200, f"GET failed: {res.text}"
    return res.json()

def test_full_4_human_flow():
    game_id = "BIK-4444"
    
    print("=====================================================================")
    print("STEP 1: Host 'Sagan' initializes Room BIK-4444 in 4-0 COM mode")
    print("=====================================================================")
    create_res = post("http://127.0.0.1:8000/api/room/create", {
        "game_id": game_id,
        "host_name": "Sagan",
        "game_name": "HumanArena",
        "setup_mode": "4-0 com",
        "trump_hider": "P1"
    })
    room = create_res["room"]
    print(f"[OK] Room created with ID: {room['game_id']}")
    print(f"  Mode: {room['setup_mode']}, Host: {room['host_name']}")
    for sid, s in room["seats"].items():
        print(f"  - Seat {sid} ({s['position']}): {s['name']} [type: {s['type']}, connected: {s['connected']}]")

    print("\n=====================================================================")
    print("STEP 2: 3 Other Human Players Join Using Room Code 'BIK-4444'")
    print("=====================================================================")
    # Priya joins
    j_priya = post("http://127.0.0.1:8000/api/room/join", {
        "game_id": game_id,
        "player_name": "Priya"
    })
    print(f"[OK] Priya joined -> Assigned to Seat {j_priya['seat_id']} ({j_priya['room']['seats'][j_priya['seat_id']]['position']})")

    # Aarav joins
    j_aarav = post("http://127.0.0.1:8000/api/room/join", {
        "game_id": game_id,
        "player_name": "Aarav"
    })
    print(f"[OK] Aarav joined -> Assigned to Seat {j_aarav['seat_id']} ({j_aarav['room']['seats'][j_aarav['seat_id']]['position']})")

    # Rohan joins
    j_rohan = post("http://127.0.0.1:8000/api/room/join", {
        "game_id": game_id,
        "player_name": "Rohan"
    })
    print(f"[OK] Rohan joined -> Assigned to Seat {j_rohan['seat_id']} ({j_rohan['room']['seats'][j_rohan['seat_id']]['position']})")

    print("\n=====================================================================")
    print("STEP 3: Host polls /api/room/status to confirm all 4 players in lobby")
    print("=====================================================================")
    status_res = get(f"http://127.0.0.1:8000/api/room/status?game_id={game_id}")
    cur_room = status_res["room"]
    for sid, s in cur_room["seats"].items():
        assert s["connected"] is True, f"Seat {sid} should be connected!"
        assert s["type"] == "human", f"Seat {sid} must be human!"
        print(f"  [OK] Seat {sid} ({s['position']}): {s['name']} [CONNECTED & READY]")

    print("\n=====================================================================")
    print("STEP 4: Host Sagan Clicks 'Start Match'")
    print("=====================================================================")
    start_res = post("http://127.0.0.1:8000/api/room/start", {
        "game_id": game_id,
        "trump_hider": "P1"
    })
    state = start_res["state"]
    print(f"[OK] Match launched! Stage: {state['deal_stage']}, Turn: {state['current_turn_player']}")
    print(f"  Player types: {state['player_types']}")
    print(f"  Player names: {state['player_names']}")
    assert all(ptype == "human" for ptype in state["player_types"].values()), "All players must be human!"

    print("\n=====================================================================")
    print("STEP 5: Player 1 (Sagan) Hides Trump Card")
    print("=====================================================================")
    p1_first_card = state["hands"]["P1"][0]["code"]
    print(f"  Sagan selects card '{p1_first_card}' to place under saucer as Hidden Trump")
    state_after_hide = post("http://127.0.0.1:8000/api/select_hidden_trump", {
        "game_id": game_id,
        "card_code": p1_first_card
    })
    print(f"[OK] Trump hidden! Hidden card: {state_after_hide['hidden_trump_card']['code']}, Revealed: {state_after_hide['trump_revealed']}")
    print(f"  Sagan hand count: {len(state_after_hide['hands']['P1'])} cards (12 cards held while hidden)")
    assert len(state_after_hide['hands']['P1']) == 12, "Sagan hand must have 12 cards while trump is hidden!"
    assert state_after_hide["deal_stage"] == "READY", "Deal stage must be READY!"

    print("\n=====================================================================")
    print("STEP 6: Trick 1 - All 4 Human Players Play Clockwise in Real Time")
    print("=====================================================================")
    cur_state = state_after_hide
    for step in range(4):
        turn_player = cur_state["current_turn_player"]
        turn_name = cur_state["player_names"][turn_player]
        led = cur_state["led_suit"]
        hand = cur_state["hands"][turn_player]
        
        # Pick legal card
        same_suit = [c for c in hand if c["suit"] == led] if led else hand
        chosen_card = (same_suit or hand)[0]["code"]
        
        print(f"  [{step+1}/4] Turn: {turn_player} ({turn_name}) plays legal card: {chosen_card}")
        cur_state = post("http://127.0.0.1:8000/api/play", {
            "game_id": game_id,
            "player_id": turn_player,
            "card_code": chosen_card,
            "demand_cut": False
        })

    print("\n=====================================================================")
    print("STEP 7: Trick 1 Outcome & Pot Accumulator Verification")
    print("=====================================================================")
    print(f"[OK] Trick 1 Finished!")
    print(f"  Pot Cards Accumulated: {cur_state['pot_card_count']} cards")
    print(f"  Pot Tricks Accumulated: {cur_state['pot_trick_count']} tricks")
    print(f"  Next Trick Lead: {cur_state['current_turn_player']} ({cur_state['player_names'][cur_state['current_turn_player']]})")
    print(f"  Recent Game Logs:\n    " + "\n    ".join(cur_state['logs'][-3:]))

    assert cur_state['pot_card_count'] == 4, "Pot must have 4 cards after trick 1!"
    assert cur_state['pot_trick_count'] == 1, "Pot must have 1 trick after trick 1!"

    print("\n=====================================================================")
    print("SUCCESS: 4 HUMAN PLAYERS SUCCESSFULLY CONNECTED AND PLAYED TOGETHER!")
    print("=====================================================================")

if __name__ == "__main__":
    test_full_4_human_flow()
