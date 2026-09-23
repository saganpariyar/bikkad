# Desi Card Games Hub (Apna Rajasthan & Indian Traditional Card Games)

A full-stack, responsive card game web application and multi-game ecosystem for traditional Indian and Rajasthani card games, built with Python FastAPI, modular game engines, and a rich casino-grade Web UI with royal playing cards.

---

## 🃏 Games Collection

- **1. Bikkad (Live Now)**: Bandh Rang Double Sir / Tug-of-War partnership pot sweep game with hidden trump, 52-point dealer ladder burden, and solo Tera contracts.
- **2. Jhuthaniya (Coming Soon)**: Bluff & deception card game.
- **3. Gadha Baji (Coming Soon)**: Donkey card elimination and shedding.
- **4. Sarkari (Coming Soon)**: Rule-bound trump clash.
- **5. Bindi Coat (Coming Soon)**: Point coat and 10s sweeps.
- **6. Tikdi (Coming Soon)**: Tri-card Rajasthani arena.

---

## 📁 Multi-Game Prompts, Logs & Rules Architecture

All game rules, prompts, and play logs are modularized in the [`games/`](file:///d:/Projects/sagan/Bikkad/games/) directory:

```text
games/
├── README.md               # Guide for adding new games & prompts
├── _template/              # Ready template for new card games
├── bikkad/                 # Prompts, play logs & official rules for Bikkad
├── jhuthaniya/             # Specifications & logs for Jhuthaniya
├── gadha_baji/             # Specifications & logs for Gadha Baji
├── sarkari/                # Specifications & logs for Sarkari
├── bindi_coat/             # Specifications & logs for Bindi Coat
└── tikdi/                  # Specifications & logs for Tikdi
```

---

## 🎮 Bikkad Features (Live Game)

- **Exact Rules Implementation**: Full compliance with the official rulebook in [`games/bikkad/rules/rules.txt`](file:///d:/Projects/sagan/Bikkad/games/bikkad/rules/rules.txt) and 52-game master ledger in [`games/bikkad/play_logs/`](file:///d:/Projects/sagan/Bikkad/games/bikkad/play_logs/).
- **Double Sir Pot Accumulation**: 2 consecutive wins scoop the accumulated center pot; 13th trick sweep for remaining pot cards.
- **Contract Modes**:
  - **Regular Mode**: Eldest hand sets hidden trump (*Bandh Hukum*).
  - **Tera Mode**: 2 vs 2 sweep challenge (13-0).
  - **Double Tera Mode**: 1 vs 2 solo challenge (declarer partner sits out).
- **Tug-of-War Debt Scoreboard**: Track dealer debt with 52-point cap out rollover and $\le 0$ free handover to opponents.
- **Classic Royal Vector Cards**: Traditional English pattern vector deck with royal reversible Jack, Queen, and King court art.
- **Flexible Player Lobby**: Simple 4-digit room code with seat allocation for 1, 2, 3, or 4 human players and smart bots.

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Application (Automated Tests + Server + Web UI)
```bash
python run.py
```
This script automatically:
1. Runs the `pytest` test suite.
2. Starts the FastAPI server on `http://127.0.0.1:8000`.
3. Opens the web app in your default browser.

---

## 🤖 Ollama AI Setup (Optional)

To enable local LLM AI players:
1. Install and launch [Ollama](https://ollama.ai).
2. Pull your preferred model:
   ```bash
   ollama run llama3
   ```
3. Open the **⚙ Lobby** in the web app and check **Enable Local Ollama AI**.

---

## 📱 Future Android App Conversion

The application has been designed with future Android deployment in mind:
- **Responsive Layout**: Designed with fluid viewports suitable for smartphone screens.
- **PWA Ready**: Native HTML5 Web Standards (Web Audio API sound effects, SVG card renderer, zero heavy web frameworks).
- **Packaging Options**:
  - **Capacitor / Cordova**: Wrap the `frontend/` directory into a native Android APK.
  - **Android WebView App**: Load `http://<server-ip>:8000` or local assets inside an Android WebView activity.
