import socket
import time
import threading
import pytest
import uvicorn

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from backend.server import app


def get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


@pytest.fixture(scope="session")
def server_url():
    """Starts a live uvicorn server in a background thread for the test session."""
    port = get_free_port()
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
    server = uvicorn.Server(config)

    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    # Wait until server is reachable
    url = f"http://127.0.0.1:{port}"
    timeout = 10.0
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection(('127.0.0.1', port), timeout=0.5):
                break
        except (OSError, ConnectionRefusedError):
            time.sleep(0.1)

    yield url
    server.should_exit = True


@pytest.fixture(scope="function")
def driver():
    """Creates a headless Chrome WebDriver instance."""
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1400,900")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    drv = webdriver.Chrome(options=chrome_options)
    drv.implicitly_wait(6)
    yield drv
    try:
        drv.quit()
    except Exception:
        pass
