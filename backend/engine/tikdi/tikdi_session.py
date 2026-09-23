import random
from typing import List, Dict, Optional, Any, Tuple
from backend.engine.card import Card, Suit, Rank
from backend.engine.tikdi.tikdi_deck import TikdiDeck, create_tikdi_deck
from backend.engine.tikdi.tikdi_ai import (
    select_tikdi_trump,
    select_penalty_return_card,
    select_tikdi_bot_play,
    evaluate_trick_winner
)


class TikdiSession:
    """
    Complete game session controller for Tikdi (3-Player / Teen Do Paanch / 3-2-5 / 5-3-2).
    """
    def __init__(self, game_id: str = "tikdi1", host_name: str = "Sagan", trump_chooser: Optional[str] = None, penalty_mode: str = "card_swap"):
        self.game_id = game_id
        self.host_name = host_name
        self.penalty_mode = penalty_mode or "card_swap"

        self.players = ["P1", "P2", "P3"]
        self.player_names = {
            "P1": host_name,
            "P2": "G. Dinesh",
            "P3": "G. Bhimaram"
        }
        self.player_types = {
            "P1": "human",
            "P2": "ai",
            "P3": "ai"
        }

        # Match Progress
        self.round_number = 1

        # Dealer determination from initial trump chooser in clockwise play (P1 -> P2 -> P3 -> P1)
        # Dealer is the player immediately preceding the trump chooser clockwise.
        order = ["P1", "P2", "P3"]
        if trump_chooser == "random":
            chosen = random.choice(order)
            self.dealer = order[(order.index(chosen) - 1) % 3]
        elif trump_chooser in order:
            self.dealer = order[(order.index(trump_chooser) - 1) % 3]
        else:
            self.dealer = "P1"  # default: P1 deals, so P2 chooses trump and leads Round 1

        # Pending Debts for Next Round: dict of {creditor: {debtor: count}}
        # e.g., {"P2": {"P1": 1}} means P2 pulls 1 card from P1
        self.debts: Dict[str, Dict[str, int]] = {p: {} for p in self.players}

        self.update_roles()

        # Cumulative Match Scores (Net surplus/deficit accumulated over rounds)
        self.cumulative_scores: Dict[str, int] = {p: 0 for p in self.players}

        # Active Round State
        self.deck: Optional[TikdiDeck] = None
        self.hands: Dict[str, List[Card]] = {p: [] for p in self.players}
        self.trump_suit: Optional[str] = None
        self.phase: str = "ROUND_START"  # TRUMP_SELECTION, PENALTY_RESOLUTION, TRICK_PLAYING, ROUND_OVER

        # Penalty Resolution State
        self.penalty_queue: List[Dict[str, Any]] = []
        self.current_penalty: Optional[Dict[str, Any]] = None

        # Trick Playing State
        self.tricks_won: Dict[str, int] = {p: 0 for p in self.players}
        self.current_trick_number: int = 1
        self.current_trick: List[Dict[str, Any]] = []  # list of {"player": str, "card": Card}
        self.current_turn: Optional[str] = None
        self.led_suit: Optional[str] = None
        self.trick_history: List[Dict[str, Any]] = []
        self.last_trick_winner: Optional[str] = None

        # Round Summary
        self.round_summary: Optional[Dict[str, Any]] = None
        self.logs: List[str] = []

        # Debt Settlement Choice State
        self.debt_choice_list: List[Dict[str, Any]] = []  # list of debts awaiting debtor choice
        self.debt_choice_idx: int = 0  # index into debt_choice_list
        self.debt_choices_made: Dict[str, str] = {}  # key "creditor:debtor" -> "card_swap" or "quota_adjustment"

        # Start initial round
        self.start_new_round()

    def update_roles(self):
        """Sets base quotas based on current dealer role in clockwise rotation.
        Quota adjustments from debts are handled separately in the PENALTY_ADJUSTMENT phase."""
        # P1 -> P2 -> P3 -> P1
        order = ["P1", "P2", "P3"]
        dealer_idx = order.index(self.dealer)
        self.trump_chooser = order[(dealer_idx + 1) % 3]
        self.bystander = order[(dealer_idx + 2) % 3]

        self.quotas = {
            self.trump_chooser: 5,
            self.bystander: 3,
            self.dealer: 2
        }
        # Store base quotas for display in adjustment modal
        self.base_quotas = dict(self.quotas)

    def start_new_round(self):
        """Starts a new round: shuffles 30 cards, updates roles, deals Stage 1 (5 cards each)."""
        self.update_roles()
        self.tricks_won = {p: 0 for p in self.players}
        self.current_trick_number = 1
        self.current_trick = []
        self.trick_history = []
        self.led_suit = None
        self.round_summary = None
        self.trump_suit = None

        order = ["P1", "P2", "P3"]
        dealer_idx = order.index(self.dealer)
        # Clockwise dealing starts from the player to dealer's left
        self.deal_order = [
            order[(dealer_idx + 1) % 3],
            order[(dealer_idx + 2) % 3],
            self.dealer
        ]

        self.logs.append(
            f"--- Round {self.round_number} Started --- Dealer: {self.player_names[self.dealer]} ({self.dealer}) [Quota {self.quotas[self.dealer]}]. "
            f"Trump Chooser: {self.player_names[self.trump_chooser]} ({self.trump_chooser}) [Quota {self.quotas[self.trump_chooser]}]. "
            f"Bystander: {self.player_names[self.bystander]} ({self.bystander}) [Quota {self.quotas[self.bystander]}]."
        )

        # Create and shuffle custom 30-card deck
        self.deck = TikdiDeck()
        self.hands = {p: [] for p in self.players}

        # Stage 1: Deal 5 cards to each player clockwise starting from Chooser
        stage_1_batch = self.deck.deal_batch(5, self.deal_order)
        for p in self.players:
            self.hands[p] = stage_1_batch[p]

        # Phase is now TRUMP_SELECTION (Trump Chooser inspects first 5 cards and declares trump)
        self.phase = "TRUMP_SELECTION"
        self.current_turn = self.trump_chooser

    def select_trump(self, suit: str, player: str = None) -> bool:
        """Trump Chooser declares trump suit from their initial 5 cards."""
        if self.phase != "TRUMP_SELECTION":
            return False
        if player and player != self.trump_chooser:
            return False

        clean_suit = suit.upper().strip()
        if clean_suit not in ('S', 'H', 'D', 'C'):
            return False

        self.trump_suit = clean_suit

        # Stage 2 & 3: Deal remaining 3 cards, then 2 cards to all players clockwise (total 10 cards each)
        deal_order = getattr(self, "deal_order", self.players)
        stage_2_batch = self.deck.deal_batch(3, deal_order)
        stage_3_batch = self.deck.deal_batch(2, deal_order)

        for p in self.players:
            self.hands[p].extend(stage_2_batch[p])
            self.hands[p].extend(stage_3_batch[p])

        # After dealing, check if there are debts to settle
        has_debts = any(ds for ds in self.debts.values() if ds)

        if has_debts:
            if self.penalty_mode == "quota_adjustment":
                self._prepare_pending_adjustments()
                self.phase = "PENALTY_ADJUSTMENT"
                self.current_turn = self.trump_chooser
            elif self.penalty_mode == "card_swap_forced":
                self.build_penalty_queue()
                if self.penalty_queue:
                    self.phase = "PENALTY_RESOLUTION"
                    self.advance_penalty()
                else:
                    self.phase = "TRICK_PLAYING"
                    self.current_turn = self.trump_chooser
            else:
                # Default: Per-debtor choice!
                # Each player who took less tricks (debtor) chooses Tash Khinchai or Extra Tricks
                self._build_debt_choice_list()
                if self.debt_choice_list:
                    self.phase = "DEBT_SETTLEMENT_CHOICE"
                    self.debt_choice_idx = 0
                    self._set_current_debt_chooser()
                else:
                    self.phase = "TRICK_PLAYING"
                    self.current_turn = self.trump_chooser
        else:
            self.phase = "TRICK_PLAYING"
            self.current_turn = self.trump_chooser

        return True

    def _build_debt_choice_list(self):
        """Builds a list of debts where each debtor (less tricks) must choose settlement method."""
        self.debt_choice_list = []
        self.debt_choices_made = {}
        for creditor, debtors in self.debts.items():
            for debtor, count in debtors.items():
                if count > 0:
                    self.debt_choice_list.append({
                        "creditor": creditor,
                        "debtor": debtor,
                        "count": count,
                        "creditor_name": self.player_names.get(creditor, creditor),
                        "debtor_name": self.player_names.get(debtor, debtor),
                        "choice": None  # will be "card_swap" or "quota_adjustment"
                    })

    def _set_current_debt_chooser(self):
        """Sets current_turn to the debtor who needs to make the next choice."""
        if self.debt_choice_idx < len(self.debt_choice_list):
            self.current_turn = self.debt_choice_list[self.debt_choice_idx]["debtor"]
        else:
            self._process_all_debt_choices()

    def make_debt_choice(self, debtor: str, choice: str) -> bool:
        """Debtor chooses settlement method: 'card_swap' (Tash Khinchai) or 'quota_adjustment' (Give Extra Tricks)."""
        if self.phase != "DEBT_SETTLEMENT_CHOICE":
            return False
        if self.debt_choice_idx >= len(self.debt_choice_list):
            return False

        current_debt = self.debt_choice_list[self.debt_choice_idx]
        if current_debt["debtor"] != debtor:
            return False
        if choice not in ("card_swap", "quota_adjustment"):
            return False

        current_debt["choice"] = choice
        key = f"{current_debt['creditor']}:{current_debt['debtor']}"
        self.debt_choices_made[key] = choice

        choice_label = "Tash Khinchai (Card Pull)" if choice == "card_swap" else "Give Extra Tricks"
        self.logs.append(
            f"⚖️ {self.player_names.get(debtor, debtor)} chose '{choice_label}' "
            f"for {current_debt['count']} trick(s) owed to {current_debt['creditor_name']}"
        )

        self.debt_choice_idx += 1
        self._set_current_debt_chooser()
        return True

    def _process_all_debt_choices(self):
        """After all debtors have chosen, apply quota adjustments and build card swap queue."""
        # 1. Apply quota adjustments for "quota_adjustment" choices
        qa_debts = [d for d in self.debt_choice_list if d["choice"] == "quota_adjustment"]
        for debt in qa_debts:
            c = debt["creditor"]
            d = debt["debtor"]
            cnt = debt["count"]
            # Debtor took fewer tricks, so debtor promises +cnt extra tricks (quota increases)
            # Creditor receives the extra tricks (creditor quota decreases)
            self.quotas[d] = self.quotas.get(d, 0) + cnt
            self.quotas[c] = max(0, self.quotas.get(c, 0) - cnt)
            self.logs.append(
                f"🎯 Quota adjusted: {debt['debtor_name']} promises {cnt} extra tricks (now needs {self.quotas[d]}), "
                f"{debt['creditor_name']} now needs {self.quotas[c]}"
            )
            # Clear this specific debt
            if d in self.debts.get(c, {}):
                del self.debts[c][d]

        # 2. Build penalty queue for "card_swap" choices (Tash Khinchai)
        cs_debts = [d for d in self.debt_choice_list if d["choice"] == "card_swap"]
        self.penalty_queue = []
        for debt in cs_debts:
            for i in range(debt["count"]):
                self.penalty_queue.append({
                    "creditor": debt["creditor"],
                    "debtor": debt["debtor"],
                    "puller": debt["creditor"],
                    "target": debt["debtor"],
                    "count": 1,
                    "step_index": i + 1,
                    "total_steps": debt["count"],
                    "pulled_card": None,
                    "returned_card": None,
                    "step": "PULL"
                })
            # Clear this specific debt
            if debt["debtor"] in self.debts.get(debt["creditor"], {}):
                del self.debts[debt["creditor"]][debt["debtor"]]

        # 3. Transition to next phase
        if self.penalty_queue:
            self.phase = "PENALTY_RESOLUTION"
            self.advance_penalty()
        else:
            self.debts = {p: {} for p in self.players}
            self.phase = "TRICK_PLAYING"
            self.current_turn = self.trump_chooser
            self.logs.append("✅ All debts settled via extra tricks. Trick play begins!")

    def _prepare_pending_adjustments(self):
        """Legacy helper for quota_adjustment mode."""
        self.pending_adjustments = []
        self.adjusted_quotas = dict(self.quotas)
        for creditor, debtors in self.debts.items():
            for debtor, count in debtors.items():
                if count > 0:
                    self.pending_adjustments.append({
                        "creditor": creditor,
                        "debtor": debtor,
                        "count": count,
                        "creditor_name": self.player_names.get(creditor, creditor),
                        "debtor_name": self.player_names.get(debtor, debtor)
                    })
                    self.adjusted_quotas[creditor] = self.adjusted_quotas.get(creditor, 0) + count
                    self.adjusted_quotas[debtor] = max(0, self.adjusted_quotas.get(debtor, 0) - count)

    def acknowledge_adjustment(self, player: str = None) -> bool:
        """Player acknowledges quota adjustments, transitioning to trick play."""
        if self.phase != "PENALTY_ADJUSTMENT":
            return False
        if hasattr(self, "adjusted_quotas"):
            self.quotas = dict(self.adjusted_quotas)
        self.debts = {p: {} for p in self.players}
        self.phase = "TRICK_PLAYING"
        self.current_turn = self.trump_chooser
        self.logs.append("✅ Quota adjustments confirmed. Trick play begins!")
        return True

    def build_penalty_queue(self):
        """Legacy: Converts ALL debts into card swap penalty queue."""
        self.penalty_queue = []
        for creditor, debtors in self.debts.items():
            for debtor, count in debtors.items():
                for i in range(count):
                    self.penalty_queue.append({
                        "creditor": creditor,
                        "debtor": debtor,
                        "puller": creditor,
                        "target": debtor,
                        "count": 1,
                        "step_index": i + 1,
                        "total_steps": count,
                        "pulled_card": None,
                        "returned_card": None,
                        "step": "PULL"
                    })

    def advance_penalty(self):
        """Advances to the next penalty in queue, or transitions to trick play if queue is empty."""
        if self.penalty_queue:
            self.current_penalty = self.penalty_queue.pop(0)
            self.current_penalty["step"] = "PULL"
            self.current_turn = self.current_penalty["creditor"]
        else:
            self.current_penalty = None
            self.phase = "TRICK_PLAYING"
            self.current_turn = self.trump_chooser
            self.debts = {p: {} for p in self.players}
            self.logs.append("✅ All penalty cards swapped. Trick play begins!")

    def pull_penalty_card(self, creditor: str, card_index: int = None) -> Optional[Card]:
        """Creditor blindly pulls a card from debtor's hand."""
        if self.phase != "PENALTY_RESOLUTION" or not self.current_penalty:
            return None
        if self.current_penalty["step"] != "PULL" or self.current_penalty["creditor"] != creditor:
            return None

        debtor = self.current_penalty["debtor"]
        debtor_hand = self.hands[debtor]
        if not debtor_hand:
            return None

        if card_index is None or card_index < 0 or card_index >= len(debtor_hand):
            card_index = random.randint(0, len(debtor_hand) - 1)

        pulled = debtor_hand.pop(card_index)
        self.hands[creditor].append(pulled)
        self.current_penalty["pulled_card"] = pulled
        self.current_penalty["step"] = "RETURN"
        self.current_turn = creditor
        return pulled

    def return_penalty_card(self, creditor: str, card_code: str) -> bool:
        """Creditor gives an unwanted card back to debtor."""
        if self.phase != "PENALTY_RESOLUTION" or not self.current_penalty:
            return False
        if self.current_penalty["step"] != "RETURN" or self.current_penalty["creditor"] != creditor:
            return False

        clean_code = card_code.upper().strip()
        matching = [c for c in self.hands[creditor] if c.code == clean_code]
        if not matching:
            return False

        card = matching[0]
        self.hands[creditor].remove(card)
        self.hands[self.current_penalty["debtor"]].append(card)

        self.current_penalty["returned_card"] = card
        self.current_penalty["step"] = "DONE"
        self.advance_penalty()
        return True

    def get_legal_moves(self, player: str) -> List[Card]:
        """Calculates legal cards for current turn: must follow suit if possible, else any card."""
        hand = self.hands.get(player, [])
        if not hand:
            return []

        # If opening trick lead, any card is legal
        if not self.current_trick or not self.led_suit:
            return list(hand)

        same_suit = [c for c in hand if c.suit.value == self.led_suit]
        if same_suit:
            return same_suit
        
        # Player is void in led suit: can play any card (trump or off-suit)
        return list(hand)

    def play_card(self, player: str, card_code: str) -> Dict[str, Any]:
        """Executes a card play in current trick."""
        if self.phase != "TRICK_PLAYING":
            return {"success": False, "error": "Not in trick playing phase"}
        if self.current_turn != player:
            return {"success": False, "error": f"Not {player}'s turn"}

        legal_cards = self.get_legal_moves(player)
        clean_code = card_code.upper().strip()
        chosen = next((c for c in legal_cards if c.code == clean_code), None)
        if not chosen:
            return {"success": False, "error": "Illegal card play"}

        # Remove card from hand
        self.hands[player].remove(chosen)

        # Set led suit if first card in trick
        if not self.current_trick:
            self.led_suit = chosen.suit.value

        self.current_trick.append({"player": player, "card": chosen})

        # Check if trick is complete (3 plays)
        if len(self.current_trick) == 3:
            win_idx, win_card = evaluate_trick_winner(self.current_trick, self.trump_suit)
            winner = self.current_trick[win_idx]["player"]
            self.tricks_won[winner] += 1
            self.last_trick_winner = winner

            trick_record = {
                "trick_number": self.current_trick_number,
                "lead_player": self.current_trick[0]["player"],
                "winner": winner,
                "winning_card": win_card.code,
                "plays": [{"player": p["player"], "card": p["card"].code} for p in self.current_trick],
                "cards": [
                    {"player": p["player"], "player_id": p["player"], "card": p["card"].to_dict()}
                    for p in self.current_trick
                ]
            }
            self.trick_history.append(trick_record)

            if self.current_trick_number >= 10:
                self.finalize_round()
                return {"success": True, "trick_complete": True, "round_over": True, "winner": winner}
            else:
                self.current_trick_number += 1
                self.current_trick = []
                self.led_suit = None
                self.current_turn = winner
                return {"success": True, "trick_complete": True, "round_over": False, "winner": winner}
        else:
            # Advance turn clockwise: P1 -> P2 -> P3 -> P1
            order = ["P1", "P2", "P3"]
            next_idx = (order.index(player) + 1) % 3
            self.current_turn = order[next_idx]
            return {"success": True, "trick_complete": False, "round_over": False}

    def finalize_round(self):
        """Calculates final scores, updates debts for next round, and prepares round summary."""
        self.phase = "ROUND_OVER"
        self.current_turn = None

        net_scores = {}
        for p in self.players:
            won = self.tricks_won[p]
            quota = self.quotas[p]
            net = won - quota
            net_scores[p] = net
            self.cumulative_scores[p] += net

        # Determine debts for next round
        # Creditors (net > 0) pull from Debtors (net < 0)
        creditors = {p: net_scores[p] for p in self.players if net_scores[p] > 0}
        debtors = {p: -net_scores[p] for p in self.players if net_scores[p] < 0}

        new_debts: Dict[str, Dict[str, int]] = {p: {} for p in self.players}
        # Match creditors to debtors
        cred_keys = list(creditors.keys())
        debt_keys = list(debtors.keys())

        for c in cred_keys:
            while creditors[c] > 0:
                for d in debt_keys:
                    if debtors[d] > 0:
                        pull_count = min(creditors[c], debtors[d])
                        new_debts[c][d] = new_debts[c].get(d, 0) + pull_count
                        creditors[c] -= pull_count
                        debtors[d] -= pull_count
                        if creditors[c] == 0:
                            break

        self.debts = new_debts

        # Round Summary Record
        self.round_summary = {
            "round_number": self.round_number,
            "dealer": self.dealer,
            "trump_chooser": self.trump_chooser,
            "bystander": self.bystander,
            "trump_suit": self.trump_suit,
            "quotas": dict(self.quotas),
            "tricks_won": dict(self.tricks_won),
            "net_scores": dict(net_scores),
            "cumulative_scores": dict(self.cumulative_scores),
            "debts_for_next_round": {c: dict(ds) for c, ds in self.debts.items() if ds}
        }

    def next_round(self):
        """Rotates dealer clockwise and initiates next round."""
        order = ["P1", "P2", "P3"]
        dealer_idx = order.index(self.dealer)
        self.dealer = order[(dealer_idx + 1) % 3]
        self.round_number += 1
        self.start_new_round()

    def step_bot(self) -> Dict[str, Any]:
        """Performs automatic AI bot action if current turn is an AI."""
        if not self.current_turn or self.player_types.get(self.current_turn) != "ai":
            # Special case: DEBT_SETTLEMENT_CHOICE when human debtor — do nothing
            return {"action": "none", "bot": False}

        bot = self.current_turn

        # CASE 0: Bot makes debt settlement choice
        if self.phase == "DEBT_SETTLEMENT_CHOICE":
            # AI defaults to card_swap (Tash Khinchai)
            import random as _rng
            choice = _rng.choice(["card_swap", "quota_adjustment"])
            self.make_debt_choice(bot, choice)
            return {"action": "debt_choice_made", "player": bot, "choice": choice, "bot": True}

        # CASE 1: Bot needs to select Trump
        if self.phase == "TRUMP_SELECTION" and bot == self.trump_chooser:
            trump_choice = select_tikdi_trump(self.hands[bot])
            self.select_trump(trump_choice, bot)
            return {"action": "trump_selected", "player": bot, "trump_suit": trump_choice}

        # CASE 2: Bot needs to pull penalty card
        if self.phase == "PENALTY_RESOLUTION" and self.current_penalty:
            if self.current_penalty["step"] == "PULL" and bot == self.current_penalty["creditor"]:
                pulled = self.pull_penalty_card(bot)
                return {"action": "penalty_pulled", "player": bot, "card": pulled.code if pulled else None}
            elif self.current_penalty["step"] == "RETURN" and bot == self.current_penalty["creditor"]:
                ret_card = select_penalty_return_card(self.hands[bot], self.trump_suit)
                self.return_penalty_card(bot, ret_card.code)
                return {"action": "penalty_returned", "player": bot, "card": ret_card.code}

        # CASE 3: Bot plays a card in Trick
        if self.phase == "TRICK_PLAYING":
            legal = self.get_legal_moves(bot)
            card = select_tikdi_bot_play(
                self.hands[bot],
                legal,
                self.current_trick,
                self.trump_suit,
                self.led_suit
            )
            res = self.play_card(bot, card.code)
            return {"action": "card_played", "player": bot, "card": card.code, "result": res}

        return {"action": "none", "bot": True}

    def to_dict(self, perspective_player: str = "P1") -> Dict[str, Any]:
        """Serializes game state for frontend API consumption."""
        hands_display = {}
        for p in self.players:
            if p == perspective_player:
                hands_display[p] = [c.to_dict() for c in sorted(self.hands[p], key=lambda c: (c.suit.value, c.rank.value))]
            else:
                # Obscure opponent cards
                hands_display[p] = [{"code": "BACK"} for _ in self.hands[p]]

        legal_codes = []
        if self.current_turn == perspective_player and self.phase == "TRICK_PLAYING":
            legal_codes = [c.code for c in self.get_legal_moves(perspective_player)]

        return {
            "game_id": self.game_id,
            "game_type": "tikdi",
            "round_number": self.round_number,
            "phase": self.phase,
            "dealer": self.dealer,
            "dealer_id": self.dealer,
            "trump_chooser": self.trump_chooser,
            "trump_chooser_id": self.trump_chooser,
            "bystander": self.bystander,
            "bystander_id": self.bystander,
            "quotas": self.quotas,
            "tricks_won": self.tricks_won,
            "cumulative_scores": self.cumulative_scores,
            "scores": {p: self.tricks_won.get(p, 0) - self.quotas.get(p, 0) for p in self.players},
            "trump_suit": self.trump_suit,
            "current_turn": self.current_turn,
            "led_suit": self.led_suit,
            "trick_number": self.current_trick_number,
            "current_trick_number": self.current_trick_number,
            "current_trick": [
                {"player": p["player"], "player_id": p["player"], "card": p["card"].to_dict()}
                for p in self.current_trick
            ],
            "last_completed_trick": (
                self.trick_history[-1].get("cards", []) if self.trick_history else []
            ),
            "last_trick_winner": self.last_trick_winner,
            "trick_history": self.trick_history[-3:],  # Last 3 tricks for summary
            "player_names": self.player_names,
            "player_types": self.player_types,
            "hands": hands_display,
            "legal_moves": legal_codes,
            "round_summary": self.round_summary,
            "current_penalty": self.current_penalty,
            "penalty_queue": self.penalty_queue,
            "debts": {c: dict(ds) for c, ds in self.debts.items() if ds},
            "penalty_mode": getattr(self, "penalty_mode", "card_swap"),
            "debt_choice_list": getattr(self, "debt_choice_list", []),
            "debt_choice_idx": getattr(self, "debt_choice_idx", 0),
            "current_debt_choice": (
                self.debt_choice_list[self.debt_choice_idx]
                if self.phase == "DEBT_SETTLEMENT_CHOICE"
                   and hasattr(self, "debt_choice_list")
                   and self.debt_choice_idx < len(self.debt_choice_list)
                else None
            ),
            "pending_adjustments": getattr(self, "pending_adjustments", []),
            "adjusted_quotas": getattr(self, "adjusted_quotas", {}),
            "base_quotas": getattr(self, "base_quotas", {}),
            "is_first_deal_stage": (self.phase == "TRUMP_SELECTION" and len(self.hands.get(self.trump_chooser, [])) == 5),
            "first_5_cards": [c.to_dict() for c in sorted(self.hands.get(self.trump_chooser, []), key=lambda c: (c.suit.value, c.rank.value))] if self.phase == "TRUMP_SELECTION" and self.hands.get(self.trump_chooser) else [],
            "logs": getattr(self, "logs", [])
        }
