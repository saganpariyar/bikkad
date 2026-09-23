import json
import urllib.request
import urllib.error
from typing import Dict, Any, Tuple, Optional
from backend.engine.card import Card, Suit
from backend.ai.prompt_builder import build_ollama_prompt
from backend.ai.heuristic_fallback import choose_move_heuristic


def get_ai_move(
    game_state: Dict[str, Any],
    player_id: str,
    ollama_url: str = "http://localhost:11434/api/generate",
    model: str = "llama3",
    use_ollama: bool = False
) -> Tuple[str, bool]:
    """
    Determines card code and demand_cut flag for AI player.
    Tries Ollama first if enabled. Falls back gracefully to heuristic AI.
    """
    player_hand_dicts = game_state['hands'].get(player_id, [])
    hand = [Card.from_code(c['code']) for c in player_hand_dicts]
    led_suit = Suit(game_state['led_suit']) if game_state.get('led_suit') else None
    trump_suit = Suit(game_state['trump_suit']) if game_state.get('trump_suit') else None
    hidden_trump_card = Card.from_code(game_state['hidden_trump_card']['code']) if game_state.get('hidden_trump_card') else None
    
    current_trick = [
        (play['player_id'], Card.from_code(play['card']['code']))
        for play in game_state.get('current_trick', [])
    ]
    
    player_teams = {'P1': 'Team A', 'P3': 'Team A', 'P2': 'Team B', 'P4': 'Team B'}

    if use_ollama:
        try:
            prompt = build_ollama_prompt(game_state, player_id)
            payload = json.dumps({
                "model": model,
                "prompt": prompt,
                "stream": False,
                "format": "json"
            }).encode('utf-8')

            req = urllib.request.Request(
                ollama_url,
                data=payload,
                headers={"Content-Type": "application/json"}
            )

            with urllib.request.urlopen(req, timeout=1.5) as resp:
                result = json.loads(resp.read().decode('utf-8'))
                response_text = result.get('response', '')
                parsed = json.loads(response_text)
                
                card_code = parsed.get('card')
                demand_cut = bool(parsed.get('demand_cut', False))

                # Verify card code is valid in hand
                if any(c.code == card_code for c in hand):
                    return card_code, demand_cut

        except Exception as e:
            # Ollama failed or offline -> fall back silently
            pass

    # Heuristic Fallback
    return choose_move_heuristic(
        player_id=player_id,
        hand=hand,
        led_suit=led_suit,
        trump_suit=trump_suit,
        trump_revealed=game_state.get('trump_revealed', False),
        current_trick=current_trick,
        hidden_trump_card=hidden_trump_card,
        mode=game_state.get('mode', 'Regular'),
        pot_size=game_state.get('pot_card_count', 0),
        streak_holder=game_state.get('pot_streak_holder'),
        streak_count=game_state.get('pot_streak_count', 0),
        player_teams=player_teams,
        hidden_trump_setter=game_state.get('hidden_trump_setter')
    )
