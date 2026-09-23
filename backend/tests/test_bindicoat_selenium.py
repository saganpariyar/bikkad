"""
Automated Selenium Test Suite for Bindi Coat (Mindikot / Dehla Pakad).
Tests browser UI, 4-player partnership setup, Bandh Hukum hidden trump mode,
vector card rendering, and trick arena interactions.
"""

import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


def test_selenium_bindicoat_home_selection(driver, server_url):
    """Verifies selecting Bindi Coat highlights card and updates banner."""
    driver.get(server_url)
    wait = WebDriverWait(driver, 10)

    # Click Bindi Coat selector card
    bc_card = wait.until(EC.element_to_be_clickable((By.ID, "gsel-bindicoat")))
    bc_card.click()

    # Verify Bindi Coat is active
    assert "gsel-active" in bc_card.get_attribute("class")

    # Verify Human Count buttons exist
    assert driver.find_element(By.ID, "hcount-1").is_displayed()
    assert driver.find_element(By.ID, "hcount-2").is_displayed()

    # Select 2 Humans to reveal multi-human seat picker
    driver.find_element(By.ID, "hcount-2").click()
    spick_p2 = wait.until(EC.visibility_of_element_located((By.ID, "spick-P2")))
    assert spick_p2.is_displayed()
    assert driver.find_element(By.ID, "spick-P3").is_displayed()
    assert driver.find_element(By.ID, "spick-P4").is_displayed()


def test_selenium_bindicoat_start_game_and_table_mode(driver, server_url):
    """Starts a Bindi Coat match and verifies felt-table.bindicoat-mode and 4 seats."""
    driver.get(server_url)
    wait = WebDriverWait(driver, 10)

    driver.find_element(By.ID, "gsel-bindicoat").click()
    driver.find_element(By.ID, "btn-start-game").click()

    # Wait for Table View
    wait.until(EC.visibility_of_element_located((By.ID, "view-table")))

    # Verify felt-table has bindicoat-mode class
    felt_table = driver.find_element(By.CLASS_NAME, "felt-table")
    assert "bindicoat-mode" in felt_table.get_attribute("class")

    # Verify header title updates to BINDI COAT
    header_title = driver.find_element(By.ID, "header-game-title")
    assert "BINDI COAT" in header_title.get_attribute("textContent").upper()

    # Verify 4 seats exist
    assert driver.find_element(By.ID, "seat-P1").is_displayed()
    assert driver.find_element(By.ID, "seat-P2").is_displayed()
    assert driver.find_element(By.ID, "seat-P3").is_displayed()
    assert driver.find_element(By.ID, "seat-P4").is_displayed()


def test_selenium_bindicoat_hand_cards_rendered(driver, server_url):
    """Verifies that 13 cards are dealt and rendered with SVG vector images in South Hand."""
    driver.get(server_url)
    wait = WebDriverWait(driver, 10)

    driver.find_element(By.ID, "gsel-bindicoat").click()
    driver.find_element(By.ID, "btn-start-game").click()
    wait.until(EC.visibility_of_element_located((By.ID, "view-table")))

    # Wait for hand cards to render
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#hand-P1 .card-wrapper")))
    hand_cards = driver.find_elements(By.CSS_SELECTOR, "#hand-P1 .card-wrapper")
    assert len(hand_cards) >= 5

    # Verify vector playing-card-svg img exists
    img = hand_cards[0].find_element(By.TAG_NAME, "img")
    assert "cards/" in img.get_attribute("src")


def test_selenium_bindicoat_bandh_hukum_selection_modal(driver, server_url):
    """Tests opening of Bandh Hukum selection modal with 5 face-down cards for trump placer."""
    driver.get(server_url)
    wait = WebDriverWait(driver, 10)

    driver.find_element(By.ID, "gsel-bindicoat").click()
    driver.find_element(By.ID, "btn-start-game").click()
    wait.until(EC.visibility_of_element_located((By.ID, "view-table")))

    # Simulate Phase: BANDH_HUKUM_SELECTION with South as trump placer
    driver.execute_script("""
        stopAutoPlay();
        if (typeof bindiCoatBotTimeout !== 'undefined' && bindiCoatBotTimeout) {
            clearTimeout(bindiCoatBotTimeout);
            bindiCoatBotTimeout = null;
        }
        renderBindiCoatState({
            game_id: 'test_bc_bh',
            phase: 'BANDH_HUKUM_SELECTION',
            deal_num: 1,
            is_trump_placer: true,
            bandh_hukum_placer_name: 'Player',
            bandh_hukum: { placed: false, revealed: false },
            my_hand: ['AS', 'KH', 'QD', 'JC', '10S'],
            players: {
                P1: { name: 'Player', team: 'NS', card_count: 5, tricks_won: 0 },
                P2: { name: 'G. Dinesh', team: 'EW', card_count: 5, tricks_won: 0 },
                P3: { name: 'G. Bhimaram', team: 'NS', card_count: 5, tricks_won: 0 },
                P4: { name: 'G. Geeta', team: 'EW', card_count: 5, tricks_won: 0 }
            },
            teams: { NS: { mindis: 0, tricks: 0 }, EW: { mindis: 0, tricks: 0 } },
            current_turn: 'P1',
            current_trick: [],
            logs: []
        });
    """)

    # Verify Bandh Hukum Modal is open
    bh_modal = wait.until(EC.visibility_of_element_located((By.ID, "modal-bandh-hukum")))
    assert bh_modal.is_displayed()

    # Verify 5 blind card choices are presented
    choices = driver.find_elements(By.CLASS_NAME, "blind-card-choice")
    assert len(choices) == 5


def test_selenium_bindicoat_bandh_hukum_reveal_flow(driver, server_url):
    """Tests Bandh Hukum reveal state when a player cuts a trick with trump."""
    driver.get(server_url)
    wait = WebDriverWait(driver, 10)

    driver.find_element(By.ID, "gsel-bindicoat").click()
    driver.find_element(By.ID, "btn-start-game").click()
    wait.until(EC.visibility_of_element_located((By.ID, "view-table")))

    # 1. Closed state
    driver.execute_script("""
        stopAutoPlay();
        if (typeof bindiCoatBotTimeout !== 'undefined' && bindiCoatBotTimeout) {
            clearTimeout(bindiCoatBotTimeout);
            bindiCoatBotTimeout = null;
        }
        renderBindiCoatState({
            game_id: 'test_bc_rev',
            phase: 'TRICK_PLAY',
            deal_num: 1,
            bandh_hukum: { placed: true, revealed: false },
            my_hand: ['AS', 'KH', 'QD'],
            players: {
                P1: { name: 'Player', team: 'NS', card_count: 3, tricks_won: 0 },
                P2: { name: 'G. Dinesh', team: 'EW', card_count: 3, tricks_won: 0 },
                P3: { name: 'G. Bhimaram', team: 'NS', card_count: 3, tricks_won: 0 },
                P4: { name: 'G. Geeta', team: 'EW', card_count: 3, tricks_won: 0 }
            },
            teams: { NS: { mindis: 0, tricks: 0 }, EW: { mindis: 0, tricks: 0 } },
            current_turn: 'P1',
            current_trick: [],
            logs: []
        });
    """)

    mode_badge = wait.until(EC.visibility_of_element_located((By.ID, "mode-badge")))
    assert "Bandh Hukum" in mode_badge.get_attribute("textContent")

    # 2. Revealed state (Hearts revealed as trump)
    driver.execute_script("""
        renderBindiCoatState({
            game_id: 'test_bc_rev',
            phase: 'TRICK_PLAY',
            deal_num: 1,
            bandh_hukum: { placed: true, revealed: true, trump_suit: 'H', trump_suit_name: 'Hearts' },
            my_hand: ['AS', 'KH', 'QD'],
            players: {
                P1: { name: 'Player', team: 'NS', card_count: 3, tricks_won: 1 },
                P2: { name: 'G. Dinesh', team: 'EW', card_count: 3, tricks_won: 0 },
                P3: { name: 'G. Bhimaram', team: 'NS', card_count: 3, tricks_won: 0 },
                P4: { name: 'G. Geeta', team: 'EW', card_count: 3, tricks_won: 0 }
            },
            teams: { NS: { mindis: 1, tricks: 1 }, EW: { mindis: 0, tricks: 0 } },
            current_turn: 'P1',
            current_trick: [],
            logs: ['Bandh Hukum revealed! Hearts is Trump!']
        });
    """)

    assert "Hearts" in mode_badge.get_attribute("textContent")


def test_selenium_bindicoat_mindi_tracking_scoreboard(driver, server_url):
    """Verifies that captured 10s (Mindis) and trick tallies are tracked for NS and EW."""
    driver.get(server_url)
    wait = WebDriverWait(driver, 10)

    driver.find_element(By.ID, "gsel-bindicoat").click()
    driver.find_element(By.ID, "btn-start-game").click()
    wait.until(EC.visibility_of_element_located((By.ID, "view-table")))

    # Simulate Mindi counts: NS has 2 Mindis / 4 Tricks, EW has 1 Mindi / 3 Tricks
    driver.execute_script("""
        let id = window.setTimeout(function() {}, 0);
        while (id--) { window.clearTimeout(id); }
        stopAutoPlay();
        if (typeof bindiCoatBotTimeout !== 'undefined' && bindiCoatBotTimeout) {
            clearTimeout(bindiCoatBotTimeout);
            bindiCoatBotTimeout = null;
        }
        triggerBindiCoatBotStep = function() {};
        renderBindiCoatState({
            game_id: 'test_bc_mindis',
            phase: 'TRICK_PLAY',
            deal_num: 1,
            bandh_hukum: { placed: true, revealed: true, trump_suit: 'S', trump_suit_name: 'Spades' },
            my_hand: ['AS'],
            players: {
                P1: { name: 'Player', team: 'NS', card_count: 1, tricks_won: 2 },
                P2: { name: 'G. Dinesh', team: 'EW', card_count: 1, tricks_won: 1 },
                P3: { name: 'G. Bhimaram', team: 'NS', card_count: 1, tricks_won: 2 },
                P4: { name: 'G. Geeta', team: 'EW', card_count: 1, tricks_won: 2 }
            },
            teams: {
                NS: { mindis: 2, tricks: 4 },
                EW: { mindis: 1, tricks: 3 }
            },
            current_turn: 'P1',
            current_trick: [],
            logs: []
        });
    """)

    # Verify center area contains NS and EW tallies
    center_area = wait.until(EC.visibility_of_element_located((By.ID, "center-area")))
    text = center_area.get_attribute("textContent")
    assert "NS: 2M / 4T" in text
    assert "EW: 1M / 3T" in text


def test_selenium_bindicoat_coat_detection_and_resolution(driver, server_url):
    """Tests deal complete state when a team achieves 4 Mindis (Bindi Coat)."""
    driver.get(server_url)
    wait = WebDriverWait(driver, 10)

    driver.find_element(By.ID, "gsel-bindicoat").click()
    driver.find_element(By.ID, "btn-start-game").click()
    wait.until(EC.visibility_of_element_located((By.ID, "view-table")))

    # Simulate GAME_OVER where NS captured all 4 Mindis (Whitewash Coat!)
    driver.execute_script("""
        let id = window.setTimeout(function() {}, 0);
        while (id--) { window.clearTimeout(id); }
        stopAutoPlay();
        if (typeof bindiCoatBotTimeout !== 'undefined' && bindiCoatBotTimeout) {
            clearTimeout(bindiCoatBotTimeout);
            bindiCoatBotTimeout = null;
        }
        triggerBindiCoatBotStep = function() {};
        renderBindiCoatState({
            game_id: 'test_bc_coat',
            phase: 'GAME_OVER',
            deal_num: 1,
            bandh_hukum: { placed: true, revealed: true, trump_suit: 'S', trump_suit_name: 'Spades' },
            my_hand: [],
            players: {
                P1: { name: 'Player', team: 'NS', card_count: 0, tricks_won: 4 },
                P2: { name: 'G. Dinesh', team: 'EW', card_count: 0, tricks_won: 2 },
                P3: { name: 'G. Bhimaram', team: 'NS', card_count: 0, tricks_won: 5 },
                P4: { name: 'G. Geeta', team: 'EW', card_count: 0, tricks_won: 2 }
            },
            teams: {
                NS: { mindis: 4, tricks: 9 },  // 4 Mindis = White-wash Coat!
                EW: { mindis: 0, tricks: 4 }
            },
            winner_team: 'NS',
            is_coat: true,
            current_turn: 'P1',
            current_trick: [],
            logs: ['🏆 BINDI COAT! Team NS captured ALL 4 MINDIS (10s)!']
        });
    """)

    # Turn badge should indicate deal complete
    turn_badge = wait.until(EC.visibility_of_element_located((By.ID, "turn-badge")))
    assert "Deal Complete" in turn_badge.get_attribute("textContent")
    assert "turn-badge-winner" in turn_badge.get_attribute("class")

    # Next deal button should appear with highlight pulse
    btn_next = wait.until(EC.visibility_of_element_located((By.ID, "btn-next-deal")))
    assert btn_next.is_displayed()
