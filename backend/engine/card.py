import random
from enum import Enum
from typing import List, Tuple, Optional


class Suit(str, Enum):
    SPADES = 'S'
    HEARTS = 'H'
    DIAMONDS = 'D'
    CLUBS = 'C'

    @property
    def symbol(self) -> str:
        symbols = {'S': '♠', 'H': '♥', 'D': '♦', 'C': '♣'}
        return symbols[self.value]

    @property
    def color(self) -> str:
        return 'red' if self.value in ('H', 'D') else 'black'

    @property
    def name_str(self) -> str:
        names = {'S': 'Spades', 'H': 'Hearts', 'D': 'Diamonds', 'C': 'Clubs'}
        return names[self.value]


class Rank(int, Enum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14

    @property
    def symbol(self) -> str:
        symbols = {
            2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 10: '10',
            11: 'J', 12: 'Q', 13: 'K', 14: 'A'
        }
        return symbols[self.value]


class Card:
    def __init__(self, rank: Rank, suit: Suit):
        self.rank = rank
        self.suit = suit

    @property
    def code(self) -> str:
        return f"{self.rank.symbol}{self.suit.value}"

    @classmethod
    def from_code(cls, code: str) -> 'Card':
        code = code.strip().upper()
        suit_char = code[-1]
        rank_str = code[:-1]
        
        suit = Suit(suit_char)
        
        rank_map = {
            '2': Rank.TWO, '3': Rank.THREE, '4': Rank.FOUR, '5': Rank.FIVE,
            '6': Rank.SIX, '7': Rank.SEVEN, '8': Rank.EIGHT, '9': Rank.NINE,
            '10': Rank.TEN, 'J': Rank.JACK, 'Q': Rank.QUEEN, 'K': Rank.KING, 'A': Rank.ACE
        }
        rank = rank_map[rank_str]
        return cls(rank, suit)

    def to_dict(self) -> dict:
        return {
            'code': self.code,
            'suit': self.suit.value,
            'rank': self.rank.value,
            'symbol': self.rank.symbol,
            'suit_symbol': self.suit.symbol,
            'color': self.suit.color
        }

    def __repr__(self) -> str:
        return self.code

    def __eq__(self, other) -> bool:
        if not isinstance(other, Card):
            return False
        return self.rank == other.rank and self.suit == other.suit

    def __hash__(self) -> int:
        return hash((self.rank, self.suit))


class Deck:
    def __init__(self, seed: Optional[int] = None):
        self.seed = seed
        self.rng = random.Random(seed)
        self.cards: List[Card] = [Card(r, s) for s in Suit for r in Rank]

    def shuffle(self):
        self.rng.shuffle(self.cards)

    def deal_batch1(self) -> Tuple[List[Card], List[Card], List[Card], List[Card]]:
        """Deals first 5 cards to each player."""
        p1 = [self.cards.pop() for _ in range(5)]
        p2 = [self.cards.pop() for _ in range(5)]
        p3 = [self.cards.pop() for _ in range(5)]
        p4 = [self.cards.pop() for _ in range(5)]
        return p1, p2, p3, p4

    def deal_batch2(self) -> Tuple[List[Card], List[Card], List[Card], List[Card]]:
        """Deals next 5 cards to each player (10 cards total)."""
        p1 = [self.cards.pop() for _ in range(5)]
        p2 = [self.cards.pop() for _ in range(5)]
        p3 = [self.cards.pop() for _ in range(5)]
        p4 = [self.cards.pop() for _ in range(5)]
        return p1, p2, p3, p4

    def deal_batch3(self) -> Tuple[List[Card], List[Card], List[Card], List[Card]]:
        """Deals final 3 cards to each player (13 cards total)."""
        p1 = [self.cards.pop() for _ in range(3)]
        p2 = [self.cards.pop() for _ in range(3)]
        p3 = [self.cards.pop() for _ in range(3)]
        p4 = [self.cards.pop() for _ in range(3)]
        return p1, p2, p3, p4

    def deal_phase1(self) -> Tuple[List[Card], List[Card], List[Card], List[Card]]:
        return self.deal_batch1()

    def deal_phase2(self) -> Tuple[List[Card], List[Card], List[Card], List[Card]]:
        b2 = self.deal_batch2()
        b3 = self.deal_batch3()
        return (
            b2[0] + b3[0],
            b2[1] + b3[1],
            b2[2] + b3[2],
            b2[3] + b3[3]
        )
