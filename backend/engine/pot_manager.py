from typing import List, Dict, Optional, Tuple
from backend.engine.card import Card


class PotManager:
    def __init__(self):
        self.reset()

    def reset(self):
        self.pot_cards: List[Card] = []
        self.pot_tricks_count: int = 0
        self.last_winner_player_id: Optional[str] = None
        self.last_winner_team: Optional[str] = None
        self.streak_count: int = 0
        self.team_tricks_won: Dict[str, int] = {'Team A': 0, 'Team B': 0}
        self.team_cards_collected: Dict[str, int] = {'Team A': 0, 'Team B': 0}

    def add_trick(
        self,
        winning_player_id: str,
        trick_cards: List[Card],
        trick_number: int,
        player_team_map: Dict[str, str]
    ) -> Tuple[bool, Optional[str], int, str]:
        """
        Adds a completed trick's cards to the center pot and updates streak / collection state.
        RULE: Two consecutive wins must be achieved by the SAME INDIVIDUAL PLAYER to collect the pot.
        Returns: (collected: bool, collecting_team: Optional[str], card_count: int, reason: str)
        """
        winning_team = player_team_map[winning_player_id]
        # Cards accumulate in center pot; tricks are only won upon collection!
        self.pot_cards.extend(trick_cards)
        self.pot_tricks_count += 1

        if winning_player_id == self.last_winner_player_id:
            self.streak_count += 1
        else:
            self.last_winner_player_id = winning_player_id
            self.last_winner_team = winning_team
            self.streak_count = 1

        # Check 2-consecutive wins by the same individual player
        cards_per_trick = len(trick_cards) if (trick_cards and len(trick_cards) > 0) else 4
        if self.streak_count >= 2:
            collected_count = len(self.pot_cards)
            self.team_cards_collected[winning_team] += collected_count
            self.team_tricks_won[winning_team] = self.team_cards_collected[winning_team] // cards_per_trick
            self.pot_cards = []
            self.pot_tricks_count = 0
            self.streak_count = 0
            self.last_winner_player_id = None
            self.last_winner_team = None
            return True, winning_team, collected_count, "consecutive_streak"

        # Check 13th trick sweep
        if trick_number == 13:
            collected_count = len(self.pot_cards)
            self.team_cards_collected[winning_team] += collected_count
            self.team_tricks_won[winning_team] = self.team_cards_collected[winning_team] // cards_per_trick
            self.pot_cards = []
            self.pot_tricks_count = 0
            self.streak_count = 0
            self.last_winner_player_id = None
            self.last_winner_team = None
            return True, winning_team, collected_count, "13th_sweep"

        return False, None, 0, "accumulating"

    def sweep_remaining_pot(self, winning_team: str, cards_per_trick: int = 4) -> int:
        """Sweeps any remaining cards in center pot to the winning team upon early win."""
        collected_count = len(self.pot_cards)
        if collected_count > 0:
            self.team_cards_collected[winning_team] += collected_count
            self.team_tricks_won[winning_team] = self.team_cards_collected[winning_team] // cards_per_trick
            self.pot_cards = []
            self.pot_tricks_count = 0
            self.streak_count = 0
            self.last_winner_player_id = None
            self.last_winner_team = None
        return collected_count
