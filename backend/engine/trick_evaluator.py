from typing import List, Tuple, Optional, Dict
from backend.engine.card import Card, Suit, Rank


def get_legal_cards(hand: List[Card], led_suit: Optional[Suit]) -> List[Card]:
    """
    Returns list of legal cards a player can play given their hand and the led suit.
    Must follow suit if holding cards of led suit.
    """
    if not led_suit:
        return list(hand)
    
    same_suit_cards = [c for c in hand if c.suit == led_suit]
    if same_suit_cards:
        return same_suit_cards
    
    # Void in led suit: player can play any card
    return list(hand)


def can_open_trump(
    hand: List[Card],
    led_suit: Optional[Suit],
    trump_revealed: bool,
    hidden_trump_card: Optional[Card],
    mode: str = "Regular"
) -> bool:
    """
    Returns True if the current player has the option to demand/open the trump card.
    Requirements:
    - Mode must be Regular (in Tera/Double Tera, declarer picks trump on first void or at start).
    - Trump must not be revealed yet.
    - Led suit must be active (a card has been led).
    - Player must be void in led suit.
    - Hidden trump card exists.
    """
    if mode != "Regular":
        return False
    if trump_revealed:
        return False
    if not led_suit:
        return False
    if not hidden_trump_card:
        return False
    
    # Must be void in led suit
    same_suit_cards = [c for c in hand if c.suit == led_suit]
    return len(same_suit_cards) == 0


def evaluate_trick(
    plays: List[Tuple[str, Card]],
    led_suit: Suit,
    trump_suit: Optional[Suit],
    trump_revealed: bool
) -> Tuple[str, Card]:
    """
    Determines the winner of a trick.
    plays: list of (player_id, Card) in turn order.
    Returns (winning_player_id, winning_card).
    """
    if not plays:
        raise ValueError("Cannot evaluate an empty trick.")

    winning_player, winning_card = plays[0]

    for player, card in plays[1:]:
        # If trump is revealed and card is trump
        if trump_revealed and trump_suit and card.suit == trump_suit:
            if winning_card.suit == trump_suit:
                if card.rank.value > winning_card.rank.value:
                    winning_player = player
                    winning_card = card
            else:
                # Trump beats any non-trump card
                winning_player = player
                winning_card = card
        # If card follows led suit and winning card is not trump
        elif card.suit == led_suit:
            if not (trump_revealed and trump_suit and winning_card.suit == trump_suit):
                if card.rank.value > winning_card.rank.value:
                    winning_player = player
                    winning_card = card
        # Off-suit discards when winning card is led suit or trump have 0 value
    
    return winning_player, winning_card
