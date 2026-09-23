"""
Bindi Coat (Mindikot / Bandh Hukum) AI — Heuristic bot players.
Covers: Bandh Hukum (trump) card selection and trick-play card selection.
"""
from typing import List, Dict, Optional, Tuple


# Rank values: 2=2 ... A=14
RANK_VALUES = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8,
    '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14
}

SUITS = ['H', 'D', 'C', 'S']


def card_rank(code: str) -> int:
    """Numeric rank from card code like '10H', 'KS'."""
    rank_str = code[:-1]
    return RANK_VALUES.get(rank_str, 0)


def card_suit(code: str) -> str:
    """Suit letter from card code."""
    return code[-1]


def is_mindi(code: str) -> bool:
    """A Mindi is any 10 (rank '10')."""
    return code[:-1] == '10'


def get_legal_moves(
    hand: List[str],
    led_suit: Optional[str],
    trump_revealed: bool,
    trump_suit: Optional[str],
    is_leading: bool
) -> List[str]:
    """
    Returns the list of legal cards for the player to play.

    - Leading: any card.
    - Following with led_suit cards: must follow suit.
    - Void in led suit: any card (triggers trump reveal if not yet revealed).
    """
    if is_leading or led_suit is None:
        return list(hand)

    suited = [c for c in hand if card_suit(c) == led_suit]
    if suited:
        return suited
    # Void in led suit — can play anything
    return list(hand)


def select_bandh_hukum(hand_5: List[str]) -> str:
    """
    AI selects which card from the initial 5 to place as hidden trump.

    Strategy: Choose the card whose suit gives the most strength overall.
    Strength = (suit count × 3) + high card points (A=4, K=3, Q=2, J=1).
    Keeps the chosen card as the trump placer's advantage.
    """
    hcp = {'A': 4, 'K': 3, 'Q': 2, 'J': 1}
    suit_scores: Dict[str, float] = {s: 0.0 for s in SUITS}
    suit_counts: Dict[str, int] = {s: 0 for s in SUITS}

    for code in hand_5:
        s = card_suit(code)
        r = code[:-1]
        suit_counts[s] += 1
        suit_scores[s] += hcp.get(r, 0.0)

    # Pick the best suit
    best_suit = max(SUITS, key=lambda s: suit_counts[s] * 3.0 + suit_scores[s])

    # From that suit, pick a mid-value card to place face-down
    # (keep highest honors in hand; place a mid card that determines trump)
    suit_cards = sorted(
        [c for c in hand_5 if card_suit(c) == best_suit],
        key=card_rank
    )
    # If we have 2+ cards of best suit, place the second-lowest (save the high for play)
    if len(suit_cards) >= 2:
        return suit_cards[1]  # place mid-value
    # If only 1 card of best suit, it becomes the trump card
    return suit_cards[0]


def select_play_card(
    hand: List[str],
    legal_moves: List[str],
    current_trick: List[Dict],
    trump_suit: Optional[str],
    trump_revealed: bool,
    partner_id: Optional[str],
    is_leading: bool,
    mindi_in_trick: bool,
) -> str:
    """
    AI selects which card to play on its turn.

    Args:
        hand: Bot's full hand.
        legal_moves: Cards the bot is allowed to play (must pick from this list).
        current_trick: List of {player_id, card_code} dicts already played in trick.
        trump_suit: Active trump suit (if revealed).
        trump_revealed: Whether the hidden trump has been revealed.
        partner_id: Bot's partner player ID (for partnership awareness).
        is_leading: True if this bot is leading the trick.
        mindi_in_trick: True if a Mindi (10) is already in the current trick pile.

    Returns:
        Card code to play.
    """
    if not legal_moves:
        return hand[0]
    if len(legal_moves) == 1:
        return legal_moves[0]

    # ── Leading ──────────────────────────────────────────────────────────────
    if is_leading:
        # 1. Lead Aces first (except trump Ace if trump not revealed yet — save mystery)
        aces = [c for c in legal_moves if c[:-1] == 'A']
        non_trump_aces = [c for c in aces if card_suit(c) != trump_suit]
        if non_trump_aces:
            return non_trump_aces[0]
        if aces:
            return aces[0]

        # 2. Lead Kings of non-trump
        kings = [c for c in legal_moves if c[:-1] == 'K' and card_suit(c) != trump_suit]
        if kings:
            return kings[0]

        # 3. Lead low card to let partner win / draw out
        sorted_moves = sorted(legal_moves, key=card_rank)
        return sorted_moves[0]

    # ── Following ─────────────────────────────────────────────────────────────

    # Determine who's currently winning the trick
    winning_card, winning_player = _trick_winner(current_trick, trump_suit)
    partner_winning = (winning_player == partner_id)

    # ── Partner is winning the trick ──────────────────────────────────────────
    if partner_winning:
        # Throw a Mindi (10) if possible — partner will secure it
        mindis_in_legal = [c for c in legal_moves if is_mindi(c)]
        if mindis_in_legal:
            return mindis_in_legal[0]
        # Otherwise throw the highest legal card to support
        return max(legal_moves, key=card_rank)

    # ── Opponent winning the trick ────────────────────────────────────────────
    # Try to beat the current winner
    beating_cards = [c for c in legal_moves if _beats(c, winning_card, trump_suit)]
    if beating_cards:
        # If trick has a Mindi, use a secure trump to win it
        if mindi_in_trick:
            trump_beats = [c for c in beating_cards if trump_suit and card_suit(c) == trump_suit]
            if trump_beats:
                return min(trump_beats, key=card_rank)
        # Otherwise play lowest beating card
        return min(beating_cards, key=card_rank)

    # Cannot beat: dump the lowest-value non-Mindi card
    non_mindis = [c for c in legal_moves if not is_mindi(c)]
    if non_mindis:
        return min(non_mindis, key=card_rank)
    # All legal moves are Mindis — dump the lowest
    return min(legal_moves, key=card_rank)


def _beats(card: str, current_winner: str, trump_suit: Optional[str]) -> bool:
    """Returns True if `card` beats `current_winner` given trump_suit."""
    if not current_winner:
        return True
    c_suit = card_suit(card)
    w_suit = card_suit(current_winner)

    if c_suit == w_suit:
        return card_rank(card) > card_rank(current_winner)
    if trump_suit and c_suit == trump_suit and w_suit != trump_suit:
        return True
    return False


def _trick_winner(trick: List[Dict], trump_suit: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """
    Returns (winning_card_code, winning_player_id) for the current trick state.
    """
    if not trick:
        return None, None

    led_suit = card_suit(trick[0]['card'])
    best = trick[0]

    for entry in trick[1:]:
        c = entry['card']
        w = best['card']
        c_suit = card_suit(c)
        w_suit = card_suit(w)

        if c_suit == w_suit and card_rank(c) > card_rank(w):
            best = entry
        elif trump_suit and c_suit == trump_suit and w_suit != trump_suit:
            best = entry

    return best['card'], best['player_id']
