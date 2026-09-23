import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any


class GameLogger:
    """
    Persistent Game and Play Logger for Bikkad.
    Outputs:
      1. Detailed human-readable play log (.txt) in the master archive format
      2. Comprehensive structured JSON (.json) for programmatic analysis/stats
      3. Daily match ledger summary (.txt)
      4. Master games index (.json)
    """

    def __init__(self, base_data_dir: Optional[str] = None):
        if not base_data_dir:
            # Default to d:/Projects/sagan/Bikkad/data/play_logs
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.base_dir = os.path.join(base_dir, "data", "play_logs")
        else:
            self.base_dir = base_data_dir

        self.game_name: str = "game1"
        self.session_id: str = ""
        self.start_time: datetime = datetime.now()
        self.date_str: str = self.start_time.strftime("%Y-%m-%d")
        self.ts_str: str = self.start_time.strftime("%Y%m%d_%H%M%S")

        self.player_names: Dict[str, str] = {}
        self.player_teams: Dict[str, str] = {}
        self.player_types: Dict[str, str] = {}

        # Logged state
        self.deals_history: List[Dict[str, Any]] = []
        self.current_deal: Optional[Dict[str, Any]] = None

        # Paths
        self.current_txt_path: Optional[str] = None
        self.current_json_path: Optional[str] = None

    def start_game(
        self,
        game_name: str,
        player_names: Dict[str, str],
        player_teams: Dict[str, str],
        player_types: Dict[str, str]
    ):
        """Initializes a new game session log."""
        self.game_name = game_name or "game1"
        self.start_time = datetime.now()
        self.date_str = self.start_time.strftime("%Y-%m-%d")
        self.ts_str = self.start_time.strftime("%Y%m%d_%H%M%S")
        self.session_id = f"{self.game_name}_{self.ts_str}"

        self.player_names = dict(player_names)
        self.player_teams = dict(player_teams)
        self.player_types = dict(player_types)
        self.deals_history = []
        self.current_deal = None

        # Prepare date folder
        date_dir = os.path.join(self.base_dir, self.date_str)
        os.makedirs(date_dir, exist_ok=True)

        self.current_txt_path = os.path.join(date_dir, f"{self.session_id}.txt")
        self.current_json_path = os.path.join(date_dir, f"{self.session_id}.json")

        self.save_to_disk()

    def start_deal(
        self,
        deal_number: int,
        dealer_id: str,
        dealer_score: int,
        dealer_team: str,
        lead_team: str,
        eldest_hand: str,
        hands: Dict[str, List[Any]],
        phase1_deals: Optional[Dict[str, List[Any]]] = None,
        phase2_deals: Optional[Dict[str, List[Any]]] = None,
        phase3_deals: Optional[Dict[str, List[Any]]] = None
    ):
        """Starts logging a new deal."""
        def serialize_cards(card_list):
            if not card_list:
                return []
            return [getattr(c, 'code', str(c)) for c in card_list]

        self.current_deal = {
            'deal_number': deal_number,
            'start_timestamp': datetime.now().isoformat(),
            'dealer_id': dealer_id,
            'dealer_name': self.player_names.get(dealer_id, dealer_id),
            'dealer_score_start': dealer_score,
            'dealer_team': dealer_team,
            'lead_team': lead_team,
            'eldest_hand': eldest_hand,
            'eldest_name': self.player_names.get(eldest_hand, eldest_hand),
            'mode': "Regular",
            'declarer_id': None,
            'declarer_name': None,
            'hidden_trump': None,
            'trump_setter': None,
            'trump_opener': None,
            'trump_suit': None,
            'trump_revealed': False,
            'trump_revealed_trick': None,
            'declarations': {},
            'phase1_deals': {p: serialize_cards(c) for p, c in (phase1_deals or {}).items()},
            'phase2_deals': {p: serialize_cards(c) for p, c in (phase2_deals or {}).items()},
            'phase3_deals': {p: serialize_cards(c) for p, c in (phase3_deals or {}).items()},
            'initial_hands': {p: serialize_cards(c) for p, c in hands.items()},
            'tricks': [],
            'result': None
        }
        self.save_to_disk()

    def log_hidden_trump_set(self, setter_id: str, card_code: str):
        if self.current_deal:
            self.current_deal['hidden_trump'] = card_code
            self.current_deal['trump_setter'] = setter_id
            self.save_to_disk()

    def log_mode_declaration(self, mode: str, declarer_id: Optional[str], declarations: Dict[str, str]):
        if self.current_deal:
            self.current_deal['mode'] = mode
            self.current_deal['declarer_id'] = declarer_id
            self.current_deal['declarer_name'] = self.player_names.get(declarer_id, declarer_id) if declarer_id else None
            self.current_deal['declarations'] = dict(declarations)
            self.save_to_disk()

    def log_trump_revealed(self, opener_id: str, trump_card: Optional[str], trump_suit: str, trick_number: int):
        if self.current_deal:
            self.current_deal['trump_revealed'] = True
            self.current_deal['trump_opener'] = opener_id
            self.current_deal['trump_suit'] = trump_suit
            self.current_deal['trump_revealed_trick'] = trick_number
            if trump_card:
                self.current_deal['hidden_trump'] = trump_card
            self.save_to_disk()

    def log_trick(
        self,
        trick_number: int,
        led_suit: str,
        trick_cards: List[tuple],  # List of (player_id, Card)
        winner_player_id: str,
        winning_card: Any,
        pot_cards_count: int,
        pot_tricks_count: int,
        collected: bool,
        collecting_team: Optional[str],
        cards_collected: int,
        collection_reason: str,
        streak_holder: Optional[str],
        streak_count: int,
        trump_revealed: bool,
        trump_suit: Optional[str],
        cut_player: Optional[str] = None
    ):
        """Logs a completed trick with rich metadata and card notations."""
        if not self.current_deal:
            return

        winning_code = getattr(winning_card, 'code', str(winning_card))
        cards_played_meta = []

        for p_id, c in trick_cards:
            code = getattr(c, 'code', str(c))
            suit_val = getattr(c, 'suit', None)
            suit_str = getattr(suit_val, 'value', str(suit_val)) if suit_val else ""

            is_lead = (len(cards_played_meta) == 0)
            is_winner = (p_id == winner_player_id)
            is_void = (suit_str != led_suit and not is_lead)
            is_cut = (trump_revealed and trump_suit and suit_str == trump_suit and is_void)

            # Mark symbol
            notation = code
            if is_winner and is_cut:
                notation += "#*"
            elif is_winner:
                notation += "*"
            elif is_cut:
                notation += "#"
            elif is_void:
                notation = f"[{notation}]"

            cards_played_meta.append({
                'player_id': p_id,
                'player_name': self.player_names.get(p_id, p_id),
                'card': code,
                'notation': notation,
                'is_lead': is_lead,
                'is_winner': is_winner,
                'is_void': is_void,
                'is_cut': is_cut
            })

        trick_record = {
            'trick_number': trick_number,
            'led_suit': led_suit,
            'cards': cards_played_meta,
            'winner_id': winner_player_id,
            'winner_name': self.player_names.get(winner_player_id, winner_player_id),
            'winner_team': self.player_teams.get(winner_player_id, ""),
            'winning_card': winning_code,
            'pot_cards_after': pot_cards_count,
            'pot_tricks_after': pot_tricks_count,
            'collected': collected,
            'collecting_team': collecting_team,
            'cards_collected': cards_collected,
            'collection_reason': collection_reason,
            'streak_holder': streak_holder,
            'streak_count': streak_count,
            'cut_player': cut_player
        }

        self.current_deal['tricks'].append(trick_record)
        self.save_to_disk()

    def end_deal(
        self,
        tricks_won: Dict[str, int],
        cards_collected: Dict[str, int],
        delta: int,
        raw_new_score: int,
        next_dealer: str,
        starting_score: int = 0,
        score_note: str = "",
        rotation_status: str = "",
        next_starting_score: Optional[int] = None,
        **kwargs
    ):
        """Finalizes the current deal log."""
        if next_starting_score is not None:
            starting_score = next_starting_score
        if not self.current_deal:
            return

        self.current_deal['end_timestamp'] = datetime.now().isoformat()
        self.current_deal['result'] = {
            'tricks_won': dict(tricks_won),
            'cards_collected': dict(cards_collected),
            'delta': delta,
            'dealer_score_end': raw_new_score,
            'next_dealer': next_dealer,
            'next_dealer_name': self.player_names.get(next_dealer, next_dealer),
            'next_starting_score': starting_score,
            'score_note': score_note,
            'rotation_status': rotation_status
        }

        self.deals_history.append(self.current_deal)
        self.current_deal = None
        self.save_to_disk()
        self._update_master_indices()

    def save_to_disk(self):
        """Writes both human-readable .txt and complete .json files."""
        if not self.current_txt_path or not self.current_json_path:
            return

        # 1. Write JSON
        payload = {
            'game_name': self.game_name,
            'session_id': self.session_id,
            'start_time': self.start_time.isoformat(),
            'last_updated': datetime.now().isoformat(),
            'player_names': self.player_names,
            'player_teams': self.player_teams,
            'player_types': self.player_types,
            'deals': self.deals_history + ([self.current_deal] if self.current_deal else []),
            'stats': self._calculate_overall_stats()
        }

        try:
            with open(self.current_json_path, 'w', encoding='utf-8') as f:
                json.dump(payload, f, indent=2)
        except Exception as e:
            print(f"Error saving JSON log: {e}")

        # 2. Write formatted Text Log
        try:
            txt_content = self._render_txt_log(payload)
            with open(self.current_txt_path, 'w', encoding='utf-8') as f:
                f.write(txt_content)
        except Exception as e:
            print(f"Error saving TXT log: {e}")

    def _calculate_overall_stats(self) -> Dict[str, Any]:
        all_deals = self.deals_history + ([self.current_deal] if self.current_deal and self.current_deal.get('result') else [])
        team_a_wins = 0
        team_b_wins = 0
        tera_attempts = 0
        tera_success = 0
        double_tera_attempts = 0
        double_tera_success = 0

        for d in all_deals:
            res = d.get('result')
            if not res:
                continue
            tw = res.get('tricks_won', {})
            a_trks = tw.get('Team A', 0)
            b_trks = tw.get('Team B', 0)

            mode = d.get('mode', 'Regular')
            if mode == "Tera":
                tera_attempts += 1
                if (a_trks == 13 and d.get('declarer_id') in ('P1', 'P3')) or (b_trks == 13 and d.get('declarer_id') in ('P2', 'P4')):
                    tera_success += 1
            elif mode == "Double Tera":
                double_tera_attempts += 1
                if (a_trks == 13 and d.get('declarer_id') in ('P1', 'P3')) or (b_trks == 13 and d.get('declarer_id') in ('P2', 'P4')):
                    double_tera_success += 1

            if a_trks > b_trks:
                team_a_wins += 1
            elif b_trks > a_trks:
                team_b_wins += 1

        return {
            'total_deals': len(all_deals),
            'team_a_deals_won': team_a_wins,
            'team_b_deals_won': team_b_wins,
            'tera_attempts': tera_attempts,
            'tera_success': tera_success,
            'double_tera_attempts': double_tera_attempts,
            'double_tera_success': double_tera_success
        }

    def _render_txt_log(self, payload: Dict[str, Any]) -> str:
        lines = []
        p_names = payload.get('player_names', {})
        p1 = p_names.get('P1', 'P1')
        p2 = p_names.get('P2', 'P2')
        p3 = p_names.get('P3', 'P3')
        p4 = p_names.get('P4', 'P4')

        lines.append("=" * 104)
        lines.append("                                          BIKKAD PLAY ARCHIVE")
        lines.append(f"  Game Name: {self.game_name.upper()} | Date: {self.date_str} | Session: {self.session_id}")
        lines.append("=" * 104)
        lines.append("TEAMS:")
        lines.append(f"  Team A: {p1} (P1) & {p3} (P3)")
        lines.append(f"  Team B: {p2} (P2) & {p4} (P4)")
        lines.append("")
        lines.append("SUITS   : H = Hearts (Laal) | C = Clubs (Chidi) | D = Diamonds (Eet) | S = Spades (Hukum)")
        lines.append("NOTATION: * = Winning Card | [] = Off-Suit Discard | # = Cut with Trump Suit | #* = Cut & Won Trick | [Card] = Hidden Trump")
        lines.append("=" * 104)
        lines.append("")

        suit_names_map = {'H': 'Hearts (Laal)', 'C': 'Clubs (Chidi)', 'D': 'Diamonds (Eet)', 'S': 'Spades (Hukum)'}

        deals = payload.get('deals', [])
        for d in deals:
            d_num = d.get('deal_number', 1)
            mode = d.get('mode', 'Regular')
            dealer_id = d.get('dealer_id', 'P1')
            dealer_name = p_names.get(dealer_id, dealer_id)
            dealer_team = d.get('dealer_team', 'Team A')
            score_start = d.get('dealer_score_start', 0)
            eldest = d.get('eldest_hand', 'P2')
            eldest_name = p_names.get(eldest, eldest)
            hidden_trump = d.get('hidden_trump', 'None')
            trump_str = f"Hidden Trump: [{hidden_trump}]" if mode == "Regular" else f"Runtime Trump: [{d.get('trump_suit') or 'Pending'}]"

            lines.append("=" * 100)
            lines.append(f"GAME {d_num:02d} | {mode.upper()} | Dealer: {dealer_name} ({dealer_id}, {dealer_team}, Score: {score_start}) | Lead: {eldest_name} ({eldest}) | {trump_str}")
            lines.append("=" * 100)

            # Trump reveal details
            trump_rev_trick = d.get('trump_revealed_trick')
            trump_opener_id = d.get('trump_opener')
            trump_opener_name = p_names.get(trump_opener_id, trump_opener_id) if trump_opener_id else ""
            trump_suit_val = d.get('trump_suit', '')
            trump_suit_full = suit_names_map.get(trump_suit_val, trump_suit_val)
            setter_id = d.get('trump_setter') or eldest
            setter_name = p_names.get(setter_id, setter_id)

            # Trick plays
            tricks = d.get('tricks', [])
            for t in tricks:
                t_num = t.get('trick_number', 1)
                if d.get('trump_revealed') and trump_rev_trick == t_num:
                    lines.append(f">>> [TRUMP REVEALED in T{t_num:02d} by {trump_opener_name}]: Hidden Card [{hidden_trump}] (Trump Suit: {trump_suit_full}) | Card returned to {setter_name} hand <<<")
                led_suit = t.get('led_suit', '')
                cards = t.get('cards', [])
                card_entries = []
                for c in cards:
                    p_name = c.get('player_name') or p_names.get(c['player_id'], c['player_id'])
                    card_entries.append(f"{p_name}: {c['notation']}")
                cards_str = " | ".join(card_entries)

                w_id = t.get('winner_id', '')
                w_name = t.get('winner_name') or p_names.get(w_id, w_id)
                w_team = t.get('winner_team', '')
                pot_cards = t.get('pot_cards_after', 0)
                pot_tricks = t.get('pot_tricks_after', 0)

                collected = t.get('collected', False)
                if collected:
                    col_team = t.get('collecting_team', '')
                    col_count = t.get('cards_collected', 0)
                    reason = t.get('collection_reason', 'consecutive_streak').upper()
                    col_trks = col_count // 4
                    res_str = f"==> {col_team} collects {col_count} cards ({col_trks} trk) [{reason}]"
                else:
                    streak_holder = t.get('streak_holder')
                    streak_cnt = t.get('streak_count', 0)
                    streak_str = f" (Win {streak_cnt})" if streak_holder else ""
                    res_str = f"--> {w_name} wins{streak_str} | Pot: {pot_cards} cards ({pot_tricks} trk)"

                lines.append(f"T{t_num:02d} [{led_suit} Lead]: {cards_str:<56} {res_str}")

            # Deal Result
            res = d.get('result')
            if res:
                tw = res.get('tricks_won', {})
                cc = res.get('cards_collected', {})
                a_trks = tw.get('Team A', 0)
                b_trks = tw.get('Team B', 0)
                a_cards = cc.get('Team A', 0)
                b_cards = cc.get('Team B', 0)
                next_d_id = res.get('next_dealer', '')
                next_d_name = res.get('next_dealer_name') or p_names.get(next_d_id, next_d_id)
                next_dealer_str = f"{next_d_name} ({next_d_id})" if next_d_id else ""

                lines.append("-" * 100)
                lines.append(f"Result: Team A = {a_trks} tricks ({a_cards} cards) | Team B = {b_trks} tricks ({b_cards} cards)")
                lines.append(f"Math  : Dealer {dealer_name} ({dealer_id}) Score: {score_start} -> {res.get('dealer_score_end')} (Delta: {res.get('delta', 0):+d}) | {res.get('score_note', '')}")
                lines.append(f"Status: {res.get('rotation_status', '')} | Next Dealer: {next_dealer_str} @ {res.get('next_starting_score', 0)} pts")
            lines.append("")

        # Match summary
        stats = payload.get('stats', {})
        lines.append("=" * 100)
        lines.append("                                        MATCH SUMMARY & STATS")
        lines.append("=" * 100)
        lines.append(f"Total Deals Played : {stats.get('total_deals', 0)}")
        lines.append(f"Team A Deals Won   : {stats.get('team_a_deals_won', 0)}")
        lines.append(f"Team B Deals Won   : {stats.get('team_b_deals_won', 0)}")
        lines.append(f"Tera Challenges    : {stats.get('tera_attempts', 0)} (Success: {stats.get('tera_success', 0)})")
        lines.append(f"Double Tera Solos  : {stats.get('double_tera_attempts', 0)} (Success: {stats.get('double_tera_success', 0)})")
        lines.append("=" * 100)

        return "\n".join(lines) + "\n"

    def _update_master_indices(self):
        """Appends summary row to daily ledger and updates games_index.json."""
        # 1. Daily ledger line
        try:
            date_dir = os.path.join(self.base_dir, self.date_str)
            daily_file = os.path.join(date_dir, f"daily_ledger_{self.date_str}.txt")
            is_new = not os.path.exists(daily_file)

            with open(daily_file, 'a', encoding='utf-8') as f:
                if is_new:
                    f.write(f"DAILY MASTER LEDGER - {self.date_str}\n")
                    f.write("Time     | Game Name | Deal# | Dealer | Mode        | Trump | Winner & Tricks          | Delta | End Score | Next Dealer\n")
                    f.write("-" * 120 + "\n")

                if self.deals_history:
                    last_deal = self.deals_history[-1]
                    res = last_deal.get('result', {})
                    tw = res.get('tricks_won', {})
                    a_trks = tw.get('Team A', 0)
                    b_trks = tw.get('Team B', 0)
                    winner_str = f"Team A ({a_trks} trk)" if a_trks > b_trks else f"Team B ({b_trks} trk)"
                    trump_str = last_deal.get('hidden_trump') or last_deal.get('trump_suit') or '-'

                    now_time = datetime.now().strftime("%H:%M:%S")
                    row = f"{now_time:<8} | {self.game_name:<9} | D{last_deal.get('deal_number', 1):02d}   | {last_deal.get('dealer_id')} ({last_deal.get('dealer_team', '')[:1]}) | {last_deal.get('mode', 'Regular'):<11} | {trump_str:<5} | {winner_str:<24} | {res.get('delta', 0):+5d} | {res.get('dealer_score_end', 0):<9} | {res.get('next_dealer')} @ {res.get('next_starting_score')}\n"
                    f.write(row)
        except Exception as e:
            print(f"Error updating daily ledger: {e}")

        # 2. Master index JSON
        try:
            index_path = os.path.join(self.base_dir, "games_index.json")
            index_data = []
            if os.path.exists(index_path):
                try:
                    with open(index_path, 'r', encoding='utf-8') as f:
                        index_data = json.load(f)
                except Exception:
                    index_data = []

            # Update or append
            entry = {
                'game_name': self.game_name,
                'session_id': self.session_id,
                'date': self.date_str,
                'start_time': self.start_time.isoformat(),
                'last_updated': datetime.now().isoformat(),
                'txt_path': self.current_txt_path,
                'json_path': self.current_json_path,
                'total_deals': len(self.deals_history),
                'player_names': self.player_names,
                'stats': self._calculate_overall_stats()
            }

            # Replace existing session entry if present, else append
            existing_idx = next((i for i, item in enumerate(index_data) if item.get('session_id') == self.session_id), None)
            if existing_idx is not None:
                index_data[existing_idx] = entry
            else:
                index_data.append(entry)

            with open(index_path, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, indent=2)
        except Exception as e:
            print(f"Error updating master index: {e}")
