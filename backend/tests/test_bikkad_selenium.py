"""
Automated Selenium Test Suite for Bikkad (Flagship 4-Player Traditional Card Game).
Tests browser UI, room setup, step-by-step deal animation, vector card rendering,
trump hiding interaction, and bidding controls.
"""

import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


def test_selenium_bikkad_home_selection(driver, server_url):
    """Verifies homepage selector strip, Bikkad card selection, and 4-player setup options."""
    driver.get(server_url)
    wait = WebDriverWait(driver, 10)

    # Click Bikkad game selector card
    bikkad_card = wait.until(EC.element_to_be_clickable((By.ID, "gsel-bikkad")))
    bikkad_card.click()

    # Verify Bikkad is active
    assert "gsel-active" in bikkad_card.get_attribute("class")

    # Verify Trump Hider selector is visible
    select_hider = wait.until(EC.visibility_of_element_located((By.ID, "select-trump-hider")))
    assert select_hider.is_displayed()

    # Verify Human Count buttons exist
    assert driver.find_element(By.ID, "hcount-1").is_displayed()
    assert driver.find_element(By.ID, "hcount-2").is_displayed()

    # Select 2 Humans to reveal multi-human seat picker
    driver.find_element(By.ID, "hcount-2").click()
    spick_p2 = wait.until(EC.visibility_of_element_located((By.ID, "spick-P2")))
    assert spick_p2.is_displayed()
    assert driver.find_element(By.ID, "spick-P3").is_displayed()
    assert driver.find_element(By.ID, "spick-P4").is_displayed()


def test_selenium_bikkad_start_game_and_seats(driver, server_url):
    """Starts a Bikkad match and checks table view, 4 player seats, and pot box."""
    driver.get(server_url)
    wait = WebDriverWait(driver, 10)

    driver.find_element(By.ID, "gsel-bikkad").click()
    driver.find_element(By.ID, "btn-start-game").click()

    # Wait for Table View to activate
    table_view = wait.until(EC.visibility_of_element_located((By.ID, "view-table")))
    assert table_view.is_displayed()

    # Check 4 seats are rendered
    assert driver.find_element(By.ID, "seat-P1").is_displayed()
    assert driver.find_element(By.ID, "seat-P2").is_displayed()
    assert driver.find_element(By.ID, "seat-P3").is_displayed()
    assert driver.find_element(By.ID, "seat-P4").is_displayed()

    # Pot accumulator box and Trump slot should be present
    assert driver.find_element(By.ID, "pot-accumulator-box").is_displayed()
    assert driver.find_element(By.ID, "trump-slot").is_displayed()


def test_selenium_bikkad_card_rendering_and_interaction(driver, server_url):
    """Verifies that vector SVG playing cards are rendered in South Hand and can be hovered/interacted."""
    driver.get(server_url)
    wait = WebDriverWait(driver, 10)

    driver.find_element(By.ID, "gsel-bikkad").click()
    driver.find_element(By.ID, "btn-start-game").click()
    wait.until(EC.visibility_of_element_located((By.ID, "view-table")))

    # Wait for South hand cards to render
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#hand-P1 .card-wrapper")))
    hand_cards = driver.find_elements(By.CSS_SELECTOR, "#hand-P1 .card-wrapper")
    assert len(hand_cards) >= 5

    # Verify vector playing-card-svg img exists
    img = hand_cards[0].find_element(By.TAG_NAME, "img")
    assert "cards/" in img.get_attribute("src")


def test_selenium_bikkad_bidding_and_trump_controls(driver, server_url):
    """Tests contract bidding bar and game controls visibility."""
    driver.get(server_url)
    wait = WebDriverWait(driver, 10)

    driver.find_element(By.ID, "gsel-bikkad").click()
    driver.find_element(By.ID, "btn-start-game").click()
    wait.until(EC.visibility_of_element_located((By.ID, "view-table")))

    # Check header brand updates to BIKKAD
    header_title = driver.find_element(By.ID, "header-game-title")
    assert "BIKKAD" in header_title.get_attribute("textContent").upper()

    # Check pause bots button operates
    btn_pause = driver.find_element(By.ID, "btn-pause-bots")
    assert btn_pause.is_displayed()
    btn_pause.click()
    time.sleep(0.3)
    assert "Resume" in btn_pause.get_attribute("textContent")
    btn_pause.click()
    time.sleep(0.3)
    assert "Pause" in btn_pause.get_attribute("textContent")


def test_selenium_bikkad_contract_declaration_ui(driver, server_url):
    """Tests prominent in-hand contract bar and bidding Tera / Double Tera buttons."""
    driver.get(server_url)
    wait = WebDriverWait(driver, 10)

    driver.find_element(By.ID, "gsel-bikkad").click()
    driver.find_element(By.ID, "btn-start-game").click()
    wait.until(EC.visibility_of_element_located((By.ID, "view-table")))

    # Simulate Trick 1 state before P1 plays card
    driver.execute_script("""
        let id = window.setTimeout(function() {}, 0);
        while (id--) { window.clearTimeout(id); }
        stopAutoPlay();
        isDealingAnimationActive = false;
        renderState({
            game_id: 'test_bikkad_bid',
            mode: 'Regular',
            trick_number: 1,
            deal_stage: 'READY',
            current_trick: [],
            current_turn_player: 'P1',
            player_types: { P1: 'human', P2: 'ai', P3: 'ai', P4: 'ai' },
            player_names: { P1: 'Sagan', P2: 'G. Dinesh', P3: 'G. Bhimaram', P4: 'G. Geeta' },
            hands: {
                P1: [{ code: 'AS', suit: 'S', rank: 'A' }, { code: 'KH', suit: 'H', rank: 'K' }],
                P2: [1,2,3,4,5,6,7,8,9,10,11,12,13],
                P3: [1,2,3,4,5,6,7,8,9,10,11,12,13],
                P4: [1,2,3,4,5,6,7,8,9,10,11,12,13]
            },
            team_tricks_won: { 'Team A': 0, 'Team B': 0 },
            team_cards_collected: { 'Team A': 0, 'Team B': 0 },
            dealer_id: 'P4',
            dealer_team: 'Team B',
            dealer_score: 0,
            logs: []
        });
    """)

    # Contract bar should be visible
    contract_bar = wait.until(EC.visibility_of_element_located((By.ID, "player-contract-bar")))
    assert contract_bar.is_displayed()

    btn_tera = wait.until(EC.visibility_of_element_located((By.ID, "btn-bid-tera")))
    btn_double_tera = wait.until(EC.visibility_of_element_located((By.ID, "btn-bid-double-tera")))
    assert btn_tera.is_displayed()
    assert btn_double_tera.is_displayed()


def test_selenium_bikkad_following_suit_and_legal_cards(driver, server_url):
    """Verifies that legal cards match the led suit while non-matching cards are marked illegal."""
    driver.get(server_url)
    wait = WebDriverWait(driver, 10)

    driver.find_element(By.ID, "gsel-bikkad").click()
    driver.find_element(By.ID, "btn-start-game").click()
    wait.until(EC.visibility_of_element_located((By.ID, "view-table")))

    # Simulate Hearts led, P1 holds Hearts ('10H') and Spades ('AS')
    driver.execute_script("""
        let id = window.setTimeout(function() {}, 0);
        while (id--) { window.clearTimeout(id); }
        stopAutoPlay();
        isDealingAnimationActive = false;
        renderState({
            game_id: 'test_bikkad_rules',
            mode: 'Regular',
            trick_number: 2,
            deal_stage: 'READY',
            led_suit: 'H',
            current_trick: [{ player_id: 'P2', card: { code: 'QH', suit: 'H' } }],
            current_turn_player: 'P1',
            player_types: { P1: 'human', P2: 'ai', P3: 'ai', P4: 'ai' },
            player_names: { P1: 'Sagan', P2: 'G. Dinesh', P3: 'G. Bhimaram', P4: 'G. Geeta' },
            hands: {
                P1: [{ code: '10H', suit: 'H', rank: '10' }, { code: 'AS', suit: 'S', rank: 'A' }],
                P2: [1,2,3], P3: [1,2,3], P4: [1,2,3]
            },
            team_tricks_won: { 'Team A': 0, 'Team B': 0 },
            team_cards_collected: { 'Team A': 0, 'Team B': 0 },
            dealer_id: 'P4',
            dealer_team: 'Team B',
            dealer_score: 0,
            logs: []
        });
    """)

    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#hand-P1 .card-wrapper")))
    cards = driver.find_elements(By.CSS_SELECTOR, "#hand-P1 .card-wrapper")
    assert len(cards) == 2

    # First card (10H) should have class legal-card
    assert "legal-card" in cards[0].get_attribute("class")
    # Second card (AS) should have class illegal-card
    assert "illegal-card" in cards[1].get_attribute("class")


def test_selenium_bikkad_trump_hidden_and_reveal_flow(driver, server_url):
    """Tests hidden trump slot rendering and demand cut / reveal trigger."""
    driver.get(server_url)
    wait = WebDriverWait(driver, 10)

    driver.find_element(By.ID, "gsel-bikkad").click()
    driver.find_element(By.ID, "btn-start-game").click()
    wait.until(EC.visibility_of_element_located((By.ID, "view-table")))

    # 1. State with Hidden Trump under saucer
    driver.execute_script("""
        let id = window.setTimeout(function() {}, 0);
        while (id--) { window.clearTimeout(id); }
        stopAutoPlay();
        isDealingAnimationActive = false;
        renderState({
            game_id: 'test_bikkad_trump',
            mode: 'Regular',
            trick_number: 3,
            deal_stage: 'READY',
            led_suit: 'D',
            current_trick: [{ player_id: 'P2', card: { code: 'KD', suit: 'D' } }],
            current_turn_player: 'P1',
            player_types: { P1: 'human', P2: 'ai', P3: 'ai', P4: 'ai' },
            player_names: { P1: 'Sagan', P2: 'G. Dinesh', P3: 'G. Bhimaram', P4: 'G. Geeta' },
            hands: {
                P1: [{ code: 'AS', suit: 'S', rank: 'A' }],
                P2: [1], P3: [1], P4: [1]
            },
            hidden_trump_card: { code: '7H', suit: 'H', rank: '7' },
            trump_revealed: false,
            team_tricks_won: { 'Team A': 0, 'Team B': 0 },
            team_cards_collected: { 'Team A': 0, 'Team B': 0 },
            dealer_id: 'P4',
            dealer_team: 'Team B',
            dealer_score: 0,
            logs: []
        });
    """)

    # P1 is void in Diamonds, so btn-demand-cut must be visible
    btn_cut = wait.until(EC.visibility_of_element_located((By.ID, "btn-demand-cut")))
    assert btn_cut.is_displayed()

    # Trump slot displays HIDDEN TRUMP
    trump_label = driver.find_element(By.ID, "trump-slot-label")
    assert "HIDDEN" in trump_label.get_attribute("textContent").upper()

    # 2. Reveal Trump state
    driver.execute_script("""
        let id = window.setTimeout(function() {}, 0);
        while (id--) { window.clearTimeout(id); }
        stopAutoPlay();
        isDealingAnimationActive = false;
        renderState({
            game_id: 'test_bikkad_trump',
            mode: 'Regular',
            trick_number: 3,
            deal_stage: 'READY',
            led_suit: 'D',
            current_trick: [{ player_id: 'P2', card: { code: 'KD', suit: 'D' } }],
            current_turn_player: 'P1',
            player_types: { P1: 'human', P2: 'ai', P3: 'ai', P4: 'ai' },
            player_names: { P1: 'Sagan', P2: 'G. Dinesh', P3: 'G. Bhimaram', P4: 'G. Geeta' },
            hands: {
                P1: [{ code: 'AS', suit: 'S', rank: 'A' }],
                P2: [1], P3: [1], P4: [1]
            },
            hidden_trump_card: { code: '7H', suit: 'H', rank: '7' },
            trump_revealed: true,
            trump_suit: 'H',
            trump_opener_id: 'P1',
            trump_opener_name: 'Sagan',
            team_tricks_won: { 'Team A': 0, 'Team B': 0 },
            team_cards_collected: { 'Team A': 0, 'Team B': 0 },
            dealer_id: 'P4',
            dealer_team: 'Team B',
            dealer_score: 0,
            logs: []
        });
    """)

    # Trump slot box receives trump-revealed-active class
    trump_box = driver.find_element(By.ID, "trump-slot")
    assert "trump-revealed-active" in trump_box.get_attribute("class")

    # Trump caller badge appears
    caller_badge = wait.until(EC.visibility_of_element_located((By.ID, "trump-revealed-caller-badge")))
    assert caller_badge.is_displayed()
    assert "Sagan" in caller_badge.get_attribute("textContent")


def test_selenium_bikkad_trick_winner_and_pot_metrics(driver, server_url):
    """Verifies center trick arena cards, crown badge on winner, and pot accumulator counters."""
    driver.get(server_url)
    wait = WebDriverWait(driver, 10)

    driver.find_element(By.ID, "gsel-bikkad").click()
    driver.find_element(By.ID, "btn-start-game").click()
    wait.until(EC.visibility_of_element_located((By.ID, "view-table")))

    # Simulate completed trick with pot streak
    driver.execute_script("""
        let id = window.setTimeout(function() {}, 0);
        while (id--) { window.clearTimeout(id); }
        stopAutoPlay();
        isDealingAnimationActive = false;
        renderState({
            game_id: 'test_bikkad_pot',
            mode: 'Regular',
            trick_number: 4,
            deal_stage: 'READY',
            last_completed_trick: [
                { player_id: 'P1', card: { code: 'AH' } },
                { player_id: 'P2', card: { code: 'KH' } },
                { player_id: 'P3', card: { code: 'QH' } },
                { player_id: 'P4', card: { code: 'JH' } }
            ],
            last_trick_winner: 'P1',
            last_trick_winning_card: 'AH',
            pot_card_count: 8,
            pot_trick_count: 2,
            pot_streak_holder: 'Team A',
            pot_streak_count: 2,
            player_types: { P1: 'human', P2: 'ai', P3: 'ai', P4: 'ai' },
            player_names: { P1: 'Sagan', P2: 'G. Dinesh', P3: 'G. Bhimaram', P4: 'G. Geeta' },
            hands: { P1: [], P2: [], P3: [], P4: [] },
            team_tricks_won: { 'Team A': 2, 'Team B': 1 },
            team_cards_collected: { 'Team A': 8, 'Team B': 4 },
            dealer_id: 'P4',
            dealer_team: 'Team B',
            dealer_score: 0,
            logs: ['P1 won the trick with AH!']
        });
    """)

    # Check pot accumulator values
    pot_cards = wait.until(EC.visibility_of_element_located((By.ID, "pot-cards-val")))
    pot_tricks = wait.until(EC.visibility_of_element_located((By.ID, "pot-tricks-val")))
    assert pot_cards.get_attribute("textContent") == "8"
    assert pot_tricks.get_attribute("textContent") == "2"

    # Trick slot P1 should have winner card and crown badge
    trick_p1 = driver.find_element(By.ID, "trick-P1")
    assert "trick-winner-card" in trick_p1.get_attribute("class")
    winner_badge = trick_p1.find_element(By.CLASS_NAME, "trick-winner-badge")
    assert "WINNER" in winner_badge.get_attribute("textContent")


def test_selenium_bikkad_tera_early_fail_scenario(driver, server_url):
    """Tests Tera contract early failure: when opponents win a trick, contract fails immediately."""
    driver.get(server_url)
    wait = WebDriverWait(driver, 10)

    driver.find_element(By.ID, "gsel-bikkad").click()
    driver.find_element(By.ID, "btn-start-game").click()
    wait.until(EC.visibility_of_element_located((By.ID, "view-table")))

    # Simulate Tera contract where Team B won trick 4, causing early contract termination
    driver.execute_script("""
        let id = window.setTimeout(function() {}, 0);
        while (id--) { window.clearTimeout(id); }
        stopAutoPlay();
        isDealingAnimationActive = false;
        renderState({
            game_id: 'test_bikkad_tera_fail',
            mode: 'Tera',
            declarer_id: 'P1',
            trick_number: 4,
            round_complete: true,
            winning_team: 'Team B',
            deal_stage: 'READY',
            team_tricks_won: { 'Team A': 3, 'Team B': 1 },
            team_cards_collected: { 'Team A': 12, 'Team B': 4 },
            dealer_id: 'P4',
            dealer_team: 'Team B',
            dealer_score: 26,  // Double penalty awarded to dealer
            player_types: { P1: 'human', P2: 'ai', P3: 'ai', P4: 'ai' },
            player_names: { P1: 'Sagan', P2: 'G. Dinesh', P3: 'G. Bhimaram', P4: 'G. Geeta' },
            hands: { P1: [], P2: [], P3: [], P4: [] },
            announcement: {
                title: 'TERA CONTRACT FAILED!',
                sub: 'Opponents won a trick! Team B receives 26 points penalty.'
            },
            logs: ['🚨 TERA CONTRACT FAILED! P2 won Trick 4!']
        });
    """)

    # Announcement banner should announce Tera contract failed
    announcement = wait.until(EC.visibility_of_element_located((By.ID, "game-announcement-banner")))
    assert announcement.is_displayed()
    title_el = driver.find_element(By.ID, "announcement-title")
    assert "FAILED" in title_el.get_attribute("textContent").upper()

    # Turn badge should indicate deal winning team
    turn_badge = driver.find_element(By.ID, "turn-badge")
    assert "Won" in turn_badge.get_attribute("textContent")


def test_selenium_bikkad_double_tera_solo_mode_scenario(driver, server_url):
    """Tests Double Tera mode: P1 plays solo against 2 opponents, while partner P3 sits out."""
    driver.get(server_url)
    wait = WebDriverWait(driver, 10)

    driver.find_element(By.ID, "gsel-bikkad").click()
    driver.find_element(By.ID, "btn-start-game").click()
    wait.until(EC.visibility_of_element_located((By.ID, "view-table")))

    # Simulate Double Tera contract where P3 sits out
    driver.execute_script("""
        let id = window.setTimeout(function() {}, 0);
        while (id--) { window.clearTimeout(id); }
        stopAutoPlay();
        isDealingAnimationActive = false;
        renderState({
            game_id: 'test_bikkad_double_tera',
            mode: 'Double Tera',
            declarer_id: 'P1',
            trick_number: 1,
            deal_stage: 'READY',
            active_players: ['P1', 'P2', 'P4'],  // P3 sits out in solo mode
            current_turn_player: 'P1',
            team_tricks_won: { 'Team A': 0, 'Team B': 0 },
            team_cards_collected: { 'Team A': 0, 'Team B': 0 },
            dealer_id: 'P4',
            dealer_team: 'Team B',
            dealer_score: 0,
            player_types: { P1: 'human', P2: 'ai', P3: 'ai', P4: 'ai' },
            player_names: { P1: 'Sagan', P2: 'G. Dinesh', P3: 'G. Bhimaram', P4: 'G. Geeta' },
            hands: {
                P1: [{ code: 'AS', suit: 'S', rank: 'A' }],
                P2: [1], P3: [], P4: [1]
            },
            logs: ['👑 Sagan declared DOUBLE TERA! Sagan plays solo alone!']
        });
    """)

    # North seat (P3) should have sits-out role badge
    p3_seat = wait.until(EC.presence_of_element_located((By.ID, "seat-P3")))
    assert "is-sitting-out" in p3_seat.get_attribute("class")
    sits_out_tag = p3_seat.find_element(By.CLASS_NAME, "badge-sits-out")
    assert "SITS OUT" in sits_out_tag.get_attribute("textContent").upper()


def test_selenium_bikkad_ladder_52_points_match_victory(driver, server_url):
    """Tests ladder progression to 52/52 points and match win state."""
    driver.get(server_url)
    wait = WebDriverWait(driver, 10)

    driver.find_element(By.ID, "gsel-bikkad").click()
    driver.find_element(By.ID, "btn-start-game").click()
    wait.until(EC.visibility_of_element_located((By.ID, "view-table")))

    # Simulate 52 points reached by dealer
    driver.execute_script("""
        let id = window.setTimeout(function() {}, 0);
        while (id--) { window.clearTimeout(id); }
        stopAutoPlay();
        isDealingAnimationActive = false;
        renderState({
            game_id: 'test_bikkad_win52',
            mode: 'Regular',
            round_complete: true,
            winning_team: 'Team A',
            dealer_id: 'P1',
            dealer_team: 'Team A',
            dealer_score: 52,
            team_tricks_won: { 'Team A': 8, 'Team B': 5 },
            team_cards_collected: { 'Team A': 32, 'Team B': 20 },
            player_types: { P1: 'human', P2: 'ai', P3: 'ai', P4: 'ai' },
            player_names: { P1: 'Sagan', P2: 'G. Dinesh', P3: 'G. Bhimaram', P4: 'G. Geeta' },
            hands: { P1: [], P2: [], P3: [], P4: [] },
            logs: ['🏆 MATCH WON! Dealer Sagan reached 52 points!']
        });
    """)

    # Scoreboard ladder should display 52 / 52
    ladder_score = wait.until(EC.visibility_of_element_located((By.ID, "ladder-score")))
    assert "52 / 52" in ladder_score.get_attribute("textContent")
    ladder_fill = driver.find_element(By.ID, "ladder-fill")
    assert "100%" in ladder_fill.get_attribute("style")
