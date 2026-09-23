# Mindikot / Bindikot (Bandh Hukum) — Dev Prompt

Build a complete, playable, modular digital card game for **"Mindikot / Bindikot with Bandh Hukum (Closed Trump)"** in Python (FastAPI backend + vanilla JS frontend).

## 1. Domain Specification & Rules

**Players**: Exactly 4 in 2 fixed partnerships:
- Team 1: P1 (Human - South) & P3 (Bot - North)
- Team 2: P2 (Bot - East) & P4 (Bot - West)

**Deck**: Standard 52-card deck (A > K > Q > J > 10 > ... > 2).

**The Four Mindis**: ♠10, ♥10, ♦10, ♣10.

**Dealing & Bandh Hukum Phase**:
- Deal first 5 cards to each player.
- Trump Placer (player next to dealer) chooses 1 card from their 5 cards and places it **FACE-DOWN** in the center table as the hidden trump.
- Deal remaining 8 cards to each player (total 13 cards each).

**Trump Reveal Trigger (Bandh Hukum)**:
- Trump remains hidden and UNKNOWN to all other players.
- Trick-taking begins with the trump placer leading Trick 1.
- Follow-suit rule is strictly enforced.
- When ANY player is void in the led suit → the hidden card is automatically revealed ("Hukum Kholo!").
- That suit becomes the active TRUMP suit.
- The void player must cut with a trump if available, or discard any card.

**Winner of Trick**:
- If trump is revealed: Highest trump wins; otherwise highest card of led suit.
- Before trump is revealed: Highest card of led suit wins.
- Winning player leads next trick.

**Scoring & Victory**:
- Count Mindis won by each team.
- Team with 4 Mindis wins. Team with 3 Mindis wins.
- If 2-2 tie: Team with >= 7 tricks wins.
- KOT: 4 Mindis + >= 7 tricks.
- White-Wash: 4 Mindis + all 13 tricks (Super KOT).

## 2. Architectural & Code Requirements

**Data Models**:
- `Card`: Suit (H/S/D/C), Rank (2..14), isMindi boolean (rank==10).
- `Deck`: Standard 52-card deck with Fisher-Yates shuffle.
- `GameState`: Enum [DEALING_5, BANDH_HUKUM_SELECTION, DEALING_REST, PLAYING_TRICK, TRUMP_REVEALED, TRICK_RESOLVED, ROUND_SUMMARY].
- `Partnership`: Tracks Mindis captured, tricks won, match points.

**Move Validation**:
- `get_legal_moves(hand, led_suit, trump_revealed, trump_suit)`:
  - If leading: any card valid.
  - If following with led_suit cards: MUST play led_suit.
  - If void in led_suit: triggers trump reveal; can play any card.

**Heuristic AI Agents (3 Bot players)**:
- Trump Selection: From first 5 cards, choose suit with highest count + strong honors.
- Card Play:
  - Partner winning trick → throw Mindi to score points.
  - Opponent winning → avoid dropping Mindis, play lowest legal.
  - Void in led suit (trump revealed) → cut with lowest winning trump; if trick contains Mindi, use secure trump.
  - Leading → play high cards (Aces) of non-trump suits; or lead low to let partner win.

**API Endpoints**:
- `POST /api/bindi-coat/create-room`
- `GET /api/bindi-coat/state`
- `POST /api/bindi-coat/select-bandh-hukum`
- `POST /api/bindi-coat/play`
- `POST /api/bindi-coat/bot-step`
- `POST /api/bindi-coat/next-round`

## 3. User Interface
- Clear visual distinction between 4 players at table.
- Center area: current trick cards + Bandh Hukum card (face-down card back until revealed, then flips).
- HUD: Mindis captured by each team, Tricks won tally.
- "HUKUM KHOLO!" banner notification on trump reveal.
- Playable cards highlighted; illegal cards disabled.
