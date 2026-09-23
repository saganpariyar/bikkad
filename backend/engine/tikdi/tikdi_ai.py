from typing import List, Dict, Optional, Tuple
from backend.engine.card import Card, Suit, Rank


def select_tikdi_trump(hand_5_cards: List[Card]) -> str:
    """
    Heuristic for Trump Chooser AI evaluating the initial 5 cards:
    Evaluates suit strength based on card count and high card points (A=4, K=3, Q=2, J=1, 10=0.5).
    """
    suit_scores = {s.value: 0.0 for s in Suit}
    suit_counts = {s.value: 0 for s in Suit}

    hcp_weights = {
        Rank.ACE: 4.0,
        Rank.KING: 3.0,
        Rank.QUEEN: 2.0,
        Rank.JACK: 1.0,
        Rank.TEN: 0.5,
    }

    for card in hand_5_cards:
        s = card.suit.value
        suit_counts[s] += 1
        suit_scores[s] += hcp_weights.get(card.rank, 0.0)

    # Combined score = (Count * 3.0) + HCP
    best_suit = 'S'
    best_score = -1.0
    for s, count in suit_counts.items():
        score = (count * 3.0) + suit_scores[s]
        if score > best_score:
            best_score = score
            best_suit = s

    return best_suit


def select_penalty_return_card(hand: List[Card], trump_suit: str) -> Card:
    """
    Heuristic for Creditor returning an unwanted card to Debtor:
    Gives back the lowest ranked non-trump card. If all are trump, returns lowest trump.
    """
    non_trumps = [c for c in hand if c.suit.value != trump_suit]
    if non_trumps:
        # Sort by rank ascending (lowest first)
        non_trumps.sort(key=lambda c: c.rank.value)
        return non_trumps[0]
    
    # If only trumps remain, return lowest trump
    sorted_hand = sorted(hand, key=lambda c: c.rank.value)
    return sorted_hand[0]


def evaluate_trick_winner(current_trick: List[Dict], trump_suit: str) -> Tuple[int, Card]:
    """Helper to evaluate current winning play in trick."""
    if not current_trick:
        return -1, None
    led_suit = current_trick[0]['card'].suit.value
    winning_idx = 0
    winning_card = current_trick[0]['card']

    for i in range(1, len(current_trick)):
        candidate = current_trick[i]['card']
        if candidate.suit.value == winning_card.suit.value:
            if candidate.rank.value > winning_card.rank.value:
                winning_card = candidate
                winning_idx = i
        elif candidate.suit.value == trump_suit and winning_card.suit.value != trump_suit:
            winning_card = candidate
            winning_idx = i

    return winning_idx, winning_card


def select_tikdi_bot_play(
    hand: List[Card],
    legal_cards: List[Card],
    current_trick: List[Dict],
    trump_suit: str,
    led_suit: Optional[str]
) -> Card:
    """
    Strategic 3-player trick play AI for Tikdi:
    - 10 tricks total.
    - If leading: Leads cash Ace, or long suit high card.
    - If following: Plays minimum card needed to win, or lowest slough if cannot win.
    """
    if not legal_cards:
        return hand[0] if hand else None

    # Only 1 legal option
    if len(legal_cards) == 1:
        return legal_cards[0]

    # CASE 1: Leading the trick
    if not current_trick:
        # Prefer leading Ace in non-trump or trump
        aces = [c for c in legal_cards if c.rank == Rank.ACE]
        if aces:
            return aces[0]
        # Prefer high card in longest suit
        suit_counts = {}
        for c in hand:
            suit_counts[c.suit.value] = suit_counts.get(c.suit.value, 0) + 1
        sorted_legal = sorted(legal_cards, key=lambda c: (suit_counts.get(c.suit.value, 0), c.rank.value), reverse=True)
        return sorted_legal[0]

    # CASE 2: Following in trick
    win_idx, win_card = evaluate_trick_winner(current_trick, trump_suit)

    # Separate winning moves from non-winning moves
    winning_moves = []
    losing_moves = []

    for c in legal_cards:
        if c.suit.value == win_card.suit.value:
            if c.rank.value > win_card.rank.value:
                winning_moves.append(c)
            else:
                losing_moves.append(c)
        elif c.suit.value == trump_suit and win_card.suit.value != trump_suit:
            winning_moves.append(c)
        else:
            losing_moves.append(c)

    if winning_moves:
        # Play lowest winning card to conserve high cards
        winning_moves.sort(key=lambda c: c.rank.value)
        return winning_moves[0]
    else:
        # Cannot win trick: dump lowest card
        losing_moves.sort(key=lambda c: c.rank.value)
        return losing_moves[0]
