"""
BindiCoatSession — Full game session controller for Mindikot / Bindikot (Bandh Hukum variant).

Rules Summary:
- 4 players in 2 fixed partnerships: Team NS (P1+P3) vs Team EW (P2+P4).
- Deck: 52 cards. Each player gets 13 cards.
- Dealing in two stages: 5 cards first, then Trump Placer selects Bandh Hukum (1 card face-down),
  then 8 more cards dealt to each.
- Trump is hidden until any player is void in led suit → "Hukum Kholo!" → trump revealed.
- Primary win: capture most Mindis (the four 10s). Tie-break: 7+ tricks wins.
- KOT: 4 Mindis + 7+ tricks. White-Wash: 4 Mindis + all 13 tricks.
"""
import random
from typing import List, Dict, Optional, Any, Tuple

try:
    from backend.engine.bindi_coat.bindi_coat_ai import (
        select_bandh_hukum,
        select_play_card,
        get_legal_moves,
        is_mindi,
        card_suit,
        card_rank,
        _trick_winner,
    )
except ImportError:
    from engine.bindi_coat.bindi_coat_ai import (
        select_bandh_hukum,
        select_play_card,
        get_legal_moves,
        is_mindi,
        card_suit,
        card_rank,
        _trick_winner,
    )


# ─── Deck & Card Helpers ─────────────────────────────────────────────────────

SUITS = ['H', 'D', 'C', 'S']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

SUIT_SYMBOL = {'H': '♥', 'D': '♦', 'C': '♣', 'S': '♠'}
SUIT_NAME = {'H': 'Hearts', 'D': 'Diamonds', 'C': 'Clubs', 'S': 'Spades'}
RANK_DISPLAY = {
    '2': '2', '3': '3', '4': '4', '5': '5', '6': '6', '7': '7',
    '8': '8', '9': '9', '10': '10', 'J': 'Jack', 'Q': 'Queen', 'K': 'King', 'A': 'Ace'
}

# Partnerships: P1+P3 = NS, P2+P4 = EW
TEAMS = {
    "NS": ["P1", "P3"],
    "EW": ["P2", "P4"],
}
PLAYER_TEAM = {"P1": "NS", "P2": "EW", "P3": "NS", "P4": "EW"}
PLAYER_PARTNER = {"P1": "P3", "P2": "P4", "P3": "P1", "P4": "P2"}
PLAYER_POSITION = {"P1": "South", "P2": "East", "P3": "North", "P4": "West"}


def build_deck() -> List[str]:
    """Returns a fresh shuffled 52-card deck."""
    deck = [f"{r}{s}" for s in SUITS for r in RANKS]
    random.shuffle(deck)
    return deck


def card_display(code: str) -> str:
    r = code[:-1]
    s = code[-1]
    return f"{r}{SUIT_SYMBOL.get(s, s)}"


DEFAULT_BOT_NAMES = {
    "P2": "G. Dinesh",
    "P3": "G. Bhimaram",
    "P4": "G. Geeta",
}


# ─── BindiCoatSession ────────────────────────────────────────────────────────

class BindiCoatSession:
    """
    Complete Mindikot / Bindikot session with Bandh Hukum (hidden trump) variant.

    Phases:
    - DEALING_5: First 5 cards being dealt (auto-happens on start).
    - BANDH_HUKUM_SELECTION: Trump Placer must choose 1 card to place face-down.
    - DEALING_REST: Remaining 8 cards being dealt (auto-happens).
    - PLAYING: Normal trick-taking in progress.
    - TRUMP_REVEALED: Trump just revealed (transient, auto-advances).
    - ROUND_SUMMARY: All 13 tricks done; show results.
    """

    def __init__(
        self,
        game_id: str = "bc1",
        host_name: str = "Player",
        player_names: Optional[Dict[str, str]] = None,
        player_types: Optional[Dict[str, str]] = None,
    ):
        self.game_id = game_id
        self.players = ["P1", "P2", "P3", "P4"]

        # Names & types
        self.player_names: Dict[str, str] = {
            "P1": host_name,
            "P2": DEFAULT_BOT_NAMES["P2"],
            "P3": DEFAULT_BOT_NAMES["P3"],
            "P4": DEFAULT_BOT_NAMES["P4"],
        }
        self.player_types: Dict[str, str] = {
            "P1": "human",
            "P2": "ai",
            "P3": "ai",
            "P4": "ai",
        }
        if player_names:
            self.player_names.update(player_names)
        if player_types:
            self.player_types.update(player_types)

        # Match state
        self.round_number: int = 1
        self.dealer: str = "P4"  # Dealer rotates; first dealer = P4 (West)
        self.trump_placer: str = "P1"  # Player to dealer's left leads & places Bandh Hukum
        self.dealer_order = ["P1", "P2", "P3", "P4"]

        # Round state
        self.hands: Dict[str, List[str]] = {p: [] for p in self.players}
        self.bandh_hukum_card: Optional[str] = None   # The hidden trump card code
        self.trump_suit: Optional[str] = None          # Revealed when Hukum Kholo
        self.trump_revealed: bool = False
        self.trump_reveal_trick: Optional[int] = None

        # Trick state
        self.current_trick: List[Dict[str, Any]] = []  # [{player_id, card}]
        self.current_trick_number: int = 1
        self.current_turn: Optional[str] = None
        self.led_suit: Optional[str] = None

        # Scores
        self.tricks_won: Dict[str, int] = {p: 0 for p in self.players}
        self.mindis_won: Dict[str, List[str]] = {p: [] for p in self.players}  # pid → list of mindi codes
        self.team_tricks: Dict[str, int] = {"NS": 0, "EW": 0}
        self.team_mindis: Dict[str, int] = {"NS": 0, "EW": 0}

        # Match-level cumulative
        self.match_scores: Dict[str, int] = {"NS": 0, "EW": 0}  # wins per team
        self.kots: Dict[str, int] = {"NS": 0, "EW": 0}

        # Trick history
        self.trick_history: List[Dict] = []

        # Phase & summary
        self.phase: str = "DEALING_5"
        self.round_summary: Optional[Dict] = None
        self.logs: List[str] = []

        # Start first round
        self._init_round()

    # ─── Round Init ──────────────────────────────────────────────────────────

    def _resolve_roles(self):
        """Trump Placer is player to the left of the Dealer (clockwise)."""
        order = ["P1", "P2", "P3", "P4"]
        dealer_idx = order.index(self.dealer)
        self.trump_placer = order[(dealer_idx + 1) % 4]

    def _init_round(self):
        """Sets up a new round: deal 5 cards, wait for Bandh Hukum selection."""
        self._resolve_roles()

        self.hands = {p: [] for p in self.players}
        self.bandh_hukum_card = None
        self.trump_suit = None
        self.trump_revealed = False
        self.trump_reveal_trick = None
        self.current_trick = []
        self.current_trick_number = 1
        self.led_suit = None
        self.tricks_won = {p: 0 for p in self.players}
        self.mindis_won = {p: [] for p in self.players}
        self.team_tricks = {"NS": 0, "EW": 0}
        self.team_mindis = {"NS": 0, "EW": 0}
        self.trick_history = []
        self.round_summary = None

        # Deal 5 cards to each player
        deck = build_deck()
        for i in range(5 * 4):
            pid = self.players[i % 4]
            self.hands[pid].append(deck[i])
        self._remaining_deck = deck[20:]  # 32 remaining cards

        self.phase = "BANDH_HUKUM_SELECTION"
        self.logs.append(
            f"Round {self.round_number} started. Dealer: {self.player_names[self.dealer]} | "
            f"Trump Placer: {self.player_names[self.trump_placer]}"
        )
        self.logs.append("5 cards dealt. Waiting for Bandh Hukum selection...")

        # Auto: if trump placer is bot, it selects blindly immediately
        if self.player_types.get(self.trump_placer) == "ai":
            import random
            chosen_idx = random.randint(0, len(self.hands[self.trump_placer]) - 1)
            self.select_bandh_hukum(self.trump_placer, card_index=chosen_idx)

    def select_bandh_hukum(
        self,
        player_id: str,
        card_code: Optional[str] = None,
        card_index: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Trump Placer places one card face-down as the Bandh Hukum (blind hidden trump).

        Args:
            player_id: Must be the trump_placer.
            card_code: Optional card code from their hand to place face-down.
            card_index: Optional 0-indexed position in hand (for blind picking).

        Returns:
            Result dict.
        """
        if self.phase != "BANDH_HUKUM_SELECTION":
            return {"success": False, "error": f"Not in BANDH_HUKUM_SELECTION phase"}
        if player_id != self.trump_placer:
            return {"success": False, "error": f"Only {self.trump_placer} places Bandh Hukum"}

        hand = self.hands.get(player_id, [])
        if card_index is not None:
            if card_index < 0 or card_index >= len(hand):
                return {"success": False, "error": f"Card index {card_index} out of range (0-{len(hand)-1})"}
            card_code = hand[card_index]
        elif card_code is not None:
            if card_code not in hand:
                return {"success": False, "error": f"Card {card_code} not in {player_id}'s hand"}
        else:
            return {"success": False, "error": "Either card_index or card_code must be provided"}

        # Remove card from hand and place face-down as secret Bandh Hukum
        hand.remove(card_code)
        self.bandh_hukum_card = card_code
        self.trump_suit = card_code[-1]  # suit is the trump (secretly stored in engine, but hidden from players)

        self.logs.append(
            f"🔒 {self.player_names[player_id]} placed Bandh Hukum face-down blindly. "
            f"Trump is completely secret — no one knows what it is until revealed!"
        )

        # Deal remaining 8 cards to each
        self._deal_remaining()
        return {"success": True, "state": self.to_dict("P1")}

    def _deal_remaining(self):
        """Deals remaining 8 cards to each player (total 13 each after Bandh Hukum)."""
        deck = self._remaining_deck
        # Trump placer already has 4 (5-1). Others have 5. Need to give placer 9 more, others 8 more.
        # Actually: after placing BH, placer has 4 cards, others have 5.
        # We need everyone at 13: placer needs 9 more, others need 8 more.
        idx = 0
        for r in range(8):
            for pid in self.players:
                if idx < len(deck):
                    self.hands[pid].append(deck[idx])
                    idx += 1

        # Give trump placer extra card (1 extra round)
        if idx < len(deck):
            self.hands[self.trump_placer].append(deck[idx])

        self.phase = "PLAYING"
        self.current_turn = self.trump_placer  # Trump placer leads first
        self.logs.append(
            f"All cards dealt. {self.player_names[self.trump_placer]} leads Trick 1."
        )

    # ─── Trick Playing ────────────────────────────────────────────────────────

    def play_card(self, player_id: str, card_code: str) -> Dict[str, Any]:
        """
        Player plays a card in the current trick.

        Returns:
            Result dict with 'success' and 'trump_revealed' flag if applicable.
        """
        if self.phase != "PLAYING":
            return {"success": False, "error": f"Not in PLAYING phase (current: {self.phase})"}
        if player_id != self.current_turn:
            return {"success": False, "error": f"Not {player_id}'s turn (current: {self.current_turn})"}

        hand = self.hands[player_id]
        if card_code not in hand:
            return {"success": False, "error": f"Card {card_code} not in {player_id}'s hand"}

        # Validate legality
        is_leading = len(self.current_trick) == 0
        legal = get_legal_moves(
            hand, self.led_suit, self.trump_revealed, self.trump_suit, is_leading
        )
        if card_code not in legal:
            return {"success": False, "error": f"Card {card_code} is not a legal play. Legal: {legal}"}

        # Check if this move triggers trump reveal (player void in led suit)
        triggered_reveal = False
        if not is_leading and not self.trump_revealed:
            c_suit = card_suite = card_code[-1]
            if self.led_suit and c_suit != self.led_suit:
                # Player is void in led suit → reveal trump!
                triggered_reveal = True
                self._reveal_trump(player_id)

        # Play the card
        hand.remove(card_code)
        self.current_trick.append({"player_id": player_id, "card": card_code})
        if is_leading:
            self.led_suit = card_code[-1]

        disp = card_display(card_code)
        self.logs.append(f"  {self.player_names[player_id]} plays {disp}")

        # If trick is complete (all 4 players played)
        if len(self.current_trick) == 4:
            return self._resolve_trick()

        # Advance turn clockwise
        self._advance_turn()
        result = {"success": True, "trick_complete": False, "trump_revealed": triggered_reveal}
        return result

    def _reveal_trump(self, triggering_player: str):
        """Reveals the Bandh Hukum card and announces the trump suit."""
        self.trump_revealed = True
        self.trump_reveal_trick = self.current_trick_number
        trump_name = {"H": "Hearts ♥", "D": "Diamonds ♦", "C": "Clubs ♣", "S": "Spades ♠"}.get(
            self.trump_suit, self.trump_suit
        )
        bh_display = card_display(self.bandh_hukum_card)
        # Trump placer gets the revealed card back
        self.hands[self.trump_placer].append(self.bandh_hukum_card)
        self.logs.append(
            f"🔓 HUKUM KHOLO! {self.player_names[triggering_player]} is void → Trump revealed: "
            f"{bh_display} → {trump_name} is TRUMP!"
        )
        self.logs.append(
            f"  {self.player_names[self.trump_placer]} takes back their Bandh Hukum card ({bh_display})."
        )

    def _advance_turn(self):
        """Moves to the next player clockwise."""
        order = ["P1", "P2", "P3", "P4"]
        idx = order.index(self.current_turn)
        self.current_turn = order[(idx + 1) % 4]

    def _resolve_trick(self) -> Dict[str, Any]:
        """Resolves the completed 4-card trick and sets up the next."""
        # Determine winner
        winner_card, winner_id = _trick_winner(
            [{"card": e["card"], "player_id": e["player_id"]} for e in self.current_trick],
            self.trump_suit if self.trump_revealed else None
        )

        # Check for Mindis in trick
        trick_mindis = [e["card"] for e in self.current_trick if is_mindi(e["card"])]

        # Assign trick & Mindis to winner's team
        self.tricks_won[winner_id] += 1
        winner_team = PLAYER_TEAM[winner_id]
        self.team_tricks[winner_team] += 1

        for mindi_card in trick_mindis:
            self.mindis_won[winner_id].append(mindi_card)
            self.team_mindis[winner_team] += 1

        # Build history entry
        trick_entry = {
            "trick_number": self.current_trick_number,
            "plays": [{"player_id": e["player_id"], "card": e["card"]} for e in self.current_trick],
            "winner": winner_id,
            "winner_team": winner_team,
            "mindis_captured": trick_mindis,
        }
        self.trick_history.append(trick_entry)

        mindi_msg = f" (Mindis: {[card_display(m) for m in trick_mindis]})" if trick_mindis else ""
        self.logs.append(
            f"Trick {self.current_trick_number}: {self.player_names[winner_id]} wins{mindi_msg}. "
            f"[NS: {self.team_tricks['NS']}T/{self.team_mindis['NS']}M | "
            f"EW: {self.team_tricks['EW']}T/{self.team_mindis['EW']}M]"
        )

        self.current_trick_number += 1
        self.current_trick = []
        self.led_suit = None

        # Check if all 13 tricks done
        if self.current_trick_number > 13:
            return self._resolve_round()

        # Next trick led by winner
        self.current_turn = winner_id
        return {"success": True, "trick_complete": True, "trick_winner": winner_id, "winner_team": winner_team,
                "mindis_captured": trick_mindis, "trump_revealed": self.trump_revealed}

    def _resolve_round(self) -> Dict[str, Any]:
        """Calculates round results after all 13 tricks."""
        ns_mindis = self.team_mindis["NS"]
        ew_mindis = self.team_mindis["EW"]
        ns_tricks = self.team_tricks["NS"]
        ew_tricks = self.team_tricks["EW"]

        # Determine winner
        if ns_mindis > ew_mindis:
            winning_team = "NS"
        elif ew_mindis > ns_mindis:
            winning_team = "EW"
        else:
            # 2-2 tie — trick tiebreak
            winning_team = "NS" if ns_tricks >= 7 else "EW"

        # KOT / White-Wash check
        victory_type = "Regular"
        winning_mindis = self.team_mindis[winning_team]
        winning_tricks = self.team_tricks[winning_team]
        if winning_mindis == 4 and winning_tricks >= 7:
            victory_type = "KOT"
            self.kots[winning_team] += 1
        if winning_mindis == 4 and winning_tricks == 13:
            victory_type = "WHITE_WASH"
            self.kots[winning_team] += 1  # extra point

        self.match_scores[winning_team] += 1
        losing_team = "EW" if winning_team == "NS" else "NS"

        self.phase = "ROUND_SUMMARY"
        self.round_summary = {
            "round_number": self.round_number,
            "winning_team": winning_team,
            "losing_team": losing_team,
            "victory_type": victory_type,
            "ns_mindis": ns_mindis,
            "ew_mindis": ew_mindis,
            "ns_tricks": ns_tricks,
            "ew_tricks": ew_tricks,
            "mindis_detail": {
                "NS": [card_display(c) for p in TEAMS["NS"] for c in self.mindis_won[p]],
                "EW": [card_display(c) for p in TEAMS["EW"] for c in self.mindis_won[p]],
            },
            "match_scores": dict(self.match_scores),
            "kots": dict(self.kots),
        }

        kot_msg = f" — {victory_type}!" if victory_type != "Regular" else ""
        self.logs.append(
            f"🏆 Round {self.round_number} OVER. Team {winning_team} WINS{kot_msg} "
            f"({winning_mindis} Mindis, {winning_tricks} Tricks)."
        )

        return {"success": True, "trick_complete": True, "round_over": True, "summary": self.round_summary}

    def next_round(self):
        """Starts a new round, rotating dealer clockwise."""
        order = ["P1", "P2", "P3", "P4"]
        idx = order.index(self.dealer)
        self.dealer = order[(idx + 1) % 4]
        self.round_number += 1
        self._init_round()

    # ─── Bot Step ─────────────────────────────────────────────────────────────

    def step_bot(self) -> Dict[str, Any]:
        """
        Executes one bot action (Bandh Hukum selection or card play).
        Returns a dict describing what the bot did.
        """
        if self.phase == "BANDH_HUKUM_SELECTION":
            pid = self.trump_placer
            if self.player_types.get(pid) != "ai":
                return {"action": "none", "reason": f"{pid} is human — waiting for Bandh Hukum selection"}
            import random
            card_idx = random.randint(0, len(self.hands[pid]) - 1)
            self.select_bandh_hukum(pid, card_index=card_idx)
            return {"action": "bandh_hukum", "player": pid, "card_index": card_idx}

        if self.phase == "PLAYING":
            pid = self.current_turn
            if not pid or self.player_types.get(pid) != "ai":
                return {"action": "none", "reason": f"{pid} is human" if pid else "No current turn"}

            hand = self.hands[pid]
            is_leading = len(self.current_trick) == 0
            legal = get_legal_moves(
                hand, self.led_suit, self.trump_revealed, self.trump_suit, is_leading
            )

            # Check if any Mindi is in current trick
            mindi_in_trick = any(is_mindi(e["card"]) for e in self.current_trick)

            card = select_play_card(
                hand=hand,
                legal_moves=legal,
                current_trick=[{"player_id": e["player_id"], "card": e["card"]} for e in self.current_trick],
                trump_suit=self.trump_suit if self.trump_revealed else None,
                trump_revealed=self.trump_revealed,
                partner_id=PLAYER_PARTNER.get(pid),
                is_leading=is_leading,
                mindi_in_trick=mindi_in_trick,
            )

            result = self.play_card(pid, card)
            return {"action": "play", "player": pid, "card": card, "result": result}

        if self.phase == "ROUND_SUMMARY":
            return {"action": "none", "reason": "Round is over — call next_round()"}

        return {"action": "none", "reason": f"Unknown phase: {self.phase}"}

    # ─── State Serialization ──────────────────────────────────────────────────

    def to_dict(self, perspective_player: str = "P1") -> Dict[str, Any]:
        """Returns full game state for the given perspective player."""
        is_bh_selection = (self.phase == "BANDH_HUKUM_SELECTION")

        players_info = {}
        for pid in self.players:
            is_me = (pid == perspective_player)
            card_count = len(self.hands[pid])
            if is_me:
                # During Bandh Hukum selection, cards are blind (face-down)
                p_hand = ["BACK"] * card_count if is_bh_selection else [c for c in self.hands[pid]]
            else:
                p_hand = []
            players_info[pid] = {
                "name": self.player_names[pid],
                "type": self.player_types[pid],
                "position": PLAYER_POSITION[pid],
                "team": PLAYER_TEAM[pid],
                "partner": PLAYER_PARTNER[pid],
                "card_count": card_count,
                "hand": p_hand,
                "tricks_won": self.tricks_won[pid],
                "mindis_won": [c for c in self.mindis_won[pid]],
            }

        # Legal moves for perspective player (if their turn and playing)
        my_legal = []
        if self.phase == "PLAYING" and self.current_turn == perspective_player:
            hand = self.hands[perspective_player]
            is_leading = len(self.current_trick) == 0
            my_legal = get_legal_moves(
                hand, self.led_suit, self.trump_revealed, self.trump_suit, is_leading
            )

        # Bandh Hukum info
        bh_info = {
            "card": card_display(self.bandh_hukum_card) if (self.trump_revealed and self.bandh_hukum_card) else None,
            "card_code": self.bandh_hukum_card if self.trump_revealed else None,
            "revealed": self.trump_revealed,
            "trump_suit": self.trump_suit if self.trump_revealed else None,
            "trump_suit_name": SUIT_NAME.get(self.trump_suit, "") if self.trump_revealed else "Hidden",
            "reveal_trick": self.trump_reveal_trick,
            "placer": self.trump_placer,
            "placer_name": self.player_names.get(self.trump_placer, ""),
        }

        return {
            "game_id": self.game_id,
            "phase": self.phase,
            "round_number": self.round_number,
            "dealer": self.dealer,
            "dealer_name": self.player_names.get(self.dealer, ""),
            "trump_placer": self.trump_placer,
            "players": players_info,
            "teams": {
                "NS": {
                    "members": TEAMS["NS"],
                    "tricks": self.team_tricks["NS"],
                    "mindis": self.team_mindis["NS"],
                    "match_wins": self.match_scores["NS"],
                    "kots": self.kots["NS"],
                },
                "EW": {
                    "members": TEAMS["EW"],
                    "tricks": self.team_tricks["EW"],
                    "mindis": self.team_mindis["EW"],
                    "match_wins": self.match_scores["EW"],
                    "kots": self.kots["EW"],
                },
            },
            "current_trick": [
                {"player_id": e["player_id"], "card": e["card"], "display": card_display(e["card"])}
                for e in self.current_trick
            ],
            "current_trick_number": self.current_trick_number,
            "current_turn": self.current_turn,
            "current_turn_name": self.player_names.get(self.current_turn, "") if self.current_turn else "",
            "led_suit": self.led_suit,
            "bandh_hukum": bh_info,
            "my_hand": ["BACK"] * len(self.hands.get(perspective_player, [])) if is_bh_selection else self.hands.get(perspective_player, []),
            "my_legal_moves": my_legal,
            "my_team": PLAYER_TEAM.get(perspective_player, "NS"),
            "is_my_turn": (self.current_turn == perspective_player and self.phase == "PLAYING"),
            "is_trump_placer": (perspective_player == self.trump_placer),
            "trick_history": self.trick_history[-5:],  # last 5 tricks
            "round_summary": self.round_summary,
            "perspective_player": perspective_player,
            "logs": self.logs[-30:],
        }
