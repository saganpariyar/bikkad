# Desi Card Games Collection & Engine Workspace

Welcome to the **Desi Card Games** repository. This directory (`games/`) is organized so that every traditional Indian and Rajasthani card game has a dedicated, structured space for its rules, AI prompts, match play logs, and design notes.

---

## 📁 Directory Structure

```text
games/
├── README.md                  # This master guide
├── _template/                 # Blank template for adding any new game
│   ├── prompts/               # Add your AI specification prompts here
│   ├── play_logs/             # Add real/simulated play logs, match transcripts
│   └── rules/                 # Add rulebooks, scoring tables, card ranking
├── bikkad/                    # 🟢 LIVE NOW: Apna Rajasthan Ka Bikkad
│   ├── prompts/               # prompt.txt, prompt1.txt
│   ├── play_logs/             # play_logs.txt, play_logs2.txt, play_logs3.txt
│   ├── rules/                 # rules.txt
│   └── README.md              # Bikkad specifications & architecture
├── jhuthaniya/                # 🔒 COMING SOON: Bluff & Deception
├── gadha_baji/                # 🔒 COMING SOON: Donkey Card Elimination
├── sarkari/                   # 🔒 COMING SOON: Rule-Bound Trump Clash
├── bindi_coat/                # 🔒 COMING SOON: Point Coat & Sweeps (Mindi)
└── tikdi/                     # 🔒 COMING SOON: Tri-Card Rajasthani Arena
```

---

## 🚀 How to Add a New Game or Update Existing Ones

Whenever you want to build or specify a new card game:
1. **Create/Use the Game Directory**: E.g. `games/jhuthaniya/` (or copy `games/_template/`).
2. **Add Prompts (`prompts/`)**:
   - Save your requirement prompts (e.g. `prompt.txt`, `prompt_v2.txt`).
   - Include player count, deal phases, bidding rules, and bot behaviors.
3. **Add Play Logs (`play_logs/`)**:
   - Paste sample play logs, game transcripts, or edge-case test runs.
   - These are directly used to validate state transitions, legal card rules, and winner evaluation.
4. **Add Rules & Texts (`rules/`)**:
   - Put detailed rules, card hierarchy, scoring formulas, and penalty structures in `rules.txt`.

Our coding agent will read these folders directly to implement the engine, bots, and UI!
