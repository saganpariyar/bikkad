from typing import Tuple, Dict, Optional


def get_team_for_player(player_id: str) -> str:
    """P1 and P3 are Team A; P2 and P4 are Team B."""
    return 'Team A' if player_id in ('P1', 'P3') else 'Team B'


def get_partner(player_id: str) -> str:
    partners = {'P1': 'P3', 'P3': 'P1', 'P2': 'P4', 'P4': 'P2'}
    return partners[player_id]


def get_next_opponent(player_id: str) -> str:
    """Clockwise rotation to opponent: P1 -> P2 -> P3 -> P4 -> P1."""
    next_map = {'P1': 'P2', 'P2': 'P3', 'P3': 'P4', 'P4': 'P1'}
    return next_map[player_id]


class LadderScoreManager:
    def __init__(self, initial_dealer: str = 'P1', initial_score: int = 0):
        self.dealer_id: str = initial_dealer
        self.dealer_score: int = initial_score

    @property
    def dealer_team(self) -> str:
        return get_team_for_player(self.dealer_id)

    @property
    def lead_team(self) -> str:
        return 'Team B' if self.dealer_team == 'Team A' else 'Team A'

    def calculate_round_result(
        self,
        mode: str,
        tricks_won: Dict[str, int],
        declarer_id: Optional[str] = None
    ) -> Tuple[int, int, str]:
        """
        Calculates score delta, new dealer score, and detailed log description.
        Returns: (delta: int, new_score: int, note: str)
        """
        dealer_team = self.dealer_team
        lead_team = self.lead_team
        dealer_tricks = tricks_won.get(dealer_team, 0)
        lead_tricks = tricks_won.get(lead_team, 0)

        delta = 0
        note = ""

        if mode == "Regular":
            if lead_tricks >= 9:
                delta = +9
                note = f"{lead_team} won {lead_tricks} tricks (Lead Target >= 9 Met). Dealer {self.dealer_id} burden +9."
            elif dealer_tricks >= 5:
                delta = -18
                note = f"{dealer_team} won {dealer_tricks} tricks (Dealer Target >= 5 Met). Dealer {self.dealer_id} burden -18."
            else:
                # Fallback edge case (e.g. 7-6 split where neither met threshold - shouldn't happen with 13 tricks)
                if lead_tricks > dealer_tricks:
                    delta = +9
                    note = f"{lead_team} won {lead_tricks} tricks. Dealer burden +9."
                else:
                    delta = -18
                    note = f"{dealer_team} won {dealer_tricks} tricks. Dealer burden -18."

        elif mode in ("Tera", "Double Tera"):
            decl_team = get_team_for_player(declarer_id) if declarer_id else lead_team
            opp_team = 'Team B' if decl_team == 'Team A' else 'Team A'
            is_decl_dealer_team = (decl_team == dealer_team)

            decl_tricks = tricks_won.get(decl_team, 0)
            opp_tricks = tricks_won.get(opp_team, 0)
            # In Tera / Double Tera, declarer must take all tricks.
            # If opponents took 0 tricks and declarer collected tricks, or if decl_tricks >= 13, declarer succeeded.
            success = (opp_tricks == 0 and decl_tricks > 0) or (decl_tricks >= 13)

            if mode == "Tera":
                if success:
                    # Win: 13 pts swing in declarer favor
                    delta = -13 if is_decl_dealer_team else +13
                    note = f"Tera SUCCESS! {decl_team} won all 13 tricks."
                else:
                    # Fail: 26 pts penalty awarded to opponents
                    delta = +26 if is_decl_dealer_team else -26
                    note = f"Tera FAILED! Opponents took tricks. 26 pts penalty."

            elif mode == "Double Tera":
                if success:
                    # Win: 26 pts swing in declarer favor
                    delta = -26 if is_decl_dealer_team else +26
                    note = f"Double Tera SUCCESS! {declarer_id} solo won all 13 tricks."
                else:
                    # Fail: 52 pts penalty awarded to opponents (instant bust!)
                    delta = +52 if is_decl_dealer_team else -52
                    note = f"Double Tera FAILED! 52 pts penalty awarded to opponents (Instant Bust)."

        raw_new_score = self.dealer_score + delta
        return delta, raw_new_score, note

    def process_rotation(self, raw_new_score: int) -> Tuple[str, int, str]:
        """
        Applies dealer rotation rules:
        - raw_new_score <= 0 -> FREE! Pass to Opponent at 9 points.
        - raw_new_score >= 52 -> BUST! Pass to Partner at remainder (raw_new_score - 52).
        - 0 < raw_new_score < 52 -> Dealer retains deal at raw_new_score.
        Returns: (next_dealer_id: str, starting_score: int, status_str: str)
        """
        old_dealer = self.dealer_id

        if raw_new_score < 0:
            next_dealer = get_next_opponent(old_dealer)
            # Tug-of-War ladder: crossing below 0 transfers the overshoot debt to the next dealer
            transfer_burden = abs(raw_new_score)

            if transfer_burden >= 52:
                cap_partner = get_partner(next_dealer)
                starting_score = transfer_burden - 52
                status = f"{old_dealer} is FREE! {next_dealer} receives {transfer_burden} penalty (Instant Coat >= 52), passing to PARTNER {cap_partner} at {starting_score} points."
                next_dealer = cap_partner
            else:
                starting_score = transfer_burden
                status = f"{old_dealer} is FREE (Debt Cleared). Deal passes to OPPONENT {next_dealer} at {starting_score} points."
        elif raw_new_score >= 52:
            next_dealer = get_partner(old_dealer)
            starting_score = raw_new_score - 52
            status = f"CAP OUT! {old_dealer} BUSTS (Score {raw_new_score} >= 52). Deal passes to PARTNER {next_dealer} at {starting_score} points."
        elif raw_new_score == 0:
            next_dealer = old_dealer
            starting_score = 0
            status = f"{old_dealer} reached 0 points and continues as Dealer at 0 points."
        else:
            next_dealer = old_dealer
            starting_score = raw_new_score
            status = f"{old_dealer} remains Dealer at {starting_score} points."

        self.dealer_id = next_dealer
        self.dealer_score = starting_score
        return next_dealer, starting_score, status
