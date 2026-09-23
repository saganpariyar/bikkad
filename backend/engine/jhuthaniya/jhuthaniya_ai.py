"""
Jhuthaniya AI — Bot heuristics for Bluff/Cheat card game.
Covers: card selection for play, challenge decision making.
"""
import random
from typing import List, Dict, Optional, Tuple


# Rank order for sorting (2=2 ... A=14)
RANK_ORDER = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
RANK_VALUE = {r: i for i, r in enumerate(RANK_ORDER)}


def rank_value(code: str) -> int:
    """Returns numeric value of a card's rank from its code like '10H', 'KS'."""
    if len(code) < 2:
        return 0
    # code format: rank + suit (e.g. '10H', 'KS', '2C')
    rank_str = code[:-1]  # everything except last char (suit)
    return RANK_VALUE.get(rank_str, 0)


def bot_select_cards_to_play(
    hand: List[str],
    claimed_rank: str,
    count: int,
    center_pot_size: int
) -> Tuple[List[str], bool]:
    """
    Bot selects which cards to play and whether to bluff.

    Strategy:
    - If bot has enough cards of claimed_rank: play them truthfully.
    - If partially: play what it has + bluff the rest with lowest cards.
    - If none: play `count` lowest-value cards as a bluff.

    Returns:
        (list of card codes to play, is_bluffing: bool)
    """
    matching = [c for c in hand if c[:-1] == claimed_rank]

    if len(matching) >= count:
        # Full truth: play first `count` matching cards
        return matching[:count], False

    bluff_candidates = [c for c in hand if c[:-1] != claimed_rank]
    bluff_candidates.sort(key=lambda c: rank_value(c))  # lowest first

    if len(matching) > 0 and len(bluff_candidates) >= (count - len(matching)):
        # Partial truth + partial bluff
        needed_bluff = count - len(matching)
        cards = matching + bluff_candidates[:needed_bluff]
        return cards, True

    # Full bluff: no matching cards — play lowest N cards
    all_sorted = sorted(hand, key=lambda c: rank_value(c))
    play_cards = all_sorted[:count]
    return play_cards, True


def bot_choose_claim_rank(hand: List[str], required_rank: Optional[str] = None) -> Tuple[str, int]:
    """
    Bot decides what rank to claim and how many cards to claim.

    Strategy (Option A):
    - If required_rank is provided: must claim required_rank.
      Uses matching cards count or bluffs 1-2 cards.
    - If required_rank is None (leading player):
      Prefers to claim ranks it actually holds (truth play).
      Claims 1–3 cards based on count.

    Returns:
        (claimed_rank: str, count: int)
    """
    if required_rank:
        matching = [c for c in hand if c[:-1] == required_rank]
        if matching:
            claim_count = min(len(matching), random.randint(1, 3))
        else:
            # Bluff: play 1 or 2 cards
            claim_count = min(len(hand), random.choice([1, 2]))
        return required_rank, max(1, claim_count)

    rank_counts: Dict[str, List[str]] = {}
    for card in hand:
        r = card[:-1]
        rank_counts.setdefault(r, []).append(card)

    # Ranks bot actually holds (sorted by count desc, then rank value desc)
    held_ranks = sorted(rank_counts.keys(), key=lambda r: (len(rank_counts[r]), RANK_VALUE.get(r, 0)), reverse=True)

    if held_ranks:
        best_rank = held_ranks[0]
        count_available = len(rank_counts[best_rank])
        # Claim 1-3 based on what we hold
        claim_count = min(count_available, random.randint(1, 3))
        return best_rank, max(1, claim_count)

    # Fallback: claim a random rank with 1 card
    ranks = list(RANK_ORDER)
    return random.choice(ranks), 1


def bot_should_challenge(
    my_hand: List[str],
    claimed_rank: str,
    claimed_count: int,
    cards_in_pot: int,
    claimant_hand_size: int,
    players_remaining: int
) -> bool:
    """
    Bot decides whether to challenge the current claim.

    Heuristics:
    1. Impossibility check: If bot holds X of rank R and opponent claims Y, X+Y > 4 → always challenge.
    2. Pot risk: Large pot = challenge only if very confident.
    3. Endgame suspicion: If opponent may be playing their last cards, increase challenge rate.
    4. Small pot: Challenge more aggressively.

    Returns:
        True = challenge ("JHUTH!"), False = pass
    """
    # Count how many of claimed_rank bot holds
    my_count = sum(1 for c in my_hand if c[:-1] == claimed_rank)
    total_claimed = my_count + claimed_count

    # 1. Impossibility: total exceeds 4 in a standard deck
    if total_claimed > 4:
        return True

    # 2. Endgame suspicion: high challenge rate if opponent is nearly out
    endgame_bonus = 0.0
    if claimant_hand_size <= claimed_count + 1:
        # Opponent is playing their last cards!
        endgame_bonus = 0.50

    # 3. Base challenge probability using card-counting probability
    # Probability opponent is bluffing = (4 - my_count - actual_they_could_have) / plausibility
    # Simple heuristic: if I see many of this rank, it's more likely a bluff
    plausibility = max(0.0, (4 - my_count) / 4.0)  # 0.0 if I have all 4, 1.0 if I have none

    # Scale by claimed count vs plausibility
    if claimed_count > (4 - my_count):
        challenge_prob = 0.95
    else:
        # Base suspicion from claimed count relative to what's possible
        base = claimed_count / max(1, (4 - my_count))
        challenge_prob = min(0.85, base * 0.6) + endgame_bonus

    # 4. Pot size modifier
    if cards_in_pot > 10:
        # Big pot: reduce challenge aggression (risky to pick up if wrong)
        challenge_prob *= 0.6
    elif cards_in_pot < 3:
        # Small pot: more aggressive
        challenge_prob = min(0.9, challenge_prob * 1.3)

    return random.random() < challenge_prob


def bot_choose_inspect_index(claimed_count: int) -> int:
    """
    When challenging, bot decides which card position (0-indexed) to inspect.
    e.g. For 3 cards, chooses 0, 1, or 2.
    """
    if claimed_count <= 1:
        return 0
    return random.randint(0, claimed_count - 1)

