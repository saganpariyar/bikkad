# Jhuthaniya — LLM & Game Developer Prompt

Build a robust, modular, turn-based multiplayer card game engine in Python 3.10+ for the traditional Indian card game **"Jhuthaniya"** (also known as Bluff / Cheat / I Doubt It).

## 1. Core Game Mechanics
- Support **2 to 7 players** (human player vs. configurable AI bots).
- Standard 52-card deck (suits: Hearts, Diamonds, Clubs, Spades; ranks: 2–10, J, Q, K, A).
- Deal cards evenly among all active players.
- Maintain **private hands** for all players and a central **hidden discard pile** (`center_pot`).

## 2. Turn Protocol & Actions
- Active player selects **1 to 4 cards** from their hand to place face-down into `center_pot`.
- Active player declares a claim: `(claimed_count: int, claimed_rank: str)` (e.g., 3 "Q").
- **Challenge Phase**: Clockwise rotation allows other players to either call "JHUTH" (Challenge) or "PASS".
  - If challenged: Reveal the played cards.
    - If ANY card does NOT match claimed rank → **BLUFF DETECTED**: Claimant picks up all `center_pot` cards.
    - If ALL cards match claimed rank → **TRUTH PROVEN**: Challenger picks up all `center_pot` cards.
  - If all players pass: Cards remain face-down in `center_pot`. Turn moves to next player.

## 3. Win & Elimination Logic
- When a player places their last card, they must survive the Challenge Phase.
- If challenged and bluffing: They take the pot and remain in the game.
- If unchallenged or truthful: Marked 'SAFE' (exited) and removed from turn order.
- Game continues until exactly **ONE** player remains with cards. That player is declared the **'LOSER' (Jhuthaniya)**.

## 4. AI Bot Heuristics
- **Honest Preference**: If bot holds cards of the claimed rank, play them truthfully.
- **Bluff Generator**: If bot lacks the rank, pick lowest/useless cards to bluff with.
- **Challenge Evaluator** (Card Counting & Probability):
  - Calculate impossibility: If Bot holds X cards of Rank R, and opponent claims Y cards of Rank R, where X + Y > 4 → Challenge Probability = 100%.
  - Risk tolerance: If `center_pot` has > 10 cards, challenge only on high certainty. If pot < 3 cards, challenge more aggressively.
  - Endgame suspicion: Increase challenge rate by 70% if an opponent claims to play their final cards.

## 5. Deliverables
- Clean, object-oriented design (`Card`, `Deck`, `Player`, `AIBot`, `JhuthaniyaGame`).
- REST API with FastAPI endpoints: `create-room`, `state`, `play`, `challenge`, `bot-step`.
- Frontend UI showing: player card counts, pot size, turn history, challenge verdict.
- Unit tests covering: honest verification, caught bluffs, win-state transitions, last-card exit edge cases.
