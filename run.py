import subprocess
import sys
import webbrowser
import time
import uvicorn


def run_tests():
    print("=" * 70)
    print("Running Bikkad Game Engine Automated Test Suite...")
    print("=" * 70)
    result = subprocess.run([sys.executable, "-m", "pytest", "-s", "backend/tests"], capture_output=False)
    if result.returncode != 0:
        print("\n[!] Tests failed. Please review engine implementation.")
        sys.exit(result.returncode)
    print("\n[OK] All engine tests passed successfully!\n")


def start_server():
    host = "127.0.0.1"
    port = 8000
    url = f"http://{host}:{port}"
    
    print("=" * 70)
    print(f"Launching Bikkad Web Application at {url}")
    print("=" * 70)

    # Open browser automatically after brief delay
    webbrowser.open(url)

    uvicorn.run("backend.server:app", host=host, port=port, reload=True)


if __name__ == "__main__":
    run_tests()
    start_server()
