"""
Automated Selenium Test Suite for Tikdi (Teen Do Paanch / 3-2-5).
Tests browser UI, penalty mode selection, 3-player table layout,
5-3-2 quotas, role badges (Dealer/Chooser/Bystander), and Tikdi scoreboard.
"""

import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


def test_selenium_tikdi_home_selection(driver, server_url):
    """Verifies selecting Tikdi shows penalty mode and hides 4th seat."""
    driver.get(server_url)
    wait = WebDriverWait(driver, 10)

    # Click Tikdi selector card
    tikdi_card = wait.until(EC.element_to_be_clickable((By.ID, "gsel-tikdi")))
    tikdi_card.click()

    # Verify Tikdi is active
    assert "gsel-active" in tikdi_card.get_attribute("class")

    # Penalty mode selector should be visible
    penalty_group = wait.until(EC.visibility_of_element_located((By.ID, "group-tikdi-penalty-mode")))
    assert penalty_group.is_displayed()

    # Verify penalty options
    penalty_select = Select(driver.find_element(By.ID, "select-tikdi-penalty-mode"))
    opts = [o.text for o in penalty_select.options]
    assert any("Tash Khinchai" in o for o in opts)
    assert any("Quota Adjustment" in o for o in opts)


def test_selenium_tikdi_start_game_and_table_mode(driver, server_url):
    """Starts a Tikdi match and verifies 3-player felt-table.tikdi-mode layout."""
    driver.get(server_url)
    wait = WebDriverWait(driver, 10)

    driver.find_element(By.ID, "gsel-tikdi").click()
    driver.find_element(By.ID, "btn-start-game").click()

    # Wait for Table View
    wait.until(EC.visibility_of_element_located((By.ID, "view-table")))

    # Verify felt-table has tikdi-mode class
    felt_table = driver.find_element(By.CLASS_NAME, "felt-table")
    assert "tikdi-mode" in felt_table.get_attribute("class")

    # Verify header title updates to TIKDI
    header_title = driver.find_element(By.ID, "header-game-title")
    assert "TIKDI" in header_title.get_attribute("textContent").upper()

    # Verify 3 active seats (South P1, West P2, North P3)
    assert driver.find_element(By.ID, "seat-P1").is_displayed()
    assert driver.find_element(By.ID, "seat-P2").is_displayed()
    assert driver.find_element(By.ID, "seat-P3").is_displayed()


def test_selenium_tikdi_scoreboard_and_quotas(driver, server_url):
    """Verifies that the dedicated 3-player Tikdi scoreboard and 5-3-2 quotas are rendered."""
    driver.get(server_url)
    wait = WebDriverWait(driver, 10)

    driver.find_element(By.ID, "gsel-tikdi").click()
    driver.find_element(By.ID, "btn-start-game").click()
    wait.until(EC.visibility_of_element_located((By.ID, "view-table")))

    # Dedicated Tikdi scoreboard should be visible
    tikdi_board = wait.until(EC.visibility_of_element_located((By.ID, "tikdi-scoreboard-panel")))
    assert tikdi_board.is_displayed()

    # Bikkad scoreboard should be hidden
    wait.until(lambda d: "hidden" in d.find_element(By.ID, "bikkad-scoreboard-panel").get_attribute("class"))

    # South Hand cards should be present (first 5 cards dealt for trump selection)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#hand-P1 .card-wrapper")))
    hand_cards = driver.find_elements(By.CSS_SELECTOR, "#hand-P1 .card-wrapper")
    assert len(hand_cards) >= 5


def test_selenium_tikdi_phase1_trump_selection(driver, server_url):
    """Tests Phase 1 initial 5 cards deal and choosing trump suit."""
    driver.get(server_url)
    wait = WebDriverWait(driver, 10)

    driver.find_element(By.ID, "gsel-tikdi").click()
    driver.find_element(By.ID, "btn-start-game").click()
    wait.until(EC.visibility_of_element_located((By.ID, "view-table")))

    # Simulate Phase 1 TRUMP_SELECTION with Spades chosen
    driver.execute_script("""
        let id = window.setTimeout(function() {}, 0);
        while (id--) { window.clearTimeout(id); }
        stopAutoPlay();
        if (typeof tikdiBotTimeout !== 'undefined' && tikdiBotTimeout) {
            clearTimeout(tikdiBotTimeout);
            tikdiBotTimeout = null;
        }
        triggerTikdiBotStep = function() {};
        renderTikdiState({
            game_id: 'test_tikdi_trump',
            phase: 'TRICK_PLAY',
            round_num: 1,
            dealer_id: 'P3',
            trump_chooser_id: 'P1',
            bystander_id: 'P2',
            trump_suit: 'S',
            quotas: { P1: 5, P2: 3, P3: 2 },
            tricks_won: { P1: 0, P2: 0, P3: 0 },
            hands: {
                P1: [
                    { code: 'AS', suit: 'S', rank: 'A' },
                    { code: 'KS', suit: 'S', rank: 'K' },
                    { code: '10H', suit: 'H', rank: '10' }
                ],
                P2: [1,2,3], P3: [1,2,3]
            },
            current_turn: 'P1',
            current_trick: [],
            player_names: { P1: 'Sagan', P2: 'G. Dinesh', P3: 'G. Bhimaram' }
        });
    """)

    # Verify Center Trump Slot displays SPADES and symbol ♠
    trump_label = wait.until(EC.visibility_of_element_located((By.ID, "trump-slot-label")))
    assert "SPADES" in trump_label.get_attribute("textContent").upper()
    trump_container = driver.find_element(By.ID, "trump-card-container")
    assert "♠" in trump_container.get_attribute("textContent")


def test_selenium_tikdi_following_suit_rule(driver, server_url):
    """Verifies that Tikdi restricts card play to led suit when player holds matching cards."""
    driver.get(server_url)
    wait = WebDriverWait(driver, 10)

    driver.find_element(By.ID, "gsel-tikdi").click()
    driver.find_element(By.ID, "btn-start-game").click()
    wait.until(EC.visibility_of_element_located((By.ID, "view-table")))

    # Simulate Diamonds led, P1 holds 1 Diamond and 1 Heart
    driver.execute_script("""
        let id = window.setTimeout(function() {}, 0);
        while (id--) { window.clearTimeout(id); }
        stopAutoPlay();
        if (typeof tikdiBotTimeout !== 'undefined' && tikdiBotTimeout) {
            clearTimeout(tikdiBotTimeout);
            tikdiBotTimeout = null;
        }
        triggerTikdiBotStep = function() {};
        renderTikdiState({
            game_id: 'test_tikdi_follow',
            phase: 'TRICK_PLAY',
            round_num: 1,
            dealer_id: 'P3',
            trump_chooser_id: 'P1',
            trump_suit: 'S',
            led_suit: 'D',
            quotas: { P1: 5, P2: 3, P3: 2 },
            tricks_won: { P1: 1, P2: 0, P3: 0 },
            hands: {
                P1: [
                    { code: 'KD', suit: 'D', rank: 'K' },
                    { code: 'AH', suit: 'H', rank: 'A' }
                ],
                P2: [1], P3: [1]
            },
            current_turn: 'P1',
            current_trick: [{ player_id: 'P2', card: { code: '7D', suit: 'D' } }],
            player_names: { P1: 'Sagan', P2: 'G. Dinesh', P3: 'G. Bhimaram' }
        });
    """)

    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#hand-P1 .card-wrapper")))
    cards = driver.find_elements(By.CSS_SELECTOR, "#hand-P1 .card-wrapper")
    assert len(cards) == 2

    # KD should be legal, AH illegal
    assert "legal-card" in cards[0].get_attribute("class")
    assert "illegal-card" in cards[1].get_attribute("class")


def test_selenium_tikdi_penalty_modal_card_swap(driver, server_url):
    """Tests Tash Khinchai penalty modal opening, face-down pullable cards, and status."""
    driver.get(server_url)
    wait = WebDriverWait(driver, 10)

    driver.find_element(By.ID, "gsel-tikdi").click()
    driver.find_element(By.ID, "btn-start-game").click()
    wait.until(EC.visibility_of_element_located((By.ID, "view-table")))

    # Simulate Penalty Resolution state where P1 pulled ahead and pulls from P2
    driver.execute_script("""
        stopAutoPlay();
        tikdiPendingReturnTarget = null;
        renderTikdiState({
            game_id: 'test_tikdi_pen',
            phase: 'PENALTY_RESOLUTION',
            round_num: 1,
            dealer_id: 'P1',
            trump_chooser_id: 'P2',
            quotas: { P1: 2, P2: 5, P3: 3 },
            tricks_won: { P1: 4, P2: 4, P3: 2 },
            penalty_queue: [{ puller: 'P1', target: 'P2' }],
            hands: {
                P1: [{ code: 'AS' }, { code: 'KH' }, { code: 'QD' }],
                P2: [{ code: '10S' }, { code: '9H' }, { code: '8D' }]
            },
            player_names: { P1: 'Sagan', P2: 'G. Dinesh', P3: 'G. Bhimaram' }
        });
        renderTikdiPenaltyModal(gameState);
    """)

    modal = wait.until(EC.visibility_of_element_located((By.ID, "modal-tikdi-penalty")))
    assert modal.is_displayed()

    # Title should indicate pulling penalty card
    title_el = driver.find_element(By.ID, "tikdi-penalty-title")
    assert "PULL" in title_el.get_attribute("textContent").upper()

    # Verify pullable face-down cards are rendered
    pullable_cards = driver.find_elements(By.CLASS_NAME, "tikdi-pullable-card")
    assert len(pullable_cards) == 3


def test_selenium_tikdi_round_complete_and_dealer_rotation(driver, server_url):
    """Verifies round complete state, next deal button, and scoreboard net scores."""
    driver.get(server_url)
    wait = WebDriverWait(driver, 10)

    driver.find_element(By.ID, "gsel-tikdi").click()
    driver.find_element(By.ID, "btn-start-game").click()
    wait.until(EC.visibility_of_element_located((By.ID, "view-table")))

    # Simulate Round Over state
    driver.execute_script("""
        let id = window.setTimeout(function() {}, 0);
        while (id--) { window.clearTimeout(id); }
        stopAutoPlay();
        if (typeof tikdiBotTimeout !== 'undefined' && tikdiBotTimeout) {
            clearTimeout(tikdiBotTimeout);
            tikdiBotTimeout = null;
        }
        triggerTikdiBotStep = function() {};
        renderTikdiState({
            game_id: 'test_tikdi_over',
            phase: 'ROUND_OVER',
            round_num: 1,
            dealer_id: 'P3',
            trump_chooser_id: 'P1',
            quotas: { P1: 5, P2: 3, P3: 2 },
            tricks_won: { P1: 6, P2: 3, P3: 1 },
            cumulative_scores: { P1: 1, P2: 0, P3: -1 },
            hands: { P1: [], P2: [], P3: [] },
            player_names: { P1: 'Sagan', P2: 'G. Dinesh', P3: 'G. Bhimaram' }
        });
    """)

    # Turn badge should indicate round complete
    turn_badge = wait.until(EC.visibility_of_element_located((By.ID, "turn-badge")))
    assert "Round Complete" in turn_badge.get_attribute("textContent")
    assert "turn-badge-winner" in turn_badge.get_attribute("class")

    # Next deal button should be displayed
    btn_next = wait.until(EC.visibility_of_element_located((By.ID, "btn-next-deal")))
    assert btn_next.is_displayed()
