# Bikkad (Apna Rajasthan Ka Bikkad)

- **Status**: 🟢 **Live Now**
- **Type**: 4-Player Partnership Trick-Taking & Pot Sweep Game
- **Players**: 4 players (Team A: P1 + P3 vs Team B: P2 + P4)

---

## Folder Contents

- **`prompts/`**:
  - `prompt.txt`: Primary system prompt defining the engine rules, WebSocket protocol, and simulation parameters.
  - `prompt1.txt`: Extended specifications for bot strategy, bidding dynamics, and UI interactions.
- **`play_logs/`**:
  - `play_logs.txt`: Reference match logs for validating scoring and trick rules.
  - `play_logs2.txt`: 52-game master ledger verifying Tug-of-War dealer ladder burden progression.
  - `play_logs3.txt`: Edge-case deal transcripts covering Tera, Double Tera, and void trump cuts.
- **`rules/`**:
  - `rules.txt`: Complete rulebook covering dealing, hidden trump, sweep rules, and ladder scoring.

---

## Core Game Mechanics

1. **Dealing & Hidden Trump**:
   - Dealer deals 5 cards each. The Trump Hider places 1 card face-down as the Hidden Trump.
   - Remaining cards are dealt in batches (5 + 3) for a total of 13 cards per player.
2. **Double Trick Sweep**:
   - Tricks accumulate in the center pot.
   - To sweep the pot, a single team must win 2 consecutive tricks in a streak.
3. **Hidden Trump Reveal**:
   - Revealed only when a player is unable to follow the led suit (void) and requests the trump cut.
4. **Tera & Double Tera**:
   - Contract to win all 13 tricks solo with dynamic runtime trump declared on first void.
5. **Tug-of-War Dealer Ladder**:
   - Dealer burden scores up to 52 points.
