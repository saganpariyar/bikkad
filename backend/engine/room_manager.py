import random
import string
from typing import Dict, Any, Optional, List


BOT_BASE_NAMES = [
    "Bhimaram", "Jitu", "Dinesh", "Geeta", "Suraj", "Kantilal",
    "Prakash", "S Kumar", "Sangeeta", "Anita", "Mangilal", "Lumbaram",
    "Chogaram", "Sukhi", "Naresh", "Ganaram", "Sagan"
]
BOT_NAMES = [f"G. {name}" for name in BOT_BASE_NAMES]
COM_NAMES = BOT_NAMES


def get_random_bot_names(count: int = 3, exclude_name: str = "") -> List[str]:
    """Returns unique randomly sampled bot names prefixed with 'G.' excluding the given player name."""
    clean_ex = (exclude_name or "").lower().replace("g.", "").replace("bot", "").strip()
    available = [
        name for name in BOT_BASE_NAMES
        if clean_ex not in name.lower() and name.lower() not in clean_ex
    ]
    if len(available) < count:
        available = list(BOT_BASE_NAMES)
    sampled = random.sample(available, min(count, len(available)))
    return [f"G. {name}" for name in sampled]


class RoomManager:
    """
    Manages game rooms, unique Game IDs (e.g., BIK-7842), setup modes
    (1-3 COM, 2-2 COM, 3-1 COM, 4-0 COM), and player seat allocations.
    """

    def __init__(self):
        self.rooms: Dict[str, Dict[str, Any]] = {}

    def generate_unique_game_id(self) -> str:
        """Generates a simple 4-digit numeric room code like 4821."""
        for _ in range(100):
            digits = "".join(random.choices(string.digits, k=4))
            game_id = digits
            if game_id not in self.rooms:
                return game_id
        # Fallback: 6-digit number
        return "".join(random.choices(string.digits, k=6))

    @staticmethod
    def resolve_initial_dealer(trump_hider: str = "P1") -> str:
        """
        Resolves initial dealer so that the chosen player hides trump & leads Trick 1:
        Clockwise order: P1 -> P2 -> P3 -> P4 -> P1
        Eldest Hand (hides trump & leads) = left of dealer (get_next_opponent(dealer))
        - Player 1 (P1) hides trump -> Dealer is P4
        - Player 2 (P2) hides trump -> Dealer is P1
        - Player 3 (P3) hides trump -> Dealer is P2
        - Player 4 (P4) hides trump -> Dealer is P3
        - 'random' -> Random player is selected to hide trump
        """
        hider_map = {
            'P1': 'P4',
            '1': 'P4',
            'ME': 'P4',
            'ME_TRUMP': 'P4',
            'P2': 'P1',
            '2': 'P1',
            'P3': 'P2',
            '3': 'P2',
            'P4': 'P3',
            '4': 'P3',
            'ME_DEALER': 'P1'
        }
        val = (trump_hider or "P1").strip().upper()
        if val in ("RANDOM", "RAND"):
            chosen = random.choice(['P1', 'P2', 'P3', 'P4'])
            return hider_map[chosen]
        return hider_map.get(val, 'P4')

    def create_room(
        self,
        host_name: str = "Sagan",
        game_name: str = "game1",
        setup_mode: str = "1-3 com",
        first_deal_role: str = "me_trump",
        game_id: Optional[str] = None,
        seats_config: Optional[Dict[str, str]] = None,
        seat_names: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Creates or registers a room with custom setup mode or explicit seats_config:
          seats_config: e.g. {'P2': 'ai', 'P3': 'human', 'P4': 'ai'}
          seat_names: e.g. {'P3': 'Priya'}
        """
        if not game_id:
            game_id = self.generate_unique_game_id()
        else:
            game_id = game_id.strip()

        host_name = host_name.strip() if host_name and host_name.strip() else "Sagan"
        game_name = game_name.strip() if game_name and game_name.strip() else "game1"

        # Check if room already exists in lobby status to preserve connected players
        existing_room = self.rooms.get(game_id) or self.rooms.get(game_id.upper())

        # Default seat structure
        bot_picks = get_random_bot_names(3, host_name)
        seats: Dict[str, Dict[str, Any]] = {
            'P1': {
                'seat_id': 'P1',
                'name': host_name,
                'type': 'human',
                'team': 'Team A',
                'position': 'South',
                'role': 'Host',
                'is_host': True,
                'connected': True
            },
            'P2': {
                'seat_id': 'P2',
                'name': bot_picks[0],
                'type': 'ai',
                'team': 'Team B',
                'position': 'West',
                'role': 'Opponent 1',
                'is_host': False,
                'connected': True
            },
            'P3': {
                'seat_id': 'P3',
                'name': bot_picks[1],
                'type': 'ai',
                'team': 'Team A',
                'position': 'North',
                'role': 'Partner',
                'is_host': False,
                'connected': True
            },
            'P4': {
                'seat_id': 'P4',
                'name': bot_picks[2],
                'type': 'ai',
                'team': 'Team B',
                'position': 'East',
                'role': 'Opponent 2',
                'is_host': False,
                'connected': True
            }
        }

        # Apply explicit seats_config if provided
        if seats_config:
            for s_id in ['P2', 'P3', 'P4']:
                stype = seats_config.get(s_id, 'ai')
                if stype == 'human':
                    seats[s_id]['type'] = 'human'
                    custom_name = (seat_names.get(s_id) or '').strip() if seat_names else ''
                    seats[s_id]['name'] = custom_name if custom_name else 'Waiting for Friend (or BOT)'
                    seats[s_id]['connected'] = bool(custom_name and not custom_name.startswith("Waiting"))
                else:
                    seats[s_id]['type'] = 'ai'
        else:
            # Adjust defaults according to setup_mode
            if setup_mode == "2-2 com":
                # P3 (Partner) defaults to an open Human slot for a friend
                seats['P3']['type'] = 'human'
                seats['P3']['name'] = 'Waiting for Friend (or BOT)'
                seats['P3']['connected'] = False
            elif setup_mode == "3-1 com":
                # P3 and P2 default to Human slots
                seats['P3']['type'] = 'human'
                seats['P3']['name'] = 'Waiting for Friend (or BOT)'
                seats['P3']['connected'] = False
                seats['P2']['type'] = 'human'
                seats['P2']['name'] = 'Waiting for Friend (or BOT)'
                seats['P2']['connected'] = False
            elif setup_mode == "4-0 com":
                seats['P3']['type'] = 'human'
                seats['P3']['name'] = 'Waiting for Friend (or BOT)'
                seats['P3']['connected'] = False
                seats['P2']['type'] = 'human'
                seats['P2']['name'] = 'Waiting for Friend (or BOT)'
                seats['P2']['connected'] = False
                seats['P4']['type'] = 'human'
                seats['P4']['name'] = 'Waiting for Friend (or BOT)'
                seats['P4']['connected'] = False

        # Preserve any previously connected human seats if updating an existing lobby room
        if existing_room and existing_room.get('status') == 'lobby':
            for p in ['P2', 'P3', 'P4']:
                prev_seat = existing_room.get('seats', {}).get(p)
                if (
                    prev_seat
                    and prev_seat.get('type') == 'human'
                    and prev_seat.get('connected')
                    and not prev_seat.get('name', '').startswith('COM ')
                    and not prev_seat.get('name', '').startswith('BOT ')
                    and not prev_seat.get('name', '').startswith('G. ')
                    and prev_seat.get('name') not in ("Waiting for Player", "Waiting for Friend (or COM)", "Waiting for Friend (or BOT)")
                ):
                    seats[p]['name'] = prev_seat['name']
                    seats[p]['type'] = 'human'
                    seats[p]['connected'] = True

        room_data = {
            'game_id': game_id,
            'game_name': game_name,
            'host_name': host_name,
            'setup_mode': setup_mode,
            'first_deal_role': first_deal_role,
            'status': 'lobby',  # 'lobby', 'playing', 'finished'
            'seats': seats,
            'waiting_players': existing_room.get('waiting_players', []) if existing_room else [],
            'created_at': None
        }

        self.rooms[game_id] = room_data
        return room_data

    def get_room(self, game_id: str) -> Optional[Dict[str, Any]]:
        clean = (game_id or "").strip()
        return self.rooms.get(clean) or self.rooms.get(clean.upper())

    def join_room(self, game_id: str, player_name: str) -> Dict[str, Any]:
        """
        Player joins an existing room using unique Game ID.
        Assigns to first available open human seat or adds to waiting list.
        """
        game_id_clean = game_id.strip()  # numeric IDs don't need uppercasing
        # Also try as-is if not found
        room = self.rooms.get(game_id_clean) or self.rooms.get(game_id_clean.upper())
        if not room:
            raise ValueError(f"Game room '{game_id_clean}' not found.")

        player_name = player_name.strip() if player_name and player_name.strip() else "Guest"

        # Check if player already seated (skip P1/host — prevent same-name collision)
        for seat_id, seat in room['seats'].items():
            if seat_id == 'P1':
                continue  # never re-assign host seat
            if seat['type'] == 'human' and seat['name'].lower() == player_name.lower() and seat.get('connected'):
                seat['connected'] = True
                return {'success': True, 'game_id': game_id_clean, 'seat_id': seat_id, 'room': room}

        # Find first unassigned/waiting human seat
        assigned_seat = None
        for seat_id in ['P3', 'P2', 'P4']:
            seat = room['seats'][seat_id]
            if seat['type'] == 'human' and (not seat['connected'] or "Waiting" in seat['name']):
                seat['name'] = player_name
                seat['connected'] = True
                assigned_seat = seat_id
                break

        # If no open human seat, add to waiting_players list so host can assign them
        if not assigned_seat:
            if player_name not in room['waiting_players']:
                room['waiting_players'].append(player_name)

        return {
            'success': True,
            'game_id': game_id_clean,
            'seat_id': assigned_seat,
            'room': room
        }

    def assign_seat(
        self,
        game_id: str,
        seat_id: str,
        player_name: str,
        player_type: str = "ai"
    ) -> Dict[str, Any]:
        """
        Creator chooses who is Player 2, 3, or 4 (human friend or COM bot).
        """
        game_id_clean = (game_id or "").strip()
        room = self.rooms.get(game_id_clean) or self.rooms.get(game_id_clean.upper())
        if not room:
            raise ValueError(f"Game room '{game_id_clean}' not found.")

        if seat_id not in ('P2', 'P3', 'P4'):
            raise ValueError(f"Cannot reassign host seat {seat_id}.")

        room['seats'][seat_id]['name'] = player_name
        room['seats'][seat_id]['type'] = player_type
        room['seats'][seat_id]['connected'] = True

        # Remove from waiting list if present
        if player_name in room['waiting_players']:
            room['waiting_players'].remove(player_name)

        return room

    def start_room(self, game_id: str) -> Dict[str, Any]:
        """Marks room as playing and validates all seats."""
        game_id_clean = (game_id or "").strip()
        room = self.rooms.get(game_id_clean) or self.rooms.get(game_id_clean.upper())
        if not room:
            raise ValueError(f"Game room '{game_id_clean}' not found.")

        # Ensure any empty seats or un-connected human seats are filled with BOTs
        existing_names = [s['name'] for s in room['seats'].values() if s.get('name') and "Waiting" not in s['name']]
        for seat_id, seat in room['seats'].items():
            if seat_id == 'P1':
                continue
            if not seat['name'] or "Waiting" in seat['name'] or (seat.get('type') == 'human' and not seat.get('connected')):
                picked = get_random_bot_names(1, exclude_name=",".join(existing_names))
                bot_name = picked[0] if picked else f"G. Bot {seat_id}"
                seat['name'] = bot_name
                existing_names.append(bot_name)
                seat['type'] = 'ai'
                seat['connected'] = True

        room['status'] = 'playing'
        return room


# Global singleton
room_manager = RoomManager()
