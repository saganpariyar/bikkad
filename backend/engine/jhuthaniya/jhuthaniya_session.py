"""
JhuthaniyaSession — Full game session controller for Jhuthaniya (Bluff / Cheat / I Doubt It).

Rules Summary:
- 2–7 players; standard 52-card deck (no jokers).
- Each turn: active player places 1–4 cards face-down into center_pot and declares a rank claim.
- After a claim, other players (clockwise) may challenge ("JHUTH!") or pass.
- Caught bluffing: claimant picks up entire pot.
- Wrongful challenge: challenger picks up entire pot.
- Players who empty their hand (and survive challenge) are SAFE (winners).
- Last player holding cards is the LOSER (Jhuthaniya).
"""
import random
from typing import List, Dict, Optional, Any

from backend.engine.jhuthaniya.jhuthaniya_ai import (
    bot_select_cards_to_play,
    bot_choose_claim_rank,
    bot_should_challenge,
    bot_choose_inspect_index,
    RANK_ORDER,
)

# ─── Card helpers ────────────────────────────────────────────────────────────

SUITS = ['H', 'D', 'C', 'S']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

RANK_DISPLAY = {
    '2': '2', '3': '3', '4': '4', '5': '5', '6': '6', '7': '7',
    '8': '8', '9': '9', '10': '10',
    'J': 'Jack', 'Q': 'Queen (Begam)', 'K': 'King (Badshah)', 'A': 'Ace'
}

SUIT_SYMBOL = {'H': '♥', 'D': '♦', 'C': '♣', 'S': '♠'}


def build_full_deck() -> List[str]:
    """Returns a fresh shuffled 52-card deck as code strings like '10H', 'KS', '2C'."""
    deck = [f"{r}{s}" for s in SUITS for r in RANKS]
    random.shuffle(deck)
    return deck


def card_display(code: str) -> str:
    """Human-readable card string, e.g. '10H' → '10♥'."""
    suit = code[-1]
    rank = code[:-1]
    return f"{rank}{SUIT_SYMBOL.get(suit, suit)}"


# ─── JhuthaniyaSession ───────────────────────────────────────────────────────

DEFAULT_BOT_NAMES = [
    "G. Dinesh", "G. Bhimaram", "G. Geeta", "G. Jitu", "G. Suraj", "G. Kantilal", "G. Prakash", "G. S Kumar"
]


class JhuthaniyaSession:
    """
    Complete Jhuthaniya game session supporting 2–7 players.

    Phases:
    - WAITING: Room not yet started.
    - PLAYING: Active player must make a claim (play cards + declare rank).
    - CHALLENGE_WINDOW: After a claim, waiting for challenges or passes.
    - ROUND_OVER: Only one player left with cards (the Loser).
    """

    def __init__(
        self,
        game_id: str = "jhuth1",
        host_name: str = "Player",
        num_players: int = 4,
        player_names: Optional[Dict[str, str]] = None,
        player_types: Optional[Dict[str, str]] = None,
    ):
        self.game_id = game_id
        self.num_players = max(2, min(7, num_players))
        self.players = [f"P{i+1}" for i in range(self.num_players)]

        # Names
        self.player_names: Dict[str, str] = {}
        self.player_names["P1"] = host_name
        for i, pid in enumerate(self.players[1:], 0):
            self.player_names[pid] = DEFAULT_BOT_NAMES[i] if i < len(DEFAULT_BOT_NAMES) else f"BOT {pid}"

        # Types
        self.player_types: Dict[str, str] = {pid: "ai" for pid in self.players}
        self.player_types["P1"] = "human"

        # Apply overrides
        if player_names:
            for k, v in player_names.items():
                if k in self.player_names:
                    self.player_names[k] = v
        if player_types:
            for k, v in player_types.items():
                if k in self.player_types:
                    self.player_types[k] = v

        # Deal & Dealer tracking (Dealer rotates clockwise each deal)
        self.deal_number: int = 1
        self.dealer_index: int = 0
        self.dealer: str = self.players[self.dealer_index]

        # Game state
        self.phase: str = "WAITING"
        self.hands: Dict[str, List[str]] = {p: [] for p in self.players}
        self.center_pot: List[str] = []  # all cards in the hidden discard pile
        self.safe_players: List[str] = []    # players who finished (safe / winners)
        self.eliminated: List[str] = []     # (same as safe - just alias for clarity)
        self.active_players: List[str] = []  # players still in game

        # Turn tracking
        self.current_turn_index: int = 0
        self.current_turn: Optional[str] = None

        # Current claim state
        self.last_claim: Optional[Dict[str, Any]] = None
        # last_claim = {claimant, claimed_rank, claimed_count, played_cards, is_bluff}
        self.current_round_rank: Optional[str] = None  # Option A: Active rank locked for the round sequence
        self.trick_leader: Optional[str] = None
        self.trick_lead: Optional[str] = None
        self.trick_plays_count: int = 0

        # Challenge tracking: who still needs to decide in challenge window
        self.challenge_order: List[str] = []  # remaining players to decide this claim
        self.challenge_decisions: Dict[str, str] = {}  # pid → "challenge" | "pass"

        # Logs
        self.logs: List[str] = []

        # Round summary (populated when ROUND_OVER)
        self.round_summary: Optional[Dict[str, Any]] = None
        self.last_resolution: Optional[Dict[str, Any]] = None

        # Start game immediately
        self._start_game()

    # ─── Setup ───────────────────────────────────────────────────────────────

    def _start_game(self):
        if self.num_players >= 6:
            deck = build_full_deck() + build_full_deck()
            random.shuffle(deck)
        else:
            deck = build_full_deck()
        self.active_players = list(self.players)
        self.safe_players = []
        self.center_pot = []
        self.hands = {p: [] for p in self.players}
        self.round_summary = None
        self.last_claim = None
        self.current_round_rank = None
        self.trick_lead = None
        self.trick_plays_count = 0
        self.last_resolution = None
        self.challenge_order = []
        self.challenge_decisions = {}

        # Deal all cards round-robin starting clockwise from the player next to the dealer
        deal_start_idx = (self.dealer_index + 1) % self.num_players
        for i, card in enumerate(deck):
            pid = self.players[(deal_start_idx + i) % self.num_players]
            self.hands[pid].append(card)

        # Player to the left of dealer (clockwise next) makes the first claim
        lead_player = self.players[(self.dealer_index + 1) % self.num_players]
        self.trick_leader = lead_player
        self.trick_lead = lead_player
        self.current_turn = lead_player
        self.current_turn_index = self.active_players.index(self.current_turn) if self.current_turn in self.active_players else 0
        self.phase = "PLAYING"
        self.logs = [
            f"Deal #{self.deal_number} started. Dealer: {self.player_names[self.dealer]} ({self.dealer}). "
            f"{self.player_names[self.current_turn]} ({self.current_turn}) leads first claim."
        ]

    def _next_active_turn(self):
        """Advance turn to next active player."""
        active = [p for p in self.players if p in self.active_players]
        if not active:
            return
        current_idx = active.index(self.current_turn) if self.current_turn in active else 0
        self.current_turn_index = (current_idx + 1) % len(active)
        self.current_turn = active[self.current_turn_index]

    # ─── Core Actions ─────────────────────────────────────────────────────────

    def play_cards(
        self,
        player_id: str,
        card_codes: List[str],
        claimed_rank: str,
        claimed_count: int
    ) -> Dict[str, Any]:
        """
        Active player places cards face-down and declares a claim.

        Args:
            player_id: The player making the claim.
            card_codes: List of 1–4 card codes from player's hand.
            claimed_rank: The rank being claimed (e.g. 'Q', '10', 'K').
            claimed_count: How many cards of that rank are claimed (must equal len(card_codes)).

        Returns:
            Result dict with success status and updated state.
        """
        if self.phase != "PLAYING":
            return {"success": False, "error": f"Not in PLAYING phase (current: {self.phase})"}
        if player_id != self.current_turn:
            return {"success": False, "error": f"Not {player_id}'s turn (current: {self.current_turn})"}

        hand = self.hands[player_id]
        # Validate cards are in hand
        for code in card_codes:
            if code not in hand:
                return {"success": False, "error": f"Card {code} not in {player_id}'s hand"}

        if len(card_codes) < 1 or len(card_codes) > 4:
            return {"success": False, "error": "Must play 1–4 cards"}

        if claimed_count != len(card_codes):
            return {"success": False, "error": "claimed_count must equal number of cards played"}

        if claimed_rank not in RANKS:
            return {"success": False, "error": f"Invalid rank: {claimed_rank}"}

        # Rank locking & Leader persistence:
        # Leader sets the rank and can change it when turn comes back around to them.
        # Followers must claim the active round rank.
        if self.current_round_rank is not None:
            if player_id == self.trick_leader:
                # Leader returns: can change card rank or keep it
                self.current_round_rank = claimed_rank
                self.trick_plays_count += 1
            else:
                if claimed_rank != self.current_round_rank:
                    locked_disp = RANK_DISPLAY.get(self.current_round_rank, self.current_round_rank)
                    return {
                        "success": False,
                        "error": f"Round rank is locked to {locked_disp}. You must claim {self.current_round_rank}."
                    }
                self.trick_plays_count += 1
        else:
            self.current_round_rank = claimed_rank
            self.trick_leader = player_id
            self.trick_lead = player_id
            self.trick_plays_count = 1

        # Check if it's a bluff
        is_bluff = any(code[:-1] != claimed_rank for code in card_codes)

        # Remove cards from hand (but don't reveal yet — add to pot)
        for code in card_codes:
            hand.remove(code)
        self.center_pot.extend(card_codes)

        self.last_claim = {
            "claimant": player_id,
            "claimed_rank": claimed_rank,
            "claimed_count": claimed_count,
            "played_cards": list(card_codes),  # hidden from others
            "is_bluff": is_bluff,
            "pot_before": len(self.center_pot) - len(card_codes),
        }

        rank_disp = RANK_DISPLAY.get(claimed_rank, claimed_rank)
        log_msg = (f"{self.player_names[player_id]} plays {claimed_count} × {rank_disp} "
                   f"[{len(hand)} cards left]. Pot: {len(self.center_pot)}")
        self.logs.append(log_msg)

        # Check if player just played their last cards
        if len(hand) == 0:
            self.last_claim["is_final_play"] = True
            self.logs.append(f"⚡ {self.player_names[player_id]} has played their last cards!")
        else:
            self.last_claim["is_final_play"] = False

        # Enter challenge window — ONLY the immediate next active player decides
        self.phase = "CHALLENGE_WINDOW"
        active = [p for p in self.players if p in self.active_players]
        claimant_idx = active.index(player_id) if player_id in active else 0
        next_player = active[(claimant_idx + 1) % len(active)]
        self.challenge_order = [next_player]
        self.challenge_decisions = {}

        return {"success": True, "state": self.to_dict("P1")}

    def make_decision(self, player_id: str, decision: str, card_index: int = 0) -> Dict[str, Any]:
        """
        Player in challenge window decides: "challenge" or "pass".

        Args:
            player_id: The deciding player.
            decision: "challenge" or "pass".
            card_index: 0-indexed position of the card to inspect (e.g. 0, 1, or 2 for 3 cards).

        Returns:
            Result dict. If a challenge occurs, includes resolution details.
        """
        if self.phase != "CHALLENGE_WINDOW":
            return {"success": False, "error": "Not in CHALLENGE_WINDOW phase"}
        if player_id not in self.challenge_order:
            return {"success": False, "error": f"{player_id} not in challenge order"}
        if player_id in self.challenge_decisions:
            return {"success": False, "error": f"{player_id} already decided"}

        self.challenge_decisions[player_id] = decision

        if decision == "challenge":
            result = self._resolve_challenge(player_id, card_index)
            return {"success": True, "resolved": True, "resolution": result, "state": self.to_dict("P1")}

        # Pass: only next player was deciding, so if they pass, everyone has passed!
        return self._all_passed()

    def _resolve_challenge(self, challenger_id: str, card_index: int = 0) -> Dict[str, Any]:
        """Resolves a challenge by inspecting a single chosen card position."""
        claim = self.last_claim
        claimant = claim["claimant"]
        played_cards = claim["played_cards"]
        claimed_rank = claim["claimed_rank"]

        # Clamp card_index to valid range [0, len(played_cards) - 1]
        card_index = max(0, min(card_index, len(played_cards) - 1))
        inspected_card = played_cards[card_index]
        inspected_rank = inspected_card[:-1]

        rank_disp = RANK_DISPLAY.get(claimed_rank, claimed_rank)
        inspected_disp = card_display(inspected_card)
        pot_size = len(self.center_pot)

        is_caught = (inspected_rank != claimed_rank)

        if is_caught:
            # Claimant was bluffing at the inspected position -> claimant takes entire pot
            self.hands[claimant].extend(self.center_pot)
            self.center_pot = []
            verdict = "CAUGHT_BLUFF"
            loser_of_challenge = claimant
            msg = (f"🚨 JHUTH! {self.player_names[challenger_id]} inspected Card #{card_index + 1} ({inspected_disp}): "
                   f"Caught bluff! It is not a {rank_disp}. {self.player_names[claimant]} picks up {pot_size} cards.")
            # Challenger succeeded in catching the bluff -> Challenger leads next
            new_leader = challenger_id
        else:
            # Claimant told the truth at the inspected position -> challenger failed to prove bluff
            self.hands[challenger_id].extend(self.center_pot)
            self.center_pot = []
            verdict = "CHALLENGE_FAILED"
            loser_of_challenge = challenger_id
            msg = (f"✅ Honest! {self.player_names[challenger_id]} inspected Card #{card_index + 1} ({inspected_disp}): "
                   f"It matches {rank_disp}! {self.player_names[challenger_id]} failed to prove bluff and picks up {pot_size} cards.")
            # Claimant was honest -> Claimant leads next
            new_leader = claimant

        self.logs.append(msg)

        if is_caught:
            if claim.get("is_final_play"):
                self.logs.append(f"💔 {self.player_names[claimant]} was caught on final play — still in game!")
        else:
            # Honest inspection: check if claimant successfully exited
            if claim.get("is_final_play") and len(self.hands[claimant]) == 0:
                self._mark_safe(claimant)

        self._check_round_over()

        if self.phase != "ROUND_OVER":
            active = [p for p in self.players if p in self.active_players]
            if new_leader not in active:
                # If new_leader exited, find next active player
                c_idx = self.players.index(new_leader) if new_leader in self.players else 0
                for step in range(1, len(self.players)):
                    cand = self.players[(c_idx + step) % len(self.players)]
                    if cand in active:
                        new_leader = cand
                        break
                else:
                    new_leader = active[0]

            self.trick_leader = new_leader
            self.trick_lead = new_leader
            self.current_turn = new_leader
            self.current_round_rank = None
            self.trick_plays_count = 0
            self.phase = "PLAYING"

        self.challenge_order = []
        self.challenge_decisions = {}
        self.last_claim = None

        res_dict = {
            "verdict": verdict,
            "inspected_index": card_index,
            "inspected_card": inspected_card,
            "inspected_card_display": inspected_disp,
            "revealed": [inspected_disp],
            "loser": loser_of_challenge,
            "loser_name": self.player_names.get(loser_of_challenge, loser_of_challenge),
            "pot_taken": pot_size,
            "message": msg,
        }
        self.last_resolution = res_dict
        return res_dict

    def _all_passed(self) -> Dict[str, Any]:
        """Next player passed on the claim. Cards stay in pot, that player takes their turn."""
        claim = self.last_claim
        claimant = claim["claimant"]
        next_player = self.challenge_order[0] if self.challenge_order else self.current_turn

        self.logs.append(f"✓ {self.player_names[next_player]} passed. Cards stay in pot ({len(self.center_pot)} total).")

        # Check if claimant successfully exited (played last cards, passed)
        if claim.get("is_final_play") and len(self.hands[claimant]) == 0:
            self._mark_safe(claimant)

        self._check_round_over()
        self.challenge_order = []
        self.challenge_decisions = {}
        self.last_claim = None

        if self.phase != "ROUND_OVER":
            active = [p for p in self.players if p in self.active_players]
            if next_player in active:
                self.current_turn = next_player
            else:
                self._next_active_turn()
            self.phase = "PLAYING"

        return {"success": True, "resolved": True, "resolution": {"verdict": "ALL_PASSED"}, "state": self.to_dict("P1")}

    def _mark_safe(self, player_id: str):
        """Marks a player as SAFE (they exited the game as a winner)."""
        if player_id in self.active_players:
            self.active_players.remove(player_id)
            self.safe_players.append(player_id)
            rank = len(self.safe_players)
            self.logs.append(f"🏆 {self.player_names[player_id]} is SAFE! (Place #{rank})")

    def _check_safe_players(self):
        """Check if any player has 0 cards and should be marked safe (used during mid-game)."""
        # Only mark safe if they played their last cards AND survived challenge
        # This is handled explicitly in resolve and all_passed
        pass

    def _check_round_over(self):
        """Check if only one player remains — they are the Loser."""
        remaining = [p for p in self.active_players]
        if len(remaining) <= 1:
            loser = remaining[0] if remaining else None
            self.phase = "ROUND_OVER"

            safe_rankings = []
            for i, pid in enumerate(self.safe_players, 1):
                safe_rankings.append({
                    "place": i,
                    "player_id": pid,
                    "name": self.player_names[pid],
                    "status": "SAFE"
                })

            self.round_summary = {
                "loser": loser,
                "loser_name": self.player_names[loser] if loser else None,
                "loser_cards": len(self.hands[loser]) if loser else 0,
                "rankings": safe_rankings,
                "pot_remaining": len(self.center_pot),
            }
            if loser:
                self.logs.append(
                    f"🎯 GAME OVER! {self.player_names[loser]} is the LOSER (Jhuthaniya) "
                    f"with {len(self.hands[loser])} cards!"
                )

    # ─── Bot Step ─────────────────────────────────────────────────────────────

    def step_bot(self) -> Dict[str, Any]:
        """
        Executes one bot action (either play cards or make a challenge/pass decision).

        Returns:
            Dict describing what the bot did.
        """
        if self.phase == "ROUND_OVER":
            return {"action": "none", "reason": "Round over"}

        if self.phase == "PLAYING":
            pid = self.current_turn
            if self.player_types.get(pid) != "ai":
                return {"action": "none", "reason": f"{pid} is human — waiting for input"}

            # Bot makes a play
            hand = self.hands[pid]
            if not hand:
                # Shouldn't happen but just in case
                self._mark_safe(pid)
                return {"action": "auto_safe", "player": pid}

            claimed_rank, claimed_count = bot_choose_claim_rank(hand, required_rank=self.current_round_rank)
            count_to_play = min(claimed_count, len(hand), 3)
            play_cards, is_bluff = bot_select_cards_to_play(hand, claimed_rank, count_to_play, len(self.center_pot))

            result = self.play_cards(pid, play_cards, claimed_rank, count_to_play)
            return {
                "action": "play",
                "player": pid,
                "claimed_rank": claimed_rank,
                "claimed_count": count_to_play,
                "is_bluff": is_bluff,
                "result": result,
            }

        elif self.phase == "CHALLENGE_WINDOW":
            # The next player is in self.challenge_order[0]
            if not self.challenge_order:
                return {"action": "none", "reason": "No player in challenge order"}
            pid = self.challenge_order[0]
            if pid in self.challenge_decisions:
                return {"action": "none", "reason": f"{pid} already decided"}
            if self.player_types.get(pid) != "ai":
                return {"action": "none", "reason": f"{pid} is human — waiting for challenge decision"}

            # Bot decides
            claim = self.last_claim
            decision_result = bot_should_challenge(
                my_hand=self.hands[pid],
                claimed_rank=claim["claimed_rank"],
                claimed_count=claim["claimed_count"],
                cards_in_pot=len(self.center_pot),
                claimant_hand_size=len(self.hands[claim["claimant"]]),
                players_remaining=len(self.active_players),
            )
            decision = "challenge" if decision_result else "pass"
            card_index = bot_choose_inspect_index(claim["claimed_count"]) if decision == "challenge" else 0
            self.logs.append(
                f"🤖 {self.player_names[pid]}: {decision.upper()}"
                + (f" on Card #{card_index + 1}" if decision == "challenge" else "")
                + f" for {claim['claimed_count']} × {claim['claimed_rank']}"
            )
            result = self.make_decision(pid, decision, card_index)
            return {
                "action": f"challenge_decision_{decision}",
                "player": pid,
                "decision": decision,
                "card_index": card_index,
                "result": result,
            }

        return {"action": "none", "reason": f"Unknown phase: {self.phase}"}

    def new_game(self):
        """Rotates dealer clockwise and starts a new deal with the same players."""
        self.dealer_index = (self.dealer_index + 1) % self.num_players
        self.dealer = self.players[self.dealer_index]
        self.deal_number += 1
        self._start_game()

    # ─── State Serialization ──────────────────────────────────────────────────

    def to_dict(self, perspective_player: str = "P1") -> Dict[str, Any]:
        """
        Returns the full game state for the given perspective player.
        Hides: other players' card values (only counts visible), pot cards (face-down).
        """
        is_challenge_window = self.phase == "CHALLENGE_WINDOW"
        claim = self.last_claim

        # Build per-player info
        players_info = {}
        for pid in self.players:
            is_me = (pid == perspective_player)
            players_info[pid] = {
                "name": self.player_names[pid],
                "type": self.player_types[pid],
                "card_count": len(self.hands[pid]),
                "hand": self.hands[pid] if is_me else [],  # Only self can see own cards
                "is_active": pid in self.active_players,
                "is_safe": pid in self.safe_players,
                "safe_rank": (self.safe_players.index(pid) + 1) if pid in self.safe_players else None,
                "is_dealer": (pid == self.dealer),
            }

        # Challenge state
        challenge_info = None
        if is_challenge_window and claim:
            challenge_info = {
                "claimant": claim["claimant"],
                "claimant_name": self.player_names[claim["claimant"]],
                "claimed_rank": claim["claimed_rank"],
                "claimed_count": claim["claimed_count"],
                "played_cards_count": len(claim["played_cards"]),
                "rank_display": RANK_DISPLAY.get(claim["claimed_rank"], claim["claimed_rank"]),
                "is_final_play": claim.get("is_final_play", False),
                "challenge_order": self.challenge_order,
                "challenge_decisions": {
                    k: v for k, v in self.challenge_decisions.items()
                },
                "my_decision": self.challenge_decisions.get(perspective_player),
                "waiting_for": [p for p in self.challenge_order if p not in self.challenge_decisions],
            }

        return {
            "game_id": self.game_id,
            "phase": self.phase,
            "deal_number": self.deal_number,
            "dealer": self.dealer,
            "dealer_id": self.dealer,
            "dealer_name": self.player_names.get(self.dealer, self.dealer),
            "num_players": self.num_players,
            "players": players_info,
            "active_players": list(self.active_players),
            "safe_players": list(self.safe_players),
            "center_pot_size": len(self.center_pot),
            "current_turn": self.current_turn,
            "current_turn_name": self.player_names.get(self.current_turn, "") if self.current_turn else "",
            "is_my_turn": (self.current_turn == perspective_player and self.phase == "PLAYING"),
            "my_hand": self.hands.get(perspective_player, []),
            "challenge": challenge_info,
            "last_resolution": self.last_resolution,
            "round_summary": self.round_summary,
            "logs": self.logs[-30:],  # Last 30 log entries
            "perspective_player": perspective_player,
            "current_round_rank": self.current_round_rank,
            "current_round_rank_display": RANK_DISPLAY.get(self.current_round_rank, self.current_round_rank) if self.current_round_rank else None,
            "can_choose_rank": (self.current_round_rank is None or self.current_turn == self.trick_leader),
            "trick_leader": self.trick_leader,
            "trick_lead": self.trick_leader,
            "trick_plays_count": self.trick_plays_count,
            "ranks": RANKS,
            "rank_display": RANK_DISPLAY,
        }
