import pytest
from backend.engine.game_session import GameSession
from backend.ai.ollama_client import get_ai_move

def test_full_game_rounds_simulation():
    """Simulates 30 consecutive full 13-trick rounds to ensure zero game stalls or invalid moves."""
    session = GameSession()
    for round_idx in range(1, 31):
        st = session.start_new_round(seed=round_idx * 101)
        if st['deal_stage'] == "SELECT_TRUMP":
            p1_card = st['hands']['P1'][0]['code']
            st = session.select_hidden_trump(p1_card)
        
        move_count = 0
        while not st['round_complete'] and move_count < 100:
            current_p = st['current_turn_player']
            card_code, demand_cut = get_ai_move(st, current_p)
            st = session.play_card(current_p, card_code, demand_cut)
            move_count += 1
            
        assert st['round_complete'] is True, f"Round {round_idx} stalled after {move_count} moves!"
        assert sum(st['team_tricks_won'].values()) <= 13
        dealer_tricks = st['team_tricks_won'][st['dealer_team']]
        lead_tricks = st['team_tricks_won'][st['lead_team']]
        assert dealer_tricks >= 5 or lead_tricks >= 9 or st['trick_number'] >= 13 or st['mode'] in ("Tera", "Double Tera")

if __name__ == "__main__":
    test_full_game_rounds_simulation()
    print("All 30 simulated rounds passed with 0 stalls!")
