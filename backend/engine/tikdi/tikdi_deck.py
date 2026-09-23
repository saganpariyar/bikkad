import random
from typing import List, Dict, Tuple
from backend.engine.card import Card, Suit, Rank


TIKDI_RANKS_HEARTS_SPADES = [
    Rank.SEVEN, Rank.EIGHT, Rank.NINE, Rank.TEN,
    Rank.JACK, Rank.QUEEN, Rank.KING, Rank.ACE
]

TIKDI_RANKS_CLUBS_DIAMONDS = [
    Rank.EIGHT, Rank.NINE, Rank.TEN,
    Rank.JACK, Rank.QUEEN, Rank.KING, Rank.ACE
]


def create_tikdi_deck() -> List[Card]:
    """
    Creates the official 30-card stripped deck for Tikdi (3-2-5 / Teen Do Paanch):
    - Hearts: 7, 8, 9, 10, J, Q, K, A (8 cards)
    - Spades: 7, 8, 9, 10, J, Q, K, A (8 cards)
    - Clubs: 8, 9, 10, J, Q, K, A (7 cards)
    - Diamonds: 8, 9, 10, J, Q, K, A (7 cards)
    Total: exactly 30 cards.
    """
    cards: List[Card] = []
    
    # Hearts & Spades (includes 7)
    for rank in TIKDI_RANKS_HEARTS_SPADES:
        cards.append(Card(rank, Suit.HEARTS))
        cards.append(Card(rank, Suit.SPADES))
        
    # Clubs & Diamonds (8 through Ace, no 7)
    for rank in TIKDI_RANKS_CLUBS_DIAMONDS:
        cards.append(Card(rank, Suit.CLUBS))
        cards.append(Card(rank, Suit.DIAMONDS))

    return cards


class TikdiDeck:
    def __init__(self, cards: List[Card] = None):
        if cards is not None:
            self.cards = list(cards)
        else:
            self.cards = create_tikdi_deck()
            self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def deal_batch(self, count_per_player: int, players: List[str] = None) -> Dict[str, List[Card]]:
        """Deals count_per_player cards to each player in order."""
        if players is None:
            players = ["P1", "P2", "P3"]
        batch: Dict[str, List[Card]] = {p: [] for p in players}
        for _ in range(count_per_player):
            for p in players:
                if self.cards:
                    batch[p].append(self.cards.pop(0))
        return batch
