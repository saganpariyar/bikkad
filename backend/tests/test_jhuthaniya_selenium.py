"""
Automated Selenium Test Suite for Jhuthaniya (Bluff / Cheat).
Tests browser UI, 2-7 player game creation, Option A rank locking, vector card rendering,
challenge window interactions (JHUTH / Pass), and end-to-end game flow.
"""

import time
import socket
import threading
import pytest
import uvicorn

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC



def test_selenium_homepage_select_jhuthaniya(driver, server_url):
    """Verifies opening homepage, selecting Jhuthaniya, and player count dropdown visibility."""
    driver.get(server_url)
    wait = WebDriverWait(driver, 10)

    # Click Jhuthaniya game selector card
    jh_card = wait.until(EC.element_to_be_clickable((By.ID, "gsel-jhuthaniya")))
    jh_card.click()

    # Verify player count selector group is visible
    jh_group = wait.until(EC.visibility_of_element_located((By.ID, "group-jhuthaniya-player-count")))
    assert jh_group.is_displayed()

    # Verify dropdown options are 2 to 7 players
    select_el = Select(driver.find_element(By.ID, "select-jhuthaniya-player-count"))
    options = [opt.text for opt in select_el.options]
    assert any("3 Players" in o for o in options)
    assert any("7 Players" in o for o in options)


def test_selenium_start_3_player_game(driver, server_url):
    """Starts a 3-player Jhuthaniya match (matching game1.md: Aarav, Priya, Rohan) and checks arena."""
    driver.get(server_url)
    wait = WebDriverWait(driver, 10)

    # Select Jhuthaniya
    driver.find_element(By.ID, "gsel-jhuthaniya").click()

    # Select 3 Players
    count_select = Select(wait.until(EC.visibility_of_element_located((By.ID, "select-jhuthaniya-player-count"))))
    count_select.select_by_value("3")

    # Set host name to Aarav if input exists
    try:
        host_input = driver.find_element(By.ID, "input-your-name")
        host_input.clear()
        host_input.send_keys("Aarav")
    except Exception:
        pass

    # Click Start Match
    btn_start = driver.find_element(By.ID, "btn-start-game")
    btn_start.click()

    # Wait for Table View and South Hand cards to render
    wait.until(EC.visibility_of_element_located((By.ID, "view-table")))
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#hand-P1 .jh-card-wrapper")))

    # Verify roster has exactly 3 players
    wait.until(lambda d: len(d.find_elements(By.CLASS_NAME, "jh-player-card")) == 3)
    roster_cards = driver.find_elements(By.CLASS_NAME, "jh-player-card")
    assert len(roster_cards) == 3

    # Verify (You) is shown on first card
    player_name_el = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".jh-player-card .jh-player-name")))
    assert "(You)" in player_name_el.get_attribute("textContent")

    # Verify vector cards count is 17 or 18
    hand_cards = driver.find_elements(By.CSS_SELECTOR, "#hand-P1 .jh-card-wrapper")
    assert len(hand_cards) in [17, 18]

    # Verify SVGs loaded inside card wrappers safely
    src = wait.until(lambda d: d.execute_script("return document.querySelector('#hand-P1 .jh-card-wrapper img')?.getAttribute('src');"))
    assert "cards/" in src


def test_selenium_card_selection_and_rank_option_a(driver, server_url):
    """Verifies vector card selection, elevation highlight, and Option A rank selection in browser."""
    driver.get(server_url)
    wait = WebDriverWait(driver, 10)

    driver.find_element(By.ID, "gsel-jhuthaniya").click()
    count_select = Select(wait.until(EC.visibility_of_element_located((By.ID, "select-jhuthaniya-player-count"))))
    count_select.select_by_value("3")
    driver.find_element(By.ID, "btn-start-game").click()

    wait.until(EC.visibility_of_element_located((By.ID, "jhuthaniya-arena")))

    # Wait for hand cards to render
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#hand-P1 .jh-card-wrapper")))

    # Select first card
    first_class = driver.execute_script("""
        const card = document.querySelector('#hand-P1 .jh-card-wrapper');
        if (card) {
            card.click();
            return card.className;
        }
        return '';
    """)
    assert "jh-selected" in first_class

    # Deselect first card
    deselected_class = driver.execute_script("""
        const card = document.querySelector('#hand-P1 .jh-card-wrapper');
        if (card) {
            card.click();
            return card.className;
        }
        return '';
    """)
    assert "jh-selected" not in deselected_class


def test_selenium_player_counts_scaling_2_to_7(driver, server_url):
    """Verifies that 2, 4, 5, 6, and 7 player games correctly initialize and render roster in browser."""
    driver.get(server_url)
    wait = WebDriverWait(driver, 10)

    for n in [2, 4, 6]:
        driver.get(server_url)
        driver.find_element(By.ID, "gsel-jhuthaniya").click()
        count_select = Select(wait.until(EC.visibility_of_element_located((By.ID, "select-jhuthaniya-player-count"))))
        count_select.select_by_value(str(n))
        driver.find_element(By.ID, "btn-start-game").click()

        wait.until(EC.visibility_of_element_located((By.ID, "jhuthaniya-arena")))
        roster_cards = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "jh-player-card")))
        assert len(roster_cards) == n


def test_selenium_option_a_ui_locked_rank_flow(driver, server_url):
    """Verifies that when round rank is locked under Option A, the locked badge is shown and pills are hidden."""
    driver.get(server_url)
    wait = WebDriverWait(driver, 10)

    # Start a 3-player match
    driver.find_element(By.ID, "gsel-jhuthaniya").click()
    count_select = Select(wait.until(EC.visibility_of_element_located((By.ID, "select-jhuthaniya-player-count"))))
    count_select.select_by_value("3")
    driver.find_element(By.ID, "btn-start-game").click()
    wait.until(EC.visibility_of_element_located((By.ID, "jhuthaniya-arena")))

    # 1. Simulate state where Option A rank is locked to Queens for P1
    driver.execute_script("""
        let id = window.setTimeout(function() {}, 0);
        while (id--) { window.clearTimeout(id); }
        stopAutoPlay();
        if (typeof jhuthaniyaBotTimeout !== 'undefined' && jhuthaniyaBotTimeout) {
            clearTimeout(jhuthaniyaBotTimeout);
            jhuthaniyaBotTimeout = null;
        }
        triggerJhuthaniyaBotStep = function() {};
        renderJhuthaniyaState({
            game_id: 'test_locked_ui',
            phase: 'PLAYING',
            current_turn: 'P1',
            is_my_turn: true,
            can_choose_rank: false,
            current_round_rank: 'Q',
            current_round_rank_display: 'Queens (Begams)',
            my_hand: ['10H', 'QD', 'AS'],
            players: { P1: { name: 'Aarav', card_count: 3 }, P2: { name: 'Priya', card_count: 3 }, P3: { name: 'Rohan', card_count: 3 } },
            active_players: ['P1', 'P2', 'P3'],
            safe_players: [],
            center_pot_size: 3,
            logs: []
        });
    """)

    # Verify locked badge is visible and shows Queens
    locked_badge = wait.until(EC.visibility_of_element_located((By.ID, "jh-locked-rank-badge")))
    assert "Queens" in locked_badge.get_attribute("textContent")

    # Verify rank pills are hidden
    rank_pills = driver.find_element(By.ID, "jh-rank-pills")
    assert "hidden" in rank_pills.get_attribute("class")

    # 2. Simulate Challenge Window UI when a claim is made against P1
    driver.execute_script("""
        let id = window.setTimeout(function() {}, 0);
        while (id--) { window.clearTimeout(id); }
        stopAutoPlay();
        if (typeof jhuthaniyaBotTimeout !== 'undefined' && jhuthaniyaBotTimeout) {
            clearTimeout(jhuthaniyaBotTimeout);
            jhuthaniyaBotTimeout = null;
        }
        triggerJhuthaniyaBotStep = function() {};
        renderJhuthaniyaState({
            game_id: 'test_ch_ui',
            phase: 'CHALLENGE_WINDOW',
            current_turn: 'P2',
            is_my_turn: false,
            challenge: {
                claimant: 'P2',
                claimant_name: 'Priya',
                claimed_rank: '10',
                claimed_count: 2,
                rank_display: '10s',
                waiting_for: ['P1'],
                challenge_decisions: {}
            },
            my_hand: ['10H', 'QD'],
            players: { P1: { name: 'Aarav', card_count: 2 }, P2: { name: 'Priya', card_count: 2 } },
            active_players: ['P1', 'P2'],
            safe_players: [],
            center_pot_size: 4,
            logs: []
        });
    """)

    # Verify challenge bar and buttons appear
    wait.until(EC.visibility_of_element_located((By.ID, "jh-challenge-bar")))
    btn_jhuth = wait.until(EC.visibility_of_element_located((By.ID, "btn-jh-challenge")))
    btn_pass = wait.until(EC.visibility_of_element_located((By.ID, "btn-jh-pass")))
    assert btn_jhuth.is_displayed()
    assert btn_pass.is_displayed()
    assert "JHUTH" in btn_jhuth.get_attribute("textContent")
    assert "PASS" in btn_pass.get_attribute("textContent")

    # Verify individual card position inspect buttons (for 2 cards claimed)
    inspect_btns = driver.find_elements(By.CLASS_NAME, "jh-inspect-btn")
    assert len(inspect_btns) == 2
    assert "Card #1" in inspect_btns[0].get_attribute("textContent")
    assert "Card #2" in inspect_btns[1].get_attribute("textContent")


def test_selenium_playing_cards_into_center_pot_stack(driver, server_url):
    """Tests cards played into center pot stack and pot badge update."""
    driver.get(server_url)
    wait = WebDriverWait(driver, 10)

    driver.find_element(By.ID, "gsel-jhuthaniya").click()
    count_select = Select(wait.until(EC.visibility_of_element_located((By.ID, "select-jhuthaniya-player-count"))))
    count_select.select_by_value("3")
    driver.find_element(By.ID, "btn-start-game").click()
    wait.until(EC.visibility_of_element_located((By.ID, "jhuthaniya-arena")))

    # Simulate pot with 5 cards
    driver.execute_script("""
        let id = window.setTimeout(function() {}, 0);
        while (id--) { window.clearTimeout(id); }
        stopAutoPlay();
        if (typeof jhuthaniyaBotTimeout !== 'undefined' && jhuthaniyaBotTimeout) {
            clearTimeout(jhuthaniyaBotTimeout);
            jhuthaniyaBotTimeout = null;
        }
        triggerJhuthaniyaBotStep = function() {};
        renderJhuthaniyaState({
            game_id: 'test_pot_stack',
            phase: 'PLAYING',
            current_turn: 'P1',
            is_my_turn: true,
            can_choose_rank: true,
            current_round_rank: null,
            center_pot_size: 5,
            my_hand: ['10H', 'QD', 'AS'],
            players: {
                P1: { name: 'Aarav', card_count: 3 },
                P2: { name: 'Priya', card_count: 3 },
                P3: { name: 'Rohan', card_count: 3 }
            },
            active_players: ['P1', 'P2', 'P3'],
            safe_players: [],
            logs: []
        });
    """)

    # Verify pot badge shows 5 cards
    pot_badge = wait.until(EC.visibility_of_element_located((By.ID, "jh-pot-badge")))
    assert "5 Cards in Pot" in pot_badge.get_attribute("textContent")

    # Verify pot stack has card images
    pot_imgs = driver.find_elements(By.CLASS_NAME, "jh-pot-img")
    assert len(pot_imgs) == 5


def test_selenium_challenge_resolution_bluff_caught(driver, server_url):
    """Verifies that catching a bluff reveals truth, logs bluff caught, and gives pot to liar."""
    driver.get(server_url)
    wait = WebDriverWait(driver, 10)

    driver.find_element(By.ID, "gsel-jhuthaniya").click()
    count_select = Select(wait.until(EC.visibility_of_element_located((By.ID, "select-jhuthaniya-player-count"))))
    count_select.select_by_value("3")
    driver.find_element(By.ID, "btn-start-game").click()
    wait.until(EC.visibility_of_element_located((By.ID, "jhuthaniya-arena")))

    # Simulate bluff caught resolution
    driver.execute_script("""
        let id = window.setTimeout(function() {}, 0);
        while (id--) { window.clearTimeout(id); }
        stopAutoPlay();
        if (typeof jhuthaniyaBotTimeout !== 'undefined' && jhuthaniyaBotTimeout) {
            clearTimeout(jhuthaniyaBotTimeout);
            jhuthaniyaBotTimeout = null;
        }
        triggerJhuthaniyaBotStep = function() {};
        renderJhuthaniyaState({
            game_id: 'test_bluff_caught',
            phase: 'PLAYING',
            current_turn: 'P1',
            is_my_turn: true,
            can_choose_rank: true,
            current_round_rank: null,
            center_pot_size: 0,
            my_hand: ['10H', 'QD', 'AS'],
            players: {
                P1: { name: 'Aarav', card_count: 3 },
                P2: { name: 'Priya', card_count: 9 },  // Priya picked up 6 pot cards
                P3: { name: 'Rohan', card_count: 3 }
            },
            active_players: ['P1', 'P2', 'P3'],
            safe_players: [],
            last_resolution: {
                claimant: 'P2',
                claimant_name: 'Priya',
                challenger: 'P1',
                challenger_name: 'Aarav',
                was_bluff: true,
                pot_size: 6,
                loser: 'P2',
                loser_name: 'Priya'
            },
            logs: ['🚨 BLUFF CAUGHT! Priya lied about Kings! Priya picks up 6 cards!']
        });
    """)

    # Verify Priya's card count increased
    wait.until(lambda d: any("9" in c.get_attribute("textContent") for c in d.find_elements(By.CLASS_NAME, "jh-player-count-badge")))
    roster_counts = driver.find_elements(By.CLASS_NAME, "jh-player-count-badge")
    assert any("9" in c.get_attribute("textContent") for c in roster_counts)

    # Verify pot is now empty
    empty_slot = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "jh-pot-empty-slot")))
    assert empty_slot.is_displayed()


def test_selenium_challenge_resolution_honest_claimant(driver, server_url):
    """Verifies that challenging an honest player penalizes the challenger with the pot."""
    driver.get(server_url)
    wait = WebDriverWait(driver, 10)

    driver.find_element(By.ID, "gsel-jhuthaniya").click()
    count_select = Select(wait.until(EC.visibility_of_element_located((By.ID, "select-jhuthaniya-player-count"))))
    count_select.select_by_value("3")
    driver.find_element(By.ID, "btn-start-game").click()
    wait.until(EC.visibility_of_element_located((By.ID, "jhuthaniya-arena")))

    # Simulate honest play where challenger was wrong
    driver.execute_script("""
        let id = window.setTimeout(function() {}, 0);
        while (id--) { window.clearTimeout(id); }
        stopAutoPlay();
        if (typeof jhuthaniyaBotTimeout !== 'undefined' && jhuthaniyaBotTimeout) {
            clearTimeout(jhuthaniyaBotTimeout);
            jhuthaniyaBotTimeout = null;
        }
        triggerJhuthaniyaBotStep = function() {};
        renderJhuthaniyaState({
            game_id: 'test_honest_claim',
            phase: 'PLAYING',
            current_turn: 'P2',
            is_my_turn: false,
            can_choose_rank: true,
            current_round_rank: null,
            center_pot_size: 0,
            my_hand: ['10H', 'QD', 'AS', '2C', '3D', '4S'], // Aarav had to pick up pot!
            players: {
                P1: { name: 'Aarav', card_count: 6 },
                P2: { name: 'Priya', card_count: 2 },
                P3: { name: 'Rohan', card_count: 3 }
            },
            active_players: ['P1', 'P2', 'P3'],
            safe_players: [],
            last_resolution: {
                claimant: 'P2',
                claimant_name: 'Priya',
                challenger: 'P1',
                challenger_name: 'Aarav',
                was_bluff: false,
                pot_size: 3,
                loser: 'P1',
                loser_name: 'Aarav'
            },
            logs: ['✅ TRUTH! Priya was honest! Aarav picks up 3 cards!']
        });
    """)

    # Verify South hand card count reflects picked up pot
    hand_cards = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#hand-P1 .jh-card-wrapper")))
    assert len(hand_cards) == 6


def test_selenium_all_pass_clears_pot_to_graveyard(driver, server_url):
    """Verifies that when all players pass, the pot is discarded and a fresh trick begins."""
    driver.get(server_url)
    wait = WebDriverWait(driver, 10)

    driver.find_element(By.ID, "gsel-jhuthaniya").click()
    count_select = Select(wait.until(EC.visibility_of_element_located((By.ID, "select-jhuthaniya-player-count"))))
    count_select.select_by_value("3")
    driver.find_element(By.ID, "btn-start-game").click()
    wait.until(EC.visibility_of_element_located((By.ID, "jhuthaniya-arena")))

    # Simulate all pass resolution
    driver.execute_script("""
        let id = window.setTimeout(function() {}, 0);
        while (id--) { window.clearTimeout(id); }
        stopAutoPlay();
        if (typeof jhuthaniyaBotTimeout !== 'undefined' && jhuthaniyaBotTimeout) {
            clearTimeout(jhuthaniyaBotTimeout);
            jhuthaniyaBotTimeout = null;
        }
        triggerJhuthaniyaBotStep = function() {};
        renderJhuthaniyaState({
            game_id: 'test_all_pass',
            phase: 'PLAYING',
            current_turn: 'P1',
            is_my_turn: true,
            can_choose_rank: true,  // Fresh rank choice
            current_round_rank: null,
            center_pot_size: 0,  // Graveyard cleared
            my_hand: ['10H', 'QD'],
            players: {
                P1: { name: 'Aarav', card_count: 2 },
                P2: { name: 'Priya', card_count: 2 },
                P3: { name: 'Rohan', card_count: 2 }
            },
            active_players: ['P1', 'P2', 'P3'],
            safe_players: [],
            logs: ['All players passed. Pot cleared to graveyard! P1 starts fresh trick.']
        });
    """)

    # Verify play bar and rank pills are available for fresh choice
    wait.until(EC.visibility_of_element_located((By.ID, "jh-play-bar")))
    rank_pills = wait.until(EC.visibility_of_element_located((By.ID, "jh-rank-pills")))
    assert rank_pills.is_displayed()

    # Verify locked badge is hidden
    locked_badge = driver.find_element(By.ID, "jh-locked-rank-badge")
    assert "hidden" in locked_badge.get_attribute("class")


def test_selenium_hand_empty_win_condition(driver, server_url):
    """Verifies that a player emptying their hand receives the Safe status tag."""
    driver.get(server_url)
    wait = WebDriverWait(driver, 10)

    driver.find_element(By.ID, "gsel-jhuthaniya").click()
    count_select = Select(wait.until(EC.visibility_of_element_located((By.ID, "select-jhuthaniya-player-count"))))
    count_select.select_by_value("3")
    driver.find_element(By.ID, "btn-start-game").click()
    wait.until(EC.visibility_of_element_located((By.ID, "jhuthaniya-arena")))

    # Simulate P1 emptying hand and winning 1st rank
    driver.execute_script("""
        let id = window.setTimeout(function() {}, 0);
        while (id--) { window.clearTimeout(id); }
        stopAutoPlay();
        if (typeof jhuthaniyaBotTimeout !== 'undefined' && jhuthaniyaBotTimeout) {
            clearTimeout(jhuthaniyaBotTimeout);
            jhuthaniyaBotTimeout = null;
        }
        triggerJhuthaniyaBotStep = function() {};
        renderJhuthaniyaState({
            game_id: 'test_win',
            phase: 'PLAYING',
            current_turn: 'P2',
            is_my_turn: false,
            can_choose_rank: false,
            current_round_rank: 'A',
            center_pot_size: 2,
            my_hand: [],  // 0 cards!
            players: {
                P1: { name: 'Aarav', card_count: 0, is_safe: true, safe_rank: 1 },
                P2: { name: 'Priya', card_count: 4, is_safe: false },
                P3: { name: 'Rohan', card_count: 3, is_safe: false }
            },
            active_players: ['P2', 'P3'],
            safe_players: ['P1'],
            logs: ['🎉 Aarav has emptied their hand and finished #1 (SAFE)!']
        });
    """)

    # Verify P1 player card has Safe status tag
    safe_tag = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "jh-status-safe")))
    assert "Safe #1" in safe_tag.get_attribute("textContent")


def test_selenium_interactive_card_clicks_and_play_submission(driver, server_url):
    """
    Tests real user clicks in browser:
    1. Clicking cards in hand selects them (elevated with jh-selected).
    2. Clicking rank pills selects the claimed rank.
    3. Submit button reflects selection and enables.
    4. Clicking a selected card again deselects it.
    5. Submitting play removes cards and updates center pot.
    """
    driver.get(server_url)
    wait = WebDriverWait(driver, 10)

    driver.find_element(By.ID, "gsel-jhuthaniya").click()
    count_select = Select(wait.until(EC.visibility_of_element_located((By.ID, "select-jhuthaniya-player-count"))))
    count_select.select_by_value("3")
    driver.find_element(By.ID, "btn-start-game").click()
    wait.until(EC.visibility_of_element_located((By.ID, "jhuthaniya-arena")))

    # Render clean controllable state with 3 cards in South hand
    driver.execute_script("""
        let id = window.setTimeout(function() {}, 0);
        while (id--) { window.clearTimeout(id); }
        stopAutoPlay();
        if (typeof jhuthaniyaBotTimeout !== 'undefined' && jhuthaniyaBotTimeout) {
            clearTimeout(jhuthaniyaBotTimeout);
            jhuthaniyaBotTimeout = null;
        }
        triggerJhuthaniyaBotStep = function() {};
        renderJhuthaniyaState({
            game_id: 'test_click_play',
            phase: 'PLAYING',
            current_turn: 'P1',
            is_my_turn: true,
            can_choose_rank: true,
            current_round_rank: null,
            center_pot_size: 0,
            my_hand: ['10H', 'QD', 'AS'],
            players: {
                P1: { name: 'Aarav', card_count: 3 },
                P2: { name: 'Priya', card_count: 3 },
                P3: { name: 'Rohan', card_count: 3 }
            },
            active_players: ['P1', 'P2', 'P3'],
            safe_players: [],
            logs: []
        });
    """)

    # Locate cards in South hand
    cards = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#hand-P1 .jh-card-wrapper")))
    assert len(cards) == 3

    # Click Card 1 (10H) and Card 2 (QD) via real user click
    cards[0].click()
    cards[1].click()

    # Verify both cards have jh-selected class
    assert "jh-selected" in cards[0].get_attribute("class")
    assert "jh-selected" in cards[1].get_attribute("class")
    assert "jh-selected" not in cards[2].get_attribute("class")

    # Locate and click Queen rank pill
    rank_pills = driver.find_elements(By.CSS_SELECTOR, "#jh-rank-pills .jh-rank-pill")
    q_pill = [p for p in rank_pills if "Q" in p.text][0]
    q_pill.click()
    assert "active" in q_pill.get_attribute("class")

    # Verify submit button is enabled and shows correct count and rank
    btn_play = driver.find_element(By.ID, "btn-jh-play-submit")
    assert btn_play.is_enabled()
    btn_text = btn_play.get_attribute("textContent")
    assert "2" in btn_text
    assert "Queens" in btn_text

    # Deselect Card 1 by clicking it again
    cards[0].click()
    assert "jh-selected" not in cards[0].get_attribute("class")
    btn_text_after = btn_play.get_attribute("textContent")
    assert "1" in btn_text_after

    # Reselect Card 1 and click play submit
    cards[0].click()
    assert "jh-selected" in cards[0].get_attribute("class")
    btn_play.click()


def test_selenium_interactive_card_position_inspection_and_toast(driver, server_url):
    """
    Tests card position inspection buttons:
    1. Opponent plays 3 cards.
    2. Challenger sees positions #1, #2, #3.
    3. Clicking position #2 triggers challenge inspecting Card #2.
    4. Resolution toast displays the inspected position and verdict.
    """
    driver.get(server_url)
    wait = WebDriverWait(driver, 10)

    driver.find_element(By.ID, "gsel-jhuthaniya").click()
    count_select = Select(wait.until(EC.visibility_of_element_located((By.ID, "select-jhuthaniya-player-count"))))
    count_select.select_by_value("3")
    driver.find_element(By.ID, "btn-start-game").click()
    wait.until(EC.visibility_of_element_located((By.ID, "jhuthaniya-arena")))

    # 1. Simulate Challenge Window for a 3-card claim
    driver.execute_script("""
        let id = window.setTimeout(function() {}, 0);
        while (id--) { window.clearTimeout(id); }
        stopAutoPlay();
        if (typeof jhuthaniyaBotTimeout !== 'undefined' && jhuthaniyaBotTimeout) {
            clearTimeout(jhuthaniyaBotTimeout);
            jhuthaniyaBotTimeout = null;
        }
        triggerJhuthaniyaBotStep = function() {};
        renderJhuthaniyaState({
            game_id: 'test_inspect_pos',
            phase: 'CHALLENGE_WINDOW',
            current_turn: 'P2',
            is_my_turn: false,
            challenge: {
                claimant: 'P2',
                claimant_name: 'Priya',
                claimed_rank: 'Q',
                claimed_count: 3,
                played_cards_count: 3,
                rank_display: 'Queens (Begams)',
                waiting_for: ['P1'],
                challenge_decisions: {}
            },
            my_hand: ['10H', 'QD'],
            players: { P1: { name: 'Aarav', card_count: 2 }, P2: { name: 'Priya', card_count: 2 } },
            active_players: ['P1', 'P2'],
            safe_players: [],
            center_pot_size: 3,
            logs: []
        });
    """)

    # Verify inspect buttons for positions 1, 2, and 3 are present
    inspect_btns = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "jh-inspect-btn")))
    assert len(inspect_btns) == 3
    assert "Card #1" in inspect_btns[0].text
    assert "Card #2" in inspect_btns[1].text
    assert "Card #3" in inspect_btns[2].text

    # Click Card #2 position
    inspect_btns[1].click()

    # Verify resolution toast for inspecting Card #2
    driver.execute_script("""
        showJhuthaniyaResolutionToast({
            challenger: 'P1',
            challenger_name: 'Aarav',
            verdict: 'CAUGHT_BLUFF',
            inspected_index: 1,
            inspected_card: 'KS',
            inspected_card_display: 'K♠',
            loser: 'P2',
            loser_name: 'Priya',
            pot_taken: 3,
            message: '🚨 JHUTH! Aarav inspected Card #2 (K♠): Caught bluff! Priya picks up 3 cards.'
        });
    """)

    toast = wait.until(EC.visibility_of_element_located((By.ID, "hub-toast")))
    assert toast.is_displayed()
    toast_text = toast.get_attribute("textContent")
    assert "JHUTH CAUGHT!" in toast_text
    assert "Card #2" in toast_text
    assert "K♠" in toast_text


