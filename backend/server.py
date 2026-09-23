import os
import random
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.engine.game_session import GameSession
from backend.engine.tikdi.tikdi_session import TikdiSession
from backend.engine.jhuthaniya.jhuthaniya_session import JhuthaniyaSession
from backend.engine.bindi_coat.bindi_coat_session import BindiCoatSession
from backend.engine.room_manager import room_manager
from backend.ai.ollama_client import get_ai_move
from backend.ai.heuristic_fallback import evaluate_bidding_heuristic, select_runtime_trump_heuristic
from backend.engine.card import Card

app = FastAPI(title="Bikkad & Desi Card Games API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_no_cache_header(request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.get("/api/health")
@app.get("/health")
def health_check():
    """Lightweight ping endpoint for Render cold-start detection and keepalives."""
    return {
        "status": "ok",
        "service": "Bikkad & Desi Card Games API",
        "version": "2.0.0",
        "active_sessions": {
            "bikkad": len(sessions),
            "tikdi": len(tikdi_sessions),
            "jhuthaniya": len(jhuthaniya_sessions),
            "bindi_coat": len(bindi_coat_sessions)
        }
    }


# Multi-Game Sessions Store (Bikkad)
sessions: Dict[str, GameSession] = {}
default_game_id: str = "game1"

# Initialize default Bikkad session
default_sess = GameSession(initial_dealer='P1', initial_score=0)
default_sess.game_id = default_game_id
default_sess.start_new_round(mode="Regular")
sessions[default_game_id] = default_sess

# Multi-Game Sessions Store (Tikdi 3-Player)
tikdi_sessions: Dict[str, TikdiSession] = {}

def get_tikdi_session(game_id: Optional[str] = None) -> TikdiSession:
    gid = (game_id or "tikdi1").strip()
    if gid in tikdi_sessions:
        return tikdi_sessions[gid]
    for key, s in tikdi_sessions.items():
        if key.upper() == gid.upper():
            return s
    sess = TikdiSession(game_id=gid)
    tikdi_sessions[gid] = sess
    return sess


# Multi-Game Sessions Store (Jhuthaniya)
jhuthaniya_sessions: Dict[str, JhuthaniyaSession] = {}

def get_jhuthaniya_session(game_id: Optional[str] = None) -> JhuthaniyaSession:
    gid = (game_id or "jhuth1").strip()
    if gid in jhuthaniya_sessions:
        return jhuthaniya_sessions[gid]
    sess = JhuthaniyaSession(game_id=gid)
    jhuthaniya_sessions[gid] = sess
    return sess


# Multi-Game Sessions Store (Bindi Coat / Mindikot)
bindi_coat_sessions: Dict[str, BindiCoatSession] = {}

def get_bindi_coat_session(game_id: Optional[str] = None) -> BindiCoatSession:
    gid = (game_id or "bc1").strip()
    if gid in bindi_coat_sessions:
        return bindi_coat_sessions[gid]
    sess = BindiCoatSession(game_id=gid)
    bindi_coat_sessions[gid] = sess
    return sess


def get_session(game_id: Optional[str] = None) -> GameSession:
    """Retrieves or creates GameSession by game_id."""
    gid = (game_id or default_game_id).strip()
    sess = None
    if gid in sessions:
        sess = sessions[gid]
    else:
        # Check case-insensitive
        for key, s in sessions.items():
            if key.upper() == gid.upper():
                sess = s
                break
    if sess is None:
        # Create new session if not found
        new_sess = GameSession(initial_dealer='P1', initial_score=0)
        new_sess.game_id = gid
        new_sess.start_new_round(mode="Regular")
        sessions[gid] = new_sess
        sess = new_sess

    # Safeguard: Ensure any player slot designated as BOT has player_type 'ai'
    for p, name in sess.player_names.items():
        if name and (name.startswith("BOT ") or name.startswith("COM ")) and sess.player_types.get(p) != 'ai':
            sess.player_types[p] = 'ai'

    return sess


# ==================== REQUEST SCHEMAS ====================

class CreateRoomRequest(BaseModel):
    host_name: str = "Sagan"
    game_name: str = "game1"
    setup_mode: str = "1-3 com"  # "1-3 com", "2-2 com", "3-1 com", "4-0 com"
    trump_hider: Optional[str] = "P1"  # "P1", "P2", "P3", "P4", "random"
    first_deal_role: Optional[str] = None  # backward-compatible alias
    game_id: Optional[str] = None
    seats_config: Optional[Dict[str, str]] = None
    seat_names: Optional[Dict[str, str]] = None


class JoinRoomRequest(BaseModel):
    game_id: str
    player_name: str


class AssignSeatRequest(BaseModel):
    game_id: str
    seat_id: str  # "P2", "P3", "P4"
    player_name: str
    player_type: str = "ai"  # "human" or "ai"


class StartRoomRequest(BaseModel):
    game_id: str
    trump_hider: Optional[str] = None


class DeclareRequest(BaseModel):
    player_id: str
    contract: str  # "Regular", "Tera", "Double Tera"
    game_id: Optional[str] = None


class SelectTrumpRequest(BaseModel):
    card_code: str
    game_id: Optional[str] = None


class OpenTrumpRequest(BaseModel):
    player_id: str
    game_id: Optional[str] = None


class RuntimeTrumpRequest(BaseModel):
    suit: str  # "S", "H", "D", "C"
    game_id: Optional[str] = None


class AskTrumpRequest(BaseModel):
    player_id: str
    game_id: Optional[str] = None


class PlayRequest(BaseModel):
    player_id: str
    card_code: str
    demand_cut: bool = False
    game_id: Optional[str] = None


class ConfigRequest(BaseModel):
    player_types: Dict[str, str]
    use_ollama: bool = False
    ollama_model: str = "llama3"
    game_id: Optional[str] = None


class NewGameRequest(BaseModel):
    game_name: str = "game1"
    game_id: Optional[str] = None
    trump_hider: Optional[str] = "P1"
    player_names: Optional[Dict[str, str]] = None
    player_types: Optional[Dict[str, str]] = None


# Tikdi (3-Player) Request Schemas
class CreateTikdiRoomRequest(BaseModel):
    host_name: str = "Sagan"
    game_id: Optional[str] = None
    game_name: Optional[str] = None
    seats_config: Optional[Dict[str, str]] = None
    seat_names: Optional[Dict[str, str]] = None
    player_types: Optional[Dict[str, str]] = None
    player_names: Optional[Dict[str, str]] = None
    trump_chooser: Optional[str] = None
    penalty_mode: Optional[str] = "choice"


class TikdiTrumpRequest(BaseModel):
    game_id: str = "tikdi1"
    seat: Optional[str] = None
    player_id: Optional[str] = None
    trump_suit: Optional[str] = None
    suit: Optional[str] = None


class TikdiPullCardRequest(BaseModel):
    game_id: str = "tikdi1"
    seat: Optional[str] = None
    puller_id: Optional[str] = None
    card_index: Optional[int] = None


class TikdiReturnCardRequest(BaseModel):
    game_id: str = "tikdi1"
    seat: Optional[str] = None
    returner_id: Optional[str] = None
    card_code: str
    target_id: Optional[str] = None


class TikdiPlayCardRequest(BaseModel):
    game_id: str = "tikdi1"
    seat: Optional[str] = None
    player_id: Optional[str] = None
    card_code: str


class TikdiBotStepRequest(BaseModel):
    game_id: str = "tikdi1"


class TikdiNextRoundRequest(BaseModel):
    game_id: str = "tikdi1"


class TikdiSwitchPenaltyModeRequest(BaseModel):
    game_id: str = "tikdi1"
    penalty_mode: str = "quota_adjustment"
    player_id: Optional[str] = "P1"


class TikdiMakeDebtChoiceRequest(BaseModel):
    game_id: str = "tikdi1"
    debtor_id: Optional[str] = None
    player_id: Optional[str] = "P1"
    seat: Optional[str] = None
    choice: str = "card_swap"  # "card_swap" or "quota_adjustment"


class TikdiAcknowledgeAdjustmentRequest(BaseModel):
    game_id: str = "tikdi1"
    player_id: Optional[str] = "P1"


# Jhuthaniya Request Schemas
class CreateJhuthaniyaRoomRequest(BaseModel):
    host_name: str = "Player"
    game_id: Optional[str] = None
    num_players: int = 4
    player_names: Optional[Dict[str, str]] = None
    player_types: Optional[Dict[str, str]] = None


class JhuthaniyaPlayRequest(BaseModel):
    game_id: str = "jhuth1"
    player_id: str = "P1"
    card_codes: List[str]
    claimed_rank: str
    claimed_count: int


class JhuthaniyaDecisionRequest(BaseModel):
    game_id: str = "jhuth1"
    player_id: str
    decision: str  # "challenge" or "pass"
    card_index: Optional[int] = 0  # 0-indexed position of card to inspect


class JhuthaniyaBotStepRequest(BaseModel):
    game_id: str = "jhuth1"


class JhuthaniyaNewGameRequest(BaseModel):
    game_id: str = "jhuth1"


# Bindi Coat Request Schemas
class CreateBindiCoatRoomRequest(BaseModel):
    host_name: str = "Player"
    game_id: Optional[str] = None
    player_names: Optional[Dict[str, str]] = None
    player_types: Optional[Dict[str, str]] = None


class BindiCoatSelectBandhHukumRequest(BaseModel):
    game_id: str = "bc1"
    player_id: str = "P1"
    card_code: Optional[str] = None
    card_index: Optional[int] = None


class BindiCoatPlayRequest(BaseModel):
    game_id: str = "bc1"
    player_id: str = "P1"
    card_code: str


class BindiCoatBotStepRequest(BaseModel):
    game_id: str = "bc1"


class BindiCoatNextRoundRequest(BaseModel):
    game_id: str = "bc1"


# ==================== ROOM & LOBBY ENDPOINTS ====================

@app.post("/api/room/create")
def create_room(req: CreateRoomRequest):
    """Creates a new game room with a unique ID, setup mode, and trump hider selection."""
    hider_choice = req.trump_hider or req.first_deal_role or "P1"
    room = room_manager.create_room(
        host_name=req.host_name,
        game_name=req.game_name,
        setup_mode=req.setup_mode,
        first_deal_role=hider_choice,
        game_id=req.game_id,
        seats_config=req.seats_config,
        seat_names=req.seat_names
    )
    game_id = room['game_id']

    # Resolve initial dealer so that the chosen player hides trump and leads
    initial_dealer = room_manager.resolve_initial_dealer(hider_choice)

    # Initialize backend GameSession for this room
    sess = GameSession(initial_dealer=initial_dealer, initial_score=0)
    sess.game_id = game_id
    sess.game_name = req.game_name

    # Apply seat names and types
    sess.player_names = {s_id: s_info['name'] for s_id, s_info in room['seats'].items()}
    sess.player_types = {s_id: s_info['type'] for s_id, s_info in room['seats'].items()}
    sess.logger.start_game(sess.game_name, sess.player_names, sess.player_teams, sess.player_types)

    sessions[game_id] = sess
    return {'room': room, 'game_id': game_id, 'seat_id': 'P1'}


@app.post("/api/room/join")
def join_room(req: JoinRoomRequest):
    """Joins an existing room using unique Game ID."""
    try:
        res = room_manager.join_room(req.game_id, req.player_name)
        game_id = res['game_id']
        sess = get_session(game_id)

        # Update player name in session if assigned to a seat
        if res.get('seat_id'):
            sess.player_names[res['seat_id']] = req.player_name
            sess.player_types[res['seat_id']] = "human"
            res['player_name'] = req.player_name

        return res
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/api/room/assign_seat")
def assign_seat(req: AssignSeatRequest):
    """Host assigns player (human friend or COM bot) to P2, P3, or P4."""
    try:
        room = room_manager.assign_seat(
            game_id=req.game_id,
            seat_id=req.seat_id,
            player_name=req.player_name,
            player_type=req.player_type
        )
        sess = get_session(req.game_id)
        sess.player_names[req.seat_id] = req.player_name
        sess.player_types[req.seat_id] = req.player_type
        return {'success': True, 'room': room}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/room/status")
def room_status(game_id: str = Query(...)):
    """Returns the room's current lobby or game state."""
    room = room_manager.get_room(game_id)
    if not room:
        raise HTTPException(status_code=404, detail=f"Room '{game_id}' not found.")
    sess = get_session(game_id)
    return {
        'room': room,
        'game_state': sess.get_state() if room['status'] == 'playing' else None
    }


@app.post("/api/room/start")
def start_room(req: StartRoomRequest):
    """Launches table play for the room."""
    try:
        room = room_manager.start_room(req.game_id)
        sess = get_session(req.game_id)

        # Ensure dealer corresponds to chosen trump hider
        hider_choice = req.trump_hider or room.get('first_deal_role') or "P1"
        initial_dealer = room_manager.resolve_initial_dealer(hider_choice)
        sess.ladder_manager.dealer_id = initial_dealer

        # Finalize names and types from seats
        sess.player_names = {s_id: s_info['name'] for s_id, s_info in room['seats'].items()}
        sess.player_types = {s_id: s_info['type'] for s_id, s_info in room['seats'].items()}
        sess.logger.start_game(sess.game_name, sess.player_names, sess.player_teams, sess.player_types)
        state = sess.start_new_round(mode="Regular")

        return {'room': room, 'state': state}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== CORE GAMEPLAY ENDPOINTS ====================

@app.get("/api/state")
def get_state(game_id: Optional[str] = None):
    sess = get_session(game_id)
    return sess.get_state()


@app.post("/api/new_game")
def new_game(req: NewGameRequest):
    """Resets score and initializes a brand new match with custom game name, players, and trump hider."""
    gid = req.game_id or req.game_name or default_game_id
    initial_dealer = room_manager.resolve_initial_dealer(req.trump_hider or "P1")
    sess = GameSession(initial_dealer=initial_dealer, initial_score=0)
    sess.game_id = gid
    sess.game_name = req.game_name.strip() if req.game_name else "game1"

    if req.player_names:
        sess.player_names.update(req.player_names)
    if req.player_types:
        sess.player_types.update(req.player_types)

    sess.logger.start_game(sess.game_name, sess.player_names, sess.player_teams, sess.player_types)
    state = sess.start_new_round(mode="Regular")
    sessions[gid] = sess
    return state


@app.post("/api/next_deal")
def next_deal(game_id: Optional[str] = None):
    """Continues match with next deal while preserving dealer score and rotation."""
    sess = get_session(game_id)
    state = sess.start_new_round(mode="Regular")
    return state


@app.post("/api/restart_deal")
def restart_deal(game_id: Optional[str] = None):
    """Restarts the current deal from scratch with same dealer and ladder score."""
    sess = get_session(game_id)
    state = sess.restart_current_deal()
    return state


@app.post("/api/select_hidden_trump")
def select_hidden_trump(req: SelectTrumpRequest):
    sess = get_session(req.game_id)
    try:
        state = sess.select_hidden_trump(req.card_code)
        return state
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/open_trump")
def open_trump_endpoint(req: OpenTrumpRequest):
    """Immediately reveals the hidden trump card face-up on table."""
    sess = get_session(req.game_id)
    success = sess.open_trump(req.player_id)
    if not success:
        raise HTTPException(status_code=400, detail="Cannot open trump at this time.")
    return sess.get_state()


@app.post("/api/declare")
def declare_contract(req: DeclareRequest):
    sess = get_session(req.game_id)
    try:
        state = sess.declare_contract(req.player_id, req.contract)
        return state
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/resolve_bidding")
def resolve_bidding(game_id: Optional[str] = None):
    sess = get_session(game_id)
    state = sess.get_state()
    for p, ptype in state['player_types'].items():
        if ptype == 'ai' and state['declarations'].get(p, "Regular") == "Regular":
            hand = [Card.from_code(c['code']) for c in state['hands'][p]]
            ai_bid = evaluate_bidding_heuristic(hand)
            if ai_bid != "Regular":
                sess.declare_contract(p, ai_bid)
                
    return sess.resolve_bidding()


@app.post("/api/set_runtime_trump")
def set_runtime_trump(req: RuntimeTrumpRequest):
    sess = get_session(req.game_id)
    try:
        state = sess.set_runtime_trump(req.suit)
        return state
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/ask_trump")
def ask_trump_endpoint(req: AskTrumpRequest):
    sess = get_session(req.game_id)
    try:
        state = sess.demand_runtime_trump(req.player_id)
        return state
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/play")
def play_card(req: PlayRequest):
    sess = get_session(req.game_id)
    try:
        state = sess.play_card(req.player_id, req.card_code, req.demand_cut)
        return state
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/ai_turn")
def ai_turn(game_id: Optional[str] = None, use_ollama: bool = False, model: str = "llama3"):
    sess = get_session(game_id)
    state = sess.get_state()
    if state['round_complete'] or state['deal_stage'] == "SELECT_TRUMP":
        return state

    current_player = state['current_turn_player']
    if state['player_types'].get(current_player) != 'ai':
        raise HTTPException(status_code=400, detail=f"Player {current_player} is set as human.")

    if state['bidding_phase']:
        hand = [Card.from_code(c['code']) for c in state['hands'][current_player]]
        ai_bid = evaluate_bidding_heuristic(hand)
        sess.declare_contract(current_player, ai_bid)
        return sess.resolve_bidding()

    if state['mode'] in ("Tera", "Double Tera") and not state['trump_revealed'] and state['declarer_id']:
        # If trump selection is waiting on a human declarer, pause AI until human picks trump
        if state.get('trump_selection_pending_from'):
            return state

        curr_hand = [Card.from_code(c['code']) for c in state['hands'][current_player]]
        is_void = bool(sess.led_suit and not any(c.suit == sess.led_suit for c in curr_hand))
        if is_void:
            decl_id = state['declarer_id']
            if state['player_types'].get(decl_id) == 'ai':
                decl_hand = [Card.from_code(c['code']) for c in state['hands'][decl_id]]
                best_suit = select_runtime_trump_heuristic(decl_hand)
                sess.trump_demanded_by = current_player
                sess.set_runtime_trump(best_suit)
                sess.must_play_trump_player = current_player
                state = sess.get_state()
            else:
                sess.trump_demanded_by = current_player
                sess.must_play_trump_player = current_player
                sess.trump_selection_pending_from = decl_id
                sess.current_round_logs.append(
                    f"{sess.player_names[current_player]} DEMANDED TRUMP from Declarer {sess.player_names[decl_id]}!"
                )
                return sess.get_state()

    card_code, demand_cut = get_ai_move(
        state,
        current_player,
        use_ollama=use_ollama,
        model=model
    )

    try:
        new_state = sess.play_card(current_player, card_code, demand_cut)
        return new_state
    except ValueError as e:
        player_cards = [Card.from_code(c['code']) for c in state['hands'][current_player]]
        if sess.must_play_trump_player == current_player and sess.trump_suit and sess.trump_revealed:
            has_led = sess.led_suit and any(c.suit == sess.led_suit for c in player_cards)
            if not has_led:
                t_cards = [c for c in player_cards if c.suit == sess.trump_suit]
                if t_cards:
                    player_cards = t_cards
        legal_cards = get_legal_cards(player_cards, sess.led_suit)
        fallback_card = legal_cards[0] if legal_cards else player_cards[0]
        try:
            new_state = sess.play_card(current_player, fallback_card.code, False)
            return new_state
        except Exception:
            for c in player_cards:
                try:
                    return sess.play_card(current_player, c.code, False)
                except Exception:
                    continue
            raise HTTPException(status_code=400, detail=f"AI player {current_player} has no legal move: {e}")


@app.post("/api/config")
def set_config(req: ConfigRequest):
    sess = get_session(req.game_id)
    sess.player_types.update(req.player_types)
    return sess.get_state()


# ==================== LOGS & ARCHIVE ENDPOINTS ====================

@app.get("/api/logs/latest")
def get_latest_logs(game_id: Optional[str] = None):
    """Returns the text log and stats of the requested or latest game session."""
    sess = get_session(game_id)
    txt_path = sess.logger.current_txt_path
    if txt_path and os.path.exists(txt_path):
        with open(txt_path, "r", encoding="utf-8") as f:
            content = f.read()
        return {'session_id': sess.logger.session_id, 'log_text': content, 'json_path': sess.logger.current_json_path}
    return {'session_id': sess.logger.session_id, 'log_text': "No deals completed yet.", 'json_path': None}


@app.get("/api/logs/list")
def list_logs():
    """Lists all archived games grouped by date."""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "play_logs"))
    if not os.path.exists(base_dir):
        return {'dates': [], 'files': []}

    dates = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    dates.sort(reverse=True)

    result = {}
    for d in dates:
        d_path = os.path.join(base_dir, d)
        files = [f for f in os.listdir(d_path) if f.endswith(".txt")]
        result[d] = files
    return {'dates': dates, 'files_by_date': result}


# ==================== TIKDI (3-PLAYER) ENDPOINTS ====================

@app.post("/api/tikdi/create-room")
def create_tikdi_room(req: CreateTikdiRoomRequest):
    """Initializes or resets a Tikdi 3-player match with custom seat types."""
    gid = req.game_id or f"TK-{random.randint(1000, 9999)}"
    sess = TikdiSession(game_id=gid, host_name=req.host_name, trump_chooser=req.trump_chooser, penalty_mode=req.penalty_mode or "choice")
    
    types = req.seats_config or req.player_types
    if types:
        sess.player_types.update(types)
    names = req.seat_names or req.player_names
    if names:
        sess.player_names.update(names)
        
    tikdi_sessions[gid] = sess
    state = sess.to_dict(perspective_player="P1")
    return {"game_id": gid, "state": state, **state}


@app.get("/api/tikdi/state")
def get_tikdi_state(game_id: Optional[str] = "tikdi1", seat: Optional[str] = "P1"):
    sess = get_tikdi_session(game_id)
    state = sess.to_dict(perspective_player=seat or "P1")
    return {"game_id": game_id, "state": state, **state}


@app.post("/api/tikdi/select-trump")
def tikdi_select_trump(req: TikdiTrumpRequest):
    sess = get_tikdi_session(req.game_id)
    seat = req.seat or req.player_id or sess.trump_chooser
    suit = req.trump_suit or req.suit
    success = sess.select_trump(suit, player=seat)
    if not success:
        raise HTTPException(status_code=400, detail="Unable to select trump")
    state = sess.to_dict(perspective_player=seat)
    return {"state": state, **state}


@app.post("/api/tikdi/pull-card")
def tikdi_pull_card(req: TikdiPullCardRequest):
    sess = get_tikdi_session(req.game_id)
    seat = req.seat or req.puller_id
    pulled = sess.pull_penalty_card(creditor=seat, card_index=req.card_index)
    if not pulled:
        raise HTTPException(status_code=400, detail="Unable to pull penalty card")
    state = sess.to_dict(perspective_player=seat)
    return {"pulled_card": pulled.code, "state": state, **state}


@app.post("/api/tikdi/return-card")
def tikdi_return_card(req: TikdiReturnCardRequest):
    sess = get_tikdi_session(req.game_id)
    seat = req.seat or req.returner_id
    success = sess.return_penalty_card(creditor=seat, card_code=req.card_code)
    if not success:
        raise HTTPException(status_code=400, detail="Unable to return penalty card")
    state = sess.to_dict(perspective_player=seat)
    return {"state": state, **state}


@app.post("/api/tikdi/play-card")
def tikdi_play_card(req: TikdiPlayCardRequest):
    sess = get_tikdi_session(req.game_id)
    seat = req.seat or req.player_id
    res = sess.play_card(seat, req.card_code)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error", "Illegal play"))
    state = sess.to_dict(perspective_player=seat)
    return {"result": res, "state": state, **state}


@app.post("/api/tikdi/bot-step")
def tikdi_bot_step(req: Optional[TikdiBotStepRequest] = None, game_id: Optional[str] = None):
    gid = (req.game_id if req and req.game_id else None) or game_id
    if not gid:
        raise HTTPException(status_code=400, detail="game_id is required")
    sess = get_tikdi_session(gid)
    step_res = sess.step_bot()
    state = sess.to_dict(perspective_player="P1")
    return {"bot_result": step_res, "state": state, **state}


@app.post("/api/tikdi/next-round")
def tikdi_next_round(req: Optional[TikdiNextRoundRequest] = None, game_id: Optional[str] = None):
    gid = (req.game_id if req and req.game_id else None) or game_id
    if not gid:
        raise HTTPException(status_code=400, detail="game_id is required")
    sess = get_tikdi_session(gid)
    sess.next_round()
    state = sess.to_dict(perspective_player="P1")
    return {"state": state, **state}


@app.post("/api/tikdi/make-debt-choice")
def tikdi_make_debt_choice(req: TikdiMakeDebtChoiceRequest):
    sess = get_tikdi_session(req.game_id)
    seat = req.seat or req.debtor_id or req.player_id
    success = sess.make_debt_choice(debtor=seat, choice=req.choice)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid debt settlement choice or not debtor's turn")
    state = sess.to_dict(perspective_player=seat)
    return {"state": state, **state}


@app.post("/api/tikdi/switch-penalty-mode")
def tikdi_switch_penalty_mode(req: TikdiSwitchPenaltyModeRequest):
    sess = get_tikdi_session(req.game_id)
    sess.penalty_mode = req.penalty_mode
    if req.penalty_mode == "quota_adjustment":
        # Convert any active card_swap penalties into extra tricks immediately
        if sess.phase == "PENALTY_RESOLUTION" and sess.penalty_queue:
            for pen in sess.penalty_queue:
                creditor = pen["creditor"]
                debtor = pen["debtor"]
                sess.quotas[debtor] = sess.quotas.get(debtor, 0) + 1
                sess.quotas[creditor] = max(0, sess.quotas.get(creditor, 0) - 1)
                sess.logs.append(
                    f"🎯 Debtor {sess.player_names.get(debtor, debtor)} switched to Extra Tricks (+1 to quota) for {sess.player_names.get(creditor, creditor)}"
                )
            sess.penalty_queue = []
            sess.current_penalty = None
            sess.debts = {p: {} for p in sess.players}
            sess.phase = "TRICK_PLAYING"
            sess.current_turn = sess.trump_chooser
            sess.logs.append("✅ Switched to Extra Tricks. Trick play begins!")
        else:
            has_debts = any(ds for ds in sess.debts.values() if ds)
            if has_debts:
                sess._prepare_pending_adjustments()
                sess.phase = "PENALTY_ADJUSTMENT"
                sess.current_turn = sess.trump_chooser
                sess.logs.append("🔄 Switched to Quota Adjustment mode. Review adjusted quotas.")
            else:
                sess.phase = "TRICK_PLAYING"
                sess.current_turn = sess.trump_chooser
                sess.logs.append("🎯 Switched to Quota Adjustment mode. No debts to adjust.")
    state = sess.to_dict(perspective_player=req.player_id or "P1")
    return {"state": state, **state}


@app.post("/api/tikdi/acknowledge-adjustment")
def tikdi_acknowledge_adjustment(req: TikdiAcknowledgeAdjustmentRequest):
    """Player acknowledges quota adjustments, allowing trick play to begin."""
    sess = get_tikdi_session(req.game_id)
    success = sess.acknowledge_adjustment(player=req.player_id)
    if not success:
        raise HTTPException(status_code=400, detail="Not in penalty adjustment phase")
    state = sess.to_dict(perspective_player=req.player_id or "P1")
    return {"state": state, **state}


# ==================== JHUTHANIYA (BLUFF) ENDPOINTS ====================

@app.post("/api/jhuthaniya/create-room")
def create_jhuthaniya_room(req: CreateJhuthaniyaRoomRequest):
    """Creates a new Jhuthaniya room with 2–7 players."""
    gid = req.game_id or f"JH-{random.randint(1000, 9999)}"
    sess = JhuthaniyaSession(
        game_id=gid,
        host_name=req.host_name,
        num_players=req.num_players,
        player_names=req.player_names,
        player_types=req.player_types,
    )
    jhuthaniya_sessions[gid] = sess
    state = sess.to_dict("P1")
    return {"game_id": gid, "state": state, **state}


@app.get("/api/jhuthaniya/state")
def get_jhuthaniya_state(game_id: Optional[str] = "jhuth1", seat: Optional[str] = "P1"):
    sess = get_jhuthaniya_session(game_id)
    state = sess.to_dict(seat or "P1")
    return {"game_id": game_id, "state": state, **state}


@app.post("/api/jhuthaniya/play")
def jhuthaniya_play(req: JhuthaniyaPlayRequest):
    """Active player places cards face-down and declares a rank claim."""
    sess = get_jhuthaniya_session(req.game_id)
    result = sess.play_cards(
        player_id=req.player_id,
        card_codes=req.card_codes,
        claimed_rank=req.claimed_rank,
        claimed_count=req.claimed_count,
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Play failed"))
    state = sess.to_dict(req.player_id)
    return {"result": result, "state": state, **state}


@app.post("/api/jhuthaniya/challenge")
def jhuthaniya_challenge(req: JhuthaniyaDecisionRequest):
    """Player calls JHUTH (challenge) or PASS during the challenge window."""
    sess = get_jhuthaniya_session(req.game_id)
    result = sess.make_decision(req.player_id, req.decision, req.card_index or 0)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Decision failed"))
    state = sess.to_dict(req.player_id)
    return {"result": result, "state": state, **state}


@app.post("/api/jhuthaniya/bot-step")
def jhuthaniya_bot_step(req: JhuthaniyaBotStepRequest):
    """Executes one bot action (play or challenge decision)."""
    sess = get_jhuthaniya_session(req.game_id)
    step_res = sess.step_bot()
    state = sess.to_dict("P1")
    return {"bot_result": step_res, "state": state, **state}


@app.post("/api/jhuthaniya/new-game")
def jhuthaniya_new_game(req: JhuthaniyaNewGameRequest):
    """Resets the Jhuthaniya game with same players."""
    sess = get_jhuthaniya_session(req.game_id)
    sess.new_game()
    state = sess.to_dict("P1")
    return {"state": state, **state}


# ==================== BINDI COAT (MINDIKOT) ENDPOINTS ====================

@app.post("/api/bindi-coat/create-room")
def create_bindi_coat_room(req: CreateBindiCoatRoomRequest):
    """Creates a new Bindi Coat room (4-player Mindikot / Bandh Hukum)."""
    gid = req.game_id or f"BC-{random.randint(1000, 9999)}"
    sess = BindiCoatSession(
        game_id=gid,
        host_name=req.host_name,
        player_names=req.player_names,
        player_types=req.player_types,
    )
    bindi_coat_sessions[gid] = sess
    state = sess.to_dict("P1")
    return {"game_id": gid, "state": state, **state}


@app.get("/api/bindi-coat/state")
def get_bindi_coat_state(game_id: Optional[str] = "bc1", seat: Optional[str] = "P1"):
    sess = get_bindi_coat_session(game_id)
    state = sess.to_dict(seat or "P1")
    return {"game_id": game_id, "state": state, **state}


@app.post("/api/bindi-coat/select-bandh-hukum")
def bindi_coat_select_bandh_hukum(req: BindiCoatSelectBandhHukumRequest):
    """Trump Placer places one card face-down as hidden trump (Bandh Hukum)."""
    sess = get_bindi_coat_session(req.game_id)
    result = sess.select_bandh_hukum(req.player_id, card_code=req.card_code, card_index=req.card_index)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Bandh Hukum selection failed"))
    state = sess.to_dict(req.player_id)
    return {"result": result, "state": state, **state}


@app.post("/api/bindi-coat/play")
def bindi_coat_play(req: BindiCoatPlayRequest):
    """Player plays a card in the current trick. Auto-triggers trump reveal if void in led suit."""
    sess = get_bindi_coat_session(req.game_id)
    result = sess.play_card(req.player_id, req.card_code)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Card play failed"))
    state = sess.to_dict(req.player_id)
    return {"result": result, "state": state, **state}


@app.post("/api/bindi-coat/bot-step")
def bindi_coat_bot_step(req: BindiCoatBotStepRequest):
    """Executes one bot action (Bandh Hukum selection or card play)."""
    sess = get_bindi_coat_session(req.game_id)
    step_res = sess.step_bot()
    state = sess.to_dict("P1")
    return {"bot_result": step_res, "state": state, **state}


@app.post("/api/bindi-coat/next-round")
def bindi_coat_next_round(req: BindiCoatNextRoundRequest):
    """Starts the next round, rotating the dealer."""
    sess = get_bindi_coat_session(req.game_id)
    sess.next_round()
    state = sess.to_dict("P1")
    return {"state": state, **state}


# ==================== STATIC & FAVICON ====================

frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    svg_path = os.path.join(frontend_dir, "favicon.svg")
    if os.path.exists(svg_path):
        return FileResponse(svg_path, media_type="image/svg+xml")
    raise HTTPException(status_code=404)

if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
