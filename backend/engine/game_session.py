import random
from typing import List, Dict, Optional, Tuple, Any
from backend.engine.card import Card, Suit, Rank, Deck
from backend.engine.trick_evaluator import get_legal_cards, can_open_trump, evaluate_trick
from backend.engine.pot_manager import PotManager
from backend.engine.ladder_score import LadderScoreManager, get_partner, get_next_opponent, get_team_for_player
from backend.engine.game_logger import GameLogger


PLAYER_SEATS = ['P1', 'P2', 'P3', 'P4']

INDIAN_NAMES_POOL = [
    "Bhimaram", "Jitu", "Dinesh", "Geeta", "Suraj", "Kantilal",
    "Prakash", "S Kumar", "Sangeeta", "Anita", "Mangilal", "Lumbaram",
    "Chogaram", "Sukhi", "Naresh", "Ganaram", "Sagan"
]


def generate_indian_player_names(p1_name: str = "Sagan") -> Dict[str, str]:
    clean_p1 = (p1_name or "").lower().replace("g.", "").replace("bot", "").strip()
    pool = [n for n in INDIAN_NAMES_POOL if clean_p1 not in n.lower() and n.lower() not in clean_p1]
    if len(pool) < 3:
        pool = list(INDIAN_NAMES_POOL)
    chosen = random.sample(pool, 3)
    return {
        'P1': f"{p1_name} (South - Team A)",
        'P2': f"G. {chosen[0]} (West - Team B)",
        'P3': f"G. {chosen[1]} (North - Team A)",
        'P4': f"G. {chosen[2]} (East - Team B)"
    }


class GameSession:
    def __init__(self, initial_dealer: str = 'P1', initial_score: int = 0):
        self.ladder_manager = LadderScoreManager(initial_dealer, initial_score)
        self.current_dealer_id = initial_dealer
        self.current_dealer_score = initial_score
        self.pot_manager = PotManager()
        
        self.player_teams = {
            'P1': 'Team A',
            'P3': 'Team A',
            'P2': 'Team B',
            'P4': 'Team B'
        }
        
        self.player_types = {
            'P1': 'human',
            'P2': 'ai',
            'P3': 'ai',
            'P4': 'ai'
        }
        
        self.player_names = generate_indian_player_names("Sagan")
        self.game_name: str = "game1"
        self.game_id: str = "game1"
        self.logger = GameLogger()
        self.logger.start_game(self.game_name, self.player_names, self.player_teams, self.player_types)
        
        self.round_number = 0
        self.game_history = []
        self.current_round_logs = []
        
        # Bidding & Deal Stage State
        self.deal_stage: str = "READY"  # "SELECT_TRUMP", "READY"
        self.bidding_phase: bool = False
        self.declarations: Dict[str, str] = {p: "Regular" for p in PLAYER_SEATS}
        
        self.mode = "Regular"  # Regular, Tera, Double Tera
        self.declarer_id: Optional[str] = None
        self.hands: Dict[str, List[Card]] = {p: [] for p in PLAYER_SEATS}
        self.phase1_deals: Dict[str, List[Card]] = {}
        self.phase2_deals: Dict[str, List[Card]] = {}
        self.phase3_deals: Dict[str, List[Card]] = {}
        self.remaining_deals: Dict[str, List[Card]] = {}
        
        self.hidden_trump_card: Optional[Card] = None
        self.hidden_trump_setter: Optional[str] = None
        self.trump_suit: Optional[Suit] = None
        self.trump_revealed: bool = False
        self.trump_opener_id: Optional[str] = None
        self.must_play_trump_player: Optional[str] = None
        self.trump_demanded_by: Optional[str] = None
        self.trump_selection_pending_from: Optional[str] = None
        
        self.current_trick: List[Tuple[str, Card]] = []
        self.last_completed_trick: Optional[List[Tuple[str, Card]]] = None
        self.last_trick_winner: Optional[str] = None
        self.last_trick_winning_card: Optional[str] = None
        self.led_suit: Optional[Suit] = None
        self.current_turn_player: str = ""
        self.trick_number: int = 1
        self.round_complete: bool = False
        self.eldest_hand: str = ""
        self.active_players: List[str] = list(PLAYER_SEATS)
        self.announcement: Optional[dict] = None

    def restart_current_deal(self, seed: Optional[int] = None) -> dict:
        """Restarts the current deal from scratch with the same dealer and ladder score."""
        if self.round_number > 0:
            self.round_number -= 1
        return self.start_new_round(mode="Regular", seed=seed)

    def start_new_round(
        self,
        mode: str = "Regular",
        declarer_id: Optional[str] = None,
        runtime_trump: Optional[Suit] = None,
        seed: Optional[int] = None
    ) -> dict:
        """
        Initializes 3-stage deal (5 cards -> select trump -> 5 cards -> 3 cards).
        """
        self.round_number += 1
        self.mode = mode
        self.declarer_id = declarer_id
        if self.mode == "Double Tera" and self.declarer_id:
            partner = get_partner(self.declarer_id)
            self.active_players = [p for p in PLAYER_SEATS if p != partner]
        else:
            self.active_players = list(PLAYER_SEATS)
        self.round_complete = False
        self.bidding_phase = False
        self.declarations = {p: "Regular" for p in PLAYER_SEATS}
        self.announcement = None
        self.trick_number = 1
        self.current_trick = []
        self.last_completed_trick = None
        self.last_trick_winner = None
        self.last_trick_winning_card = None
        self.trump_revealed = False
        self.trump_opener_id = None
        self.must_play_trump_player = None
        self.trump_demanded_by = None
        self.trump_selection_pending_from = None
        self.hidden_trump_card = None
        self.hidden_trump_setter = None
        self.trump_suit = None
        self.led_suit = None
        self.current_round_logs = []
        self.pot_manager.reset()

        dealer = self.ladder_manager.dealer_id
        self.current_dealer_id = dealer
        self.current_dealer_score = self.ladder_manager.dealer_score
        self.eldest_hand = get_next_opponent(dealer)  # Player left of dealer

        # Shuffle and Deal Batches
        deck = Deck(seed=seed)
        deck.shuffle()

        # Batch 1: 5 cards each
        p1_5, p2_5, p3_5, p4_5 = deck.deal_batch1()
        # Batch 2: 5 cards each
        b2_1, b2_2, b2_3, b2_4 = deck.deal_batch2()
        # Batch 3: 3 cards each
        b3_1, b3_2, b3_3, b3_4 = deck.deal_batch3()

        self.phase1_deals = {'P1': p1_5, 'P2': p2_5, 'P3': p3_5, 'P4': p4_5}
        self.phase2_deals = {'P1': b2_1, 'P2': b2_2, 'P3': b2_3, 'P4': b2_4}
        self.phase3_deals = {'P1': b3_1, 'P2': b3_2, 'P3': b3_3, 'P4': b3_4}
        self.remaining_deals = {
            'P1': b2_1 + b3_1,
            'P2': b2_2 + b3_2,
            'P3': b2_3 + b3_3,
            'P4': b2_4 + b3_4
        }

        # Check if Eldest Hand is Human (P1) and in Regular Mode
        if self.player_types.get(self.eldest_hand) == 'human' and self.mode == "Regular":
            self.deal_stage = "SELECT_TRUMP"
            self.hands = {p: list(self.phase1_deals[p]) for p in PLAYER_SEATS}
            self.current_turn_player = self.eldest_hand
            log_msg = f"Deal {self.round_number} Started. Dealer: {self.player_names[dealer]}. {self.player_names[self.eldest_hand]} got initial 5 cards to select Hidden Trump."
            self.current_round_logs.append(log_msg)
        else:
            # AI Eldest Hand or Special Mode
            self._finalize_deal_stage(None)

        self.logger.start_deal(
            deal_number=self.round_number,
            dealer_id=dealer,
            dealer_score=self.ladder_manager.dealer_score,
            dealer_team=self.ladder_manager.dealer_team,
            lead_team=self.ladder_manager.lead_team,
            eldest_hand=self.eldest_hand,
            hands=self.hands,
            phase1_deals=self.phase1_deals,
            phase2_deals=self.phase2_deals,
            phase3_deals=self.phase3_deals
        )

        return self.get_state()

    def select_hidden_trump(self, card_code: str) -> dict:
        """
        Called when Eldest Hand selects 1 card from their 5 initial cards as Hidden Trump.
        """
        if self.deal_stage != "SELECT_TRUMP":
            raise ValueError("Not in trump selection stage.")

        eldest_5 = self.phase1_deals[self.eldest_hand]
        selected_card = None
        for c in eldest_5:
            if c.code == card_code:
                selected_card = c
                break

        if not selected_card:
            raise ValueError(f"Card {card_code} not in {self.eldest_hand}'s initial 5 cards.")

        self.logger.log_hidden_trump_set(self.eldest_hand, selected_card.code)
        self._finalize_deal_stage(selected_card)
        return self.get_state()

    def _finalize_deal_stage(self, selected_trump_card: Optional[Card]):
        """Completes 5->5->3 dealing and places hidden trump."""
        eldest_5 = self.phase1_deals[self.eldest_hand]
        
        if not selected_trump_card and self.mode == "Regular":
            selected_trump_card = self.auto_select_hidden_trump(self.eldest_hand, eldest_5)

        if self.mode == "Regular":
            self.hidden_trump_card = selected_trump_card
            self.hidden_trump_setter = self.eldest_hand
            self.trump_suit = selected_trump_card.suit
            self.trump_revealed = False
            self.trump_opener_id = None

        # Assemble active hands:
        # Other players receive all 13 cards (5 + 5 + 3)
        # Trump setter holds 12 cards in hand because the hidden trump card is placed under the saucer (Bandh Hukum)
        self.hands = {}
        for p in PLAYER_SEATS:
            all_cards = list(self.phase1_deals[p]) + list(self.remaining_deals[p])
            if self.mode == "Regular" and p == self.hidden_trump_setter and self.hidden_trump_card:
                for idx, c in enumerate(all_cards):
                    if c.code == self.hidden_trump_card.code:
                        all_cards.pop(idx)
                        break
            self.hands[p] = sorted(all_cards, key=lambda c: (c.suit.value, -c.rank.value))

        self.deal_stage = "READY"
        self.current_turn_player = self.eldest_hand
        
        log_msg = f"Cards dealt (5 -> 5 -> 3 = 13 cards total). Leader: {self.player_names[self.eldest_hand]}."
        if self.hidden_trump_card:
            log_msg += " Hidden Trump set."
        self.current_round_logs.append(log_msg)

    def declare_contract(self, player_id: str, contract: str) -> dict:
        """Sets player's declaration ('Regular', 'Tera', 'Double Tera')."""
        if contract not in ("Regular", "Tera", "Double Tera"):
            raise ValueError(f"Invalid contract selection: {contract}")
        self.declarations[player_id] = contract
        self.current_round_logs.append(f"{self.player_names[player_id]} declared contract: {contract}")
        return self.get_state()

    def resolve_bidding(self) -> dict:
        """
        Resolves bidding phase declarations:
        1. Higher contract level wins (Double Tera > Tera > Regular).
        2. Tie-breaker: Team holding/setting hidden trump has higher priority!
        3. Tera / Double Tera: Removes hidden trump card and resets trump_suit until selected at runtime on first void!
        """
        contract_ranks = {"Double Tera": 3, "Tera": 2, "Regular": 1}
        
        highest_rank = 1
        winning_contract = "Regular"
        winning_declarer = None

        trump_team = get_team_for_player(self.hidden_trump_setter) if self.hidden_trump_setter else "Team A"

        for p in PLAYER_SEATS:
            decl = self.declarations.get(p, "Regular")
            rank = contract_ranks[decl]
            
            if rank > highest_rank:
                highest_rank = rank
                winning_contract = decl
                winning_declarer = p
            elif rank == highest_rank and rank > 1:
                p_team = get_team_for_player(p)
                w_team = get_team_for_player(winning_declarer)
                if p_team == trump_team and w_team != trump_team:
                    winning_declarer = p

        self.mode = winning_contract
        self.declarer_id = winning_declarer
        self.bidding_phase = False
        self.logger.log_mode_declaration(self.mode, self.declarer_id, self.declarations)

        if self.mode in ("Tera", "Double Tera") and self.declarer_id:
            # 1. Take back all played cards in trick 1 so every player has their full 13 cards restored
            for p in PLAYER_SEATS:
                full_13 = list(self.phase1_deals[p]) + list(self.remaining_deals[p])
                self.hands[p] = sorted(full_13, key=lambda c: (c.suit.value, -c.rank.value))

            # 2. Reset trick state so Trick 1 restarts fresh
            self.current_trick = []
            self.led_suit = None
            self.trick_number = 1
            self.last_completed_trick = None
            self.last_trick_winner = None
            self.pot_manager.reset()

            # 3. Clear hidden trump (in Tera, trump is chosen runtime on first void)
            self.hidden_trump_card = None
            self.hidden_trump_setter = None
            self.trump_suit = None
            self.trump_revealed = False

            declarer_name = self.player_names.get(self.declarer_id, self.declarer_id)

            if self.mode == "Double Tera":
                partner = get_partner(self.declarer_id)
                partner_name = self.player_names.get(partner, partner)
                self.active_players = [p for p in PLAYER_SEATS if p != partner]
                self.current_round_logs.append(
                    f"📢 CONTRACT FINALIZED: DOUBLE TERA by {declarer_name}! Played cards taken back into hands. Partner {partner_name} sits out."
                )
            else:
                self.active_players = list(PLAYER_SEATS)
                self.current_round_logs.append(
                    f"📢 CONTRACT FINALIZED: TERA by {declarer_name}! Played cards taken back into hands."
                )

            # 4. Declarer leads the first trick!
            self.eldest_hand = self.declarer_id
            self.current_turn_player = self.declarer_id
            self.current_round_logs.append(
                f"{declarer_name} leads the first card for {self.mode}."
            )

            self.announcement = {
                'title': f"{declarer_name} declared {self.mode.upper()}!",
                'sub': f"All played cards returned to hands. {declarer_name} plays first!",
                'declarer_id': self.declarer_id,
                'mode': self.mode
            }
        else:
            self.active_players = list(PLAYER_SEATS)
            self.current_round_logs.append("CONTRACT FINALIZED: REGULAR MODE.")
            self.current_turn_player = self.eldest_hand
            self.announcement = None

        return self.get_state()

    def set_runtime_trump(self, suit_char: str) -> dict:
        """Sets the runtime trump suit declared by Declarer upon first void."""
        suit = Suit(suit_char)
        self.trump_suit = suit
        self.trump_revealed = True
        self.trump_selection_pending_from = None
        opener = self.trump_demanded_by or self.declarer_id
        self.trump_opener_id = opener
        if self.trump_demanded_by:
            self.must_play_trump_player = self.trump_demanded_by
        elif self.declarer_id:
            self.must_play_trump_player = self.declarer_id
        self.current_round_logs.append(
            f"RUN-TIME TRUMP DECLARED by {self.player_names[self.declarer_id]}: {suit.name_str} ({suit.symbol})"
        )
        self.logger.log_trump_revealed(
            opener_id=opener or "",
            trump_card=None,
            trump_suit=suit.value,
            trick_number=self.trick_number
        )
        return self.get_state()

    def demand_runtime_trump(self, player_id: str) -> dict:
        """Player demands runtime trump during Tera / Double Tera when void in led suit."""
        if self.mode not in ("Tera", "Double Tera"):
            raise ValueError("Demand runtime trump is only valid in Tera / Double Tera modes.")
        if self.trump_revealed:
            return self.get_state()
        if player_id != self.current_turn_player:
            raise ValueError(f"Not {self.player_names.get(player_id, player_id)}'s turn.")

        player_hand = self.hands[player_id]
        if self.led_suit and any(c.suit == self.led_suit for c in player_hand):
            raise ValueError(f"Cannot demand trump: player still holds cards of led suit {self.led_suit.name_str}.")

        self.trump_demanded_by = player_id
        self.must_play_trump_player = player_id

        # If declarer is AI, declarer picks trump heuristic immediately
        if self.player_types.get(self.declarer_id) == 'ai':
            from backend.ai.heuristic_fallback import select_runtime_trump_heuristic
            decl_hand = self.hands[self.declarer_id]
            best_suit = select_runtime_trump_heuristic(decl_hand)
            self.set_runtime_trump(best_suit)
            self.trump_opener_id = player_id
            self.must_play_trump_player = player_id
            self.current_round_logs.append(
                f"{self.player_names[player_id]} DEMANDED TRUMP! Declarer {self.player_names[self.declarer_id]} declared: {self.trump_suit.name_str} ({self.trump_suit.symbol})"
            )
        else:
            self.trump_selection_pending_from = self.declarer_id
            self.current_round_logs.append(
                f"{self.player_names[player_id]} DEMANDED TRUMP from Declarer {self.player_names[self.declarer_id]}!"
            )
        return self.get_state()

    def auto_select_hidden_trump(self, player_id: str, phase1_5_cards: List[Card]) -> Card:
        """Heuristic selection for hidden trump from 5 initial cards."""
        suit_counts = {}
        for c in phase1_5_cards:
            suit_counts[c.suit] = suit_counts.get(c.suit, 0) + 1
        sorted_cards = sorted(phase1_5_cards, key=lambda c: (-suit_counts[c.suit], c.rank.value))
        return sorted_cards[0]

    def get_next_player(self, current_p: str) -> str:
        """Returns next active player in clockwise turn order."""
        idx = PLAYER_SEATS.index(current_p)
        for i in range(1, 4):
            nxt = PLAYER_SEATS[(idx + i) % 4]
            if nxt in self.active_players:
                return nxt
        return current_p

    def open_trump(self, player_id: str, force: bool = False) -> bool:
        """Reveals the hidden trump card (Rang Kholna) and returns it to the setter's active hand."""
        if self.trump_revealed:
            return True
        if force or can_open_trump(
            self.hands[player_id],
            self.led_suit,
            self.trump_revealed,
            self.hidden_trump_card,
            self.mode
        ):
            self.trump_revealed = True
            self.trump_opener_id = player_id
            self.must_play_trump_player = player_id

            # Return hidden trump card to the setter's active hand!
            if self.hidden_trump_card and self.hidden_trump_setter:
                setter_hand = self.hands.get(self.hidden_trump_setter, [])
                if not any(c.code == self.hidden_trump_card.code for c in setter_hand):
                    setter_hand.append(self.hidden_trump_card)
                    self.hands[self.hidden_trump_setter] = sorted(
                        setter_hand, key=lambda c: (c.suit.value, -c.rank.value)
                    )

            self.current_round_logs.append(
                f"{self.player_names[player_id]} DEMANDED THE CUT! Hidden Trump revealed: [{self.hidden_trump_card.code}] ({self.trump_suit.name_str})"
            )
            self.logger.log_trump_revealed(
                opener_id=player_id,
                trump_card=self.hidden_trump_card.code if self.hidden_trump_card else None,
                trump_suit=self.trump_suit.value if self.trump_suit else "",
                trick_number=self.trick_number
            )
            return True
        return False

    def play_card(self, player_id: str, card_code: str, demand_cut: bool = False) -> dict:
        """
        Executes a turn play for player_id.
        """
        if self.deal_stage == "SELECT_TRUMP":
            raise ValueError("Must select hidden trump card first.")

        if self.bidding_phase:
            self.resolve_bidding()

        if self.round_complete:
            raise ValueError("Round is already complete.")
        if player_id != self.current_turn_player:
            raise ValueError(f"Not {self.player_names[player_id]}'s turn. Current turn: {self.player_names[self.current_turn_player]}")

        # Safeguard: if trump is still unrevealed on trick 13 or if setter has 0 cards left, reveal trump
        if not self.trump_revealed and self.hidden_trump_card and self.hidden_trump_setter:
            if self.trick_number == 13 or len(self.hands.get(self.hidden_trump_setter, [])) == 0:
                self.open_trump(self.hidden_trump_setter, force=True)

        just_opened_cut = False
        if demand_cut and not self.trump_revealed:
            if self.mode == "Regular":
                just_opened_cut = self.open_trump(player_id)
            elif self.mode in ("Tera", "Double Tera"):
                self.demand_runtime_trump(player_id)
                just_opened_cut = self.trump_revealed

        player_hand = self.hands[player_id]
        target_card = None
        for c in player_hand:
            if c.code == card_code:
                target_card = c
                break

        if not target_card:
            raise ValueError(f"Card {card_code} not in {self.player_names[player_id]}'s hand.")

        legal_cards = get_legal_cards(player_hand, self.led_suit)
        
        # If player demanded/asked for trump on their turn and is void in led suit:
        # They MUST play a trump card if they hold any trump card in hand!
        # If they do not hold any trump card, they can play any legal card.
        has_demanded_trump = (self.must_play_trump_player == player_id or just_opened_cut)
        if has_demanded_trump and self.trump_suit and self.trump_revealed:
            has_led_suit = self.led_suit and any(c.suit == self.led_suit for c in player_hand)
            if not has_led_suit:
                trump_cards_in_hand = [c for c in player_hand if c.suit == self.trump_suit]
                if trump_cards_in_hand and target_card.suit != self.trump_suit:
                    raise ValueError(f"Must play a trump card ({self.trump_suit.name_str}) after asking/opening trump!")

        if target_card not in legal_cards:
            raise ValueError(f"Illegal move: Must follow led suit {self.led_suit.name_str if self.led_suit else ''}.")

        player_hand.remove(target_card)
        self.must_play_trump_player = None
        self.trump_demanded_by = None
        if not self.led_suit:
            self.led_suit = target_card.suit

        self.current_trick.append((player_id, target_card))
        self.current_round_logs.append(f"T{self.trick_number:02d}: {self.player_names[player_id]} plays {target_card.code}")

        cards_required = len(self.active_players)
        if len(self.current_trick) == cards_required:
            self._resolve_trick()
        else:
            self.current_turn_player = self.get_next_player(player_id)

        return self.get_state()

    def _resolve_trick(self):
        """Resolves completed trick, evaluates winner, updates pot accumulator, checks round end."""
        winning_player, winning_card = evaluate_trick(
            self.current_trick,
            self.led_suit,
            self.trump_suit,
            self.trump_revealed
        )

        self.last_completed_trick = list(self.current_trick)
        self.last_trick_winner = winning_player
        self.last_trick_winning_card = winning_card.code

        trick_cards = [c for _, c in self.current_trick]
        collected, team_collected, count, reason = self.pot_manager.add_trick(
            winning_player,
            trick_cards,
            self.trick_number,
            self.player_teams
        )

        winning_team = self.player_teams[winning_player]
        win_msg = f"T{self.trick_number:02d} Winner: {self.player_names[winning_player]} ({winning_team}) with {winning_card.code}."
        if collected:
            win_msg += f" ==> {team_collected} COLLECTED {count} CARDS ({reason.upper()})!"
        self.current_round_logs.append(win_msg)

        self.logger.log_trick(
            trick_number=self.trick_number,
            led_suit=self.led_suit.value if self.led_suit else "",
            trick_cards=self.current_trick,
            winner_player_id=winning_player,
            winning_card=winning_card,
            pot_cards_count=len(self.pot_manager.pot_cards),
            pot_tricks_count=self.pot_manager.pot_tricks_count,
            collected=collected,
            collecting_team=team_collected,
            cards_collected=count,
            collection_reason=reason,
            streak_holder=self.player_names.get(self.pot_manager.last_winner_player_id, self.pot_manager.last_winner_player_id) if self.pot_manager.last_winner_player_id else None,
            streak_count=self.pot_manager.streak_count,
            trump_revealed=self.trump_revealed,
            trump_suit=self.trump_suit.value if self.trump_suit else None
        )

        abort_round = False
        if self.mode in ("Tera", "Double Tera") and self.declarer_id:
            decl_team = get_team_for_player(self.declarer_id)
            # In Bikkad, an in-between hand win does not win a trick; cards remain in the pot.
            # Tera fails ONLY when opponents actually collect tricks (2 consecutive wins or 13th sweep).
            if collected and team_collected != decl_team:
                abort_round = True
                msg = f"{self.mode.upper()} FAILED! Opponents ({team_collected}) collected {count} cards at Trick {self.trick_number:02d}."
                self.current_round_logs.append(msg)
        elif self.mode == "Regular":
            dealer_team = get_team_for_player(self.current_dealer_id)
            lead_team = 'Team B' if dealer_team == 'Team A' else 'Team A'
            dealer_tricks = self.pot_manager.team_tricks_won.get(dealer_team, 0)
            lead_tricks = self.pot_manager.team_tricks_won.get(lead_team, 0)

            if dealer_tricks >= 5:
                abort_round = True
                swept = self.pot_manager.sweep_remaining_pot(dealer_team)
                msg = f"EARLY WIN: Dealer {dealer_team} clinched deal with {dealer_tricks} tricks at Trick {self.trick_number:02d} (Target >= 5 Met)!"
                if swept > 0:
                    msg += f" {dealer_team} sweeps remaining {swept} pot cards!"
                self.current_round_logs.append(msg)
            elif lead_tricks >= 9:
                abort_round = True
                swept = self.pot_manager.sweep_remaining_pot(lead_team)
                msg = f"EARLY WIN: Lead {lead_team} clinched deal with {lead_tricks} tricks at Trick {self.trick_number:02d} (Target >= 9 Met)!"
                if swept > 0:
                    msg += f" {lead_team} sweeps remaining {swept} pot cards!"
                self.current_round_logs.append(msg)

        if self.trick_number == 13 or abort_round:
            self._end_round()
        else:
            self.trick_number += 1
            self.current_trick = []
            self.led_suit = None
            self.current_turn_player = winning_player

    def _end_round(self):
        """Finalizes round, calculates ladder score, and updates dealer rotation."""
        self.round_complete = True
        # Note: self.active_players is preserved so sitting out partner remains marked as sitting out in deal summary
        delta, raw_new_score, score_note = self.ladder_manager.calculate_round_result(
            self.mode,
            self.pot_manager.team_tricks_won,
            self.declarer_id
        )

        next_dealer, starting_score, rotation_status = self.ladder_manager.process_rotation(raw_new_score)

        round_summary = {
            'round_number': self.round_number,
            'mode': self.mode,
            'dealer': self.current_dealer_id,
            'dealer_score': self.current_dealer_score,
            'tricks_won': dict(self.pot_manager.team_tricks_won),
            'cards_collected': dict(self.pot_manager.team_cards_collected),
            'delta': delta,
            'new_score': raw_new_score,
            'next_dealer': next_dealer,
            'next_starting_score': starting_score,
            'note': score_note,
            'rotation_status': rotation_status
        }
        self.game_history.append(round_summary)
        self.current_round_logs.append(f"ROUND END: {score_note} | {rotation_status}")
        self.logger.end_deal(
            tricks_won=self.pot_manager.team_tricks_won,
            cards_collected=self.pot_manager.team_cards_collected,
            delta=delta,
            raw_new_score=raw_new_score,
            next_dealer=next_dealer,
            next_starting_score=starting_score,
            score_note=score_note,
            rotation_status=rotation_status
        )

    def get_state(self) -> dict:
        """Returns snapshot of current state for Web UI / API."""
        dealer_for_state = self.current_dealer_id if self.round_complete else self.ladder_manager.dealer_id
        score_for_state = self.current_dealer_score if self.round_complete else self.ladder_manager.dealer_score
        dealer_team = get_team_for_player(dealer_for_state)
        lead_team = 'Team B' if dealer_team == 'Team A' else 'Team A'

        return {
            'round_number': self.round_number,
            'deal_stage': self.deal_stage,
            'bidding_phase': self.bidding_phase,
            'declarations': self.declarations,
            'mode': self.mode,
            'declarer_id': self.declarer_id,
            'dealer_id': dealer_for_state,
            'dealer_score': score_for_state,
            'dealer_team': dealer_team,
            'lead_team': lead_team,
            'next_dealer': self.ladder_manager.dealer_id,
            'next_dealer_score': self.ladder_manager.dealer_score,
            'eldest_hand': self.eldest_hand,
            'current_turn_player': self.current_turn_player,
            'trick_number': self.trick_number,
            'led_suit': self.led_suit.value if self.led_suit else None,
            'trump_suit': self.trump_suit.value if self.trump_suit else None,
            'trump_revealed': self.trump_revealed,
            'trump_opener_id': self.trump_opener_id,
            'trump_opener_name': self.player_names.get(self.trump_opener_id, self.trump_opener_id) if self.trump_opener_id else None,
            'must_play_trump_player': self.must_play_trump_player,
            'trump_demanded_by': self.trump_demanded_by,
            'trump_selection_pending_from': self.trump_selection_pending_from,
            'hidden_trump_card': self.hidden_trump_card.to_dict() if self.hidden_trump_card else None,
            'hidden_trump_setter': self.hidden_trump_setter,
            'pot_card_count': len(self.pot_manager.pot_cards),
            'pot_trick_count': self.pot_manager.pot_tricks_count,
            'pot_streak_holder': self.player_names.get(self.pot_manager.last_winner_player_id, self.pot_manager.last_winner_player_id) if self.pot_manager.last_winner_player_id else None,
            'pot_streak_count': self.pot_manager.streak_count,
            'team_tricks_won': self.pot_manager.team_tricks_won,
            'team_cards_collected': self.pot_manager.team_cards_collected,
            'active_players': self.active_players,
            'round_complete': self.round_complete,
            'current_trick': [{'player_id': p, 'card': c.to_dict()} for p, c in self.current_trick],
            'last_completed_trick': [{'player_id': p, 'card': c.to_dict()} for p, c in (self.last_completed_trick or [])],
            'last_trick_winner': self.last_trick_winner,
            'last_trick_winning_card': self.last_trick_winning_card,
            'hands': {p: [c.to_dict() for c in hand] for p, hand in self.hands.items()},
            'phase1_deals': {p: [c.to_dict() for c in hand] for p, hand in self.phase1_deals.items()},
            'phase2_deals': {p: [c.to_dict() for c in hand] for p, hand in self.phase2_deals.items()},
            'phase3_deals': {p: [c.to_dict() for c in hand] for p, hand in self.phase3_deals.items()},
            'player_types': self.player_types,
            'player_names': self.player_names,
            'logs': self.current_round_logs,
            'announcement': self.announcement,
            'game_name': self.game_name,
            'game_id': self.game_id
        }
