#!/usr/bin/env python3
import os
import sys
import time
import subprocess
import httpx

def main():
    port = os.getenv("MOCK_PORT", "8001")
    host = os.getenv("MOCK_HOST", "127.0.0.1")
    app_url = f"http://{host}:{port}"
    os.environ["APP_URL"] = app_url

    print(f"[E2E Runner] Starting mock server on {app_url}...")
    
    # Start uvicorn background process
    log_file = open(".mock_server.log", "w")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "tests_e2e.mock_server:app", "--host", host, "--port", port],
        stdout=log_file,
        stderr=log_file,
        preexec_fn=None if os.name == 'nt' else os.setsid
    )

    try:
        # Wait for server to become responsive
        start_time = time.time()
        timeout = 15.0
        server_ready = False
        while time.time() - start_time < timeout:
            try:
                response = httpx.get(f"{app_url}/health")
                if response.status_code == 200:
                    server_ready = True
                    break
            except Exception:
                pass
            time.sleep(0.5)

        if not server_ready:
            print("[E2E Runner] Error: Mock server failed to start or respond to health check.")
            # Print last few lines of uvicorn log
            log_file.close()
            with open(".mock_server.log", "r") as f:
                print(f.read())
            sys.exit(1)

        print("[E2E Runner] Mock server is up. Invoking pytest...")
        # Run pytest passing arguments from the command line
        pytest_args = [sys.executable, "-m", "pytest"] + sys.argv[1:]
        result = subprocess.run(pytest_args)
        sys.exit(result.returncode)

    finally:
        print("[E2E Runner] Terminating mock server...")
        try:
            if os.name == 'nt':
                proc.terminate()
            else:
                import signal
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        except Exception as e:
            print(f"[E2E Runner] Warning while killing process: {e}")
        proc.wait()
        log_file.close()

if __name__ == "__main__":
    main()
