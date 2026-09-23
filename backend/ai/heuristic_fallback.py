from typing import List, Optional, Tuple, Dict, Any
from backend.engine.card import Card, Suit, Rank
from backend.engine.trick_evaluator import get_legal_cards, can_open_trump, evaluate_trick


def select_hidden_trump_heuristic(hand_5: List[Card]) -> Card:
    """
    Selects hidden trump from 5 initial cards.
    Prefers strongest suit (most cards, highest rank).
    """
    suit_counts: Dict[Suit, int] = {}
    for c in hand_5:
        suit_counts[c.suit] = suit_counts.get(c.suit, 0) + 1

    sorted_cards = sorted(hand_5, key=lambda c: (-suit_counts[c.suit], -c.rank.value))
    return sorted_cards[0]


def select_runtime_trump_heuristic(hand: List[Card]) -> str:
    """
    Selects runtime trump suit for Declarer on first void in Tera / Double Tera.
    Returns suit string ('S', 'H', 'D', 'C').
    """
    suit_counts: Dict[Suit, int] = {}
    suit_ranks: Dict[Suit, int] = {}
    
    for c in hand:
        suit_counts[c.suit] = suit_counts.get(c.suit, 0) + 1
        suit_ranks[c.suit] = suit_ranks.get(c.suit, 0) + c.rank.value

    best_suit = max(Suit, key=lambda s: (suit_counts.get(s, 0), suit_ranks.get(s, 0)))
    return best_suit.value


def evaluate_bidding_heuristic(hand: List[Card]) -> str:
    """
    Evaluates whether an AI player should declare Tera or Double Tera.
    Requires an exceptional hand (high cards / Aces & Kings count).
    """
    top_cards = [c for c in hand if c.rank in (Rank.ACE, Rank.KING, Rank.QUEEN)]
    aces = [c for c in hand if c.rank == Rank.ACE]
    
    if len(hand) == 13 and len(top_cards) >= 11 and len(aces) >= 3:
        return "Double Tera"
    elif len(hand) == 13 and len(top_cards) >= 9 and len(aces) >= 2:
        return "Tera"
    
    return "Regular"


def choose_move_heuristic(
    player_id: str,
    hand: List[Card],
    led_suit: Optional[Suit],
    trump_suit: Optional[Suit],
    trump_revealed: bool,
    current_trick: List[Tuple[str, Card]],
    hidden_trump_card: Optional[Card],
    mode: str,
    pot_size: int,
    streak_holder: Optional[str],
    streak_count: int,
    player_teams: Dict[str, str],
    hidden_trump_setter: Optional[str] = None
) -> Tuple[str, bool]:
    """
    Selects card code to play and whether to demand cut (open trump).
    Returns: (card_code: str, demand_cut: bool)
    """
    my_team = player_teams[player_id]
    legal_cards = get_legal_cards(hand, led_suit)
    demand_cut = False

    # Void in led suit check
    if led_suit and len([c for c in hand if c.suit == led_suit]) == 0:
        if mode == "Regular":
            if can_open_trump(hand, led_suit, trump_revealed, hidden_trump_card, mode):
                is_partner_winning = False
                if current_trick:
                    winning_player, _ = evaluate_trick(current_trick, led_suit, trump_suit, trump_revealed)
                    if player_teams.get(winning_player) == my_team:
                        is_partner_winning = True

                if pot_size >= 8 or not is_partner_winning or streak_holder != my_team:
                    demand_cut = True
                    if hidden_trump_card:
                        trump_cards = [c for c in hand if c.suit == hidden_trump_card.suit]
                        # If this player is the hidden trump setter, hidden_trump_card returns upon cut!
                        if hidden_trump_setter == player_id and not any(c.code == hidden_trump_card.code for c in trump_cards):
                            trump_cards.append(hidden_trump_card)
                        if trump_cards:
                            legal_cards = trump_cards
        elif mode in ("Tera", "Double Tera"):
            if not trump_revealed:
                demand_cut = True
            elif trump_suit:
                trump_cards = [c for c in hand if c.suit == trump_suit]
                if trump_cards:
                    legal_cards = trump_cards

    if not legal_cards:
        legal_cards = list(hand)

    # 1. Leading the trick
    if not current_trick or not led_suit:
        high_aces = [c for c in legal_cards if c.rank == Rank.ACE]
        if high_aces:
            return high_aces[0].code, demand_cut

        if streak_holder == my_team and streak_count == 1:
            high_kings = [c for c in legal_cards if c.rank == Rank.KING]
            if high_kings:
                return high_kings[0].code, demand_cut

        suit_counts: Dict[Suit, int] = {}
        for c in hand:
            suit_counts[c.suit] = suit_counts.get(c.suit, 0) + 1

        sorted_cards = sorted(legal_cards, key=lambda c: (-suit_counts[c.suit], -c.rank.value))
        return sorted_cards[0].code, demand_cut

    # 2. Responding to trick
    winning_player, winning_card = evaluate_trick(current_trick, led_suit, trump_suit, trump_revealed or demand_cut)
    is_partner_winning = (player_teams.get(winning_player) == my_team)

    if is_partner_winning:
        sorted_legal = sorted(legal_cards, key=lambda c: c.rank.value)
        return sorted_legal[0].code, demand_cut
    else:
        winning_moves = []
        for c in legal_cards:
            temp_trick = list(current_trick) + [(player_id, c)]
            eff_trump_suit = hidden_trump_card.suit if (demand_cut and hidden_trump_card) else trump_suit
            w_player, _ = evaluate_trick(temp_trick, led_suit, eff_trump_suit, trump_revealed or demand_cut)
            if w_player == player_id:
                winning_moves.append(c)

        if winning_moves:
            sorted_win = sorted(winning_moves, key=lambda c: c.rank.value)
            return sorted_win[0].code, demand_cut

        sorted_legal = sorted(legal_cards, key=lambda c: c.rank.value)
        return sorted_legal[0].code, demand_cut
