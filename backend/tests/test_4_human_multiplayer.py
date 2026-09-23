from fastapi.testclient import TestClient
from backend.server import app

client = TestClient(app)

def post(endpoint, data):
    path = endpoint.replace('http://127.0.0.1:8000', '')
    res = client.post(path, json=data)
    assert res.status_code == 200, f"Request failed: {res.text}"
    return res.json()

def test_4_human_match():
    # 1. Host (Sagan) creates game room in 4-0 com mode
    print("=== Step 1: Host creates room in 4-0 com mode ===")
    create_res = post('http://127.0.0.1:8000/api/room/create', {
        'host_name': 'Sagan',
        'game_name': 'MultiTest',
        'setup_mode': '4-0 com',
        'trump_hider': 'P1'
    })
    game_id = create_res['game_id']
    print(f"Created Room ID: {game_id}")
    for k, v in create_res['room']['seats'].items():
        print(f"  Seat {k}: {v['name']} ({v['type']}, {v['position']})")

    # 2. 3 other humans join using Room ID
    print("\n=== Step 2: 3 other human players join ===")
    j1 = post('http://127.0.0.1:8000/api/room/join', {'game_id': game_id, 'player_name': 'Aarav'})
    print(f"  Joined: {j1['player_name']} -> Seat {j1['seat_id']}")
    j2 = post('http://127.0.0.1:8000/api/room/join', {'game_id': game_id, 'player_name': 'Priya'})
    print(f"  Joined: {j2['player_name']} -> Seat {j2['seat_id']}")
    j3 = post('http://127.0.0.1:8000/api/room/join', {'game_id': game_id, 'player_name': 'Rohan'})
    print(f"  Joined: {j3['player_name']} -> Seat {j3['seat_id']}")

    # 3. Host starts room
    print("\n=== Step 3: Host launches table match ===")
    start_res = post('http://127.0.0.1:8000/api/room/start', {'game_id': game_id, 'trump_hider': 'P1'})
    state = start_res['state']
    print(f"Match Started! Deal Stage: {state['deal_stage']}, Turn: {state['current_turn_player']}")
    print(f"Player types: {state['player_types']}")
    print(f"Player names: {state['player_names']}")
    assert all(ptype == 'human' for ptype in state['player_types'].values()), "All 4 seats must be human!"

    # 4. P1 (Sagan) selects hidden trump
    print("\n=== Step 4: Sagan selects hidden trump card ===")
    p1_card = state['hands']['P1'][0]['code']
    print(f"  Sagan selects card {p1_card} to hide as Trump")
    state2 = post('http://127.0.0.1:8000/api/select_hidden_trump', {'card_code': p1_card, 'game_id': game_id})
    print(f"  After hiding -> Stage: {state2['deal_stage']}, Turn: {state2['current_turn_player']}")
    print(f"  Sagan hand count: {len(state2['hands']['P1'])} (12 cards while hidden)")
    print(f"  Hidden Trump: {state2['hidden_trump_card']['code']}, Revealed: {state2['trump_revealed']}")

    # 5. Play Trick 1 with all 4 human players
    print("\n=== Step 5: All 4 humans play cards in clockwise order ===")
    for step in range(4):
        turn_player = state2['current_turn_player']
        player_name = state2['player_names'][turn_player]
        led = state2['led_suit']
        hand = state2['hands'][turn_player]
        same_suit = [c for c in hand if c['suit'] == led] if led else hand
        card_to_play = (same_suit or hand)[0]['code']
        print(f"  Step {step+1}: Player {turn_player} ({player_name}) plays card {card_to_play}")
        state2 = post('http://127.0.0.1:8000/api/play', {
            'player_id': turn_player,
            'card_code': card_to_play,
            'demand_cut': False,
            'game_id': game_id
        })

    print(f"\nTrick 1 Finished! Next Turn Player: {state2['current_turn_player']} ({state2['player_names'][state2['current_turn_player']]})")
    print(f"Center Pot Cards: {state2['pot_card_count']}, Pot Tricks: {state2['pot_trick_count']}")
    print(f"Logs: {state2['logs'][-2:]}")
    print("\n>>> ALL 4 HUMANS JOINED AND PLAYED SUCCESSFULLY! <<<")

if __name__ == '__main__':
    test_4_human_match()
