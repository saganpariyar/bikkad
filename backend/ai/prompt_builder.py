import json
from typing import Dict, Any, List
from backend.engine.card import Card, Suit
from backend.engine.trick_evaluator import get_legal_cards, can_open_trump


def build_ollama_prompt(game_state: Dict[str, Any], player_id: str) -> str:
    """
    Constructs a compact JSON prompt for Ollama AI model.
    """
    player_hand_dicts = game_state['hands'].get(player_id, [])
    hand_codes = [c['code'] for c in player_hand_dicts]
    
    led_suit = game_state.get('led_suit')
    
    # Calculate legal card codes
    hand_cards = [Card.from_code(code) for code in hand_codes]
    led_suit_obj = Suit(led_suit) if led_suit else None
    legal_cards = get_legal_cards(hand_cards, led_suit_obj)
    legal_codes = [c.code for c in legal_cards]

    context = {
        "task": "Choose the best card to play in Bikkad card game.",
        "player_id": player_id,
        "mode": game_state.get('mode', 'Regular'),
        "dealer_id": game_state.get('dealer_id'),
        "dealer_score": game_state.get('dealer_score'),
        "hand": hand_codes,
        "legal_moves": legal_codes,
        "led_suit": led_suit,
        "trump_suit": game_state.get('trump_suit'),
        "trump_revealed": game_state.get('trump_revealed', False),
        "pot_size": game_state.get('pot_card_count', 0),
        "streak_holder": game_state.get('pot_streak_holder'),
        "streak_count": game_state.get('pot_streak_count', 0),
        "current_trick": [
            {"player": play['player_id'], "card": play['card']['code']}
            for play in game_state.get('current_trick', [])
        ]
    }

    instructions = (
        "Respond ONLY with a valid JSON object strictly matching this format:\n"
        "{\"card\": \"<CARD_CODE>\", \"demand_cut\": false}\n"
        "Example: {\"card\": \"AS\", \"demand_cut\": false}\n"
        "The card field MUST be one of the codes listed in legal_moves."
    )

    return f"Context:\n{json.dumps(context, indent=2)}\n\nInstructions:\n{instructions}"
