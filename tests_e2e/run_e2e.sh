#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status, except pytest.
set -eo pipefail

# Define variables
MOCK_PORT=${MOCK_PORT:-8000}
MOCK_HOST=${MOCK_HOST:-127.0.0.1}
export APP_URL="http://$MOCK_HOST:$MOCK_PORT"

# Clean up function to terminate background jobs on exit
PID_FILE=".mock_server.pid"
cleanup() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null; then
            echo "[E2E Runner] Shutting down mock server (PID: $PID)..."
            kill "$PID" || true
            wait "$PID" 2>/dev/null || true
        fi
        rm -f "$PID_FILE"
    fi
}
trap cleanup EXIT INT TERM

echo "[E2E Runner] Starting mock server on $APP_URL..."
# Run the mock server in the background
# We assume mock_server.py is in the tests_e2e directory
python -m uvicorn tests_e2e.mock_server:app --host "$MOCK_HOST" --port "$MOCK_PORT" > .mock_server.log 2>&1 &
MOCK_PID=$!
echo "$MOCK_PID" > "$PID_FILE"

# Wait for mock server to become healthy
echo "[E2E Runner] Waiting for mock server to become healthy..."
TIMEOUT=15
ELAPSED=0
HEALTH_CHECK_URL="$APP_URL/health"

# Fallback: check via python if curl is not installed
use_python_check=0
if ! command -v curl &> /dev/null; then
    use_python_check=1
fi

until [ "$ELAPSED" -gt $((TIMEOUT * 2)) ]; do
    if [ "$use_python_check" -eq 1 ]; then
        if python -c "import sys, httpx; sys.exit(0) if httpx.get('$HEALTH_CHECK_URL').status_code == 200 else sys.exit(1)" 2>/dev/null; then
            break
        fi
    else
        if curl -s "$HEALTH_CHECK_URL" > /dev/null; then
            break
        fi
    fi
    sleep 0.5
    ELAPSED=$((ELAPSED + 1))
done

if [ "$ELAPSED" -gt $((TIMEOUT * 2)) ]; do
    echo "[E2E Runner] Error: Mock server did not become healthy within $TIMEOUT seconds."
    echo "[E2E Runner] Mock server logs:"
    cat .mock_server.log
    exit 1
fi

echo "[E2E Runner] Mock server is healthy. Running E2E tests..."

# Run pytest. We pass any arguments given to run_e2e.sh directly to pytest.
set +e # Don't exit on pytest failure so cleanup can run
pytest "$@"
PYTEST_STATUS=$?
set -e

echo "[E2E Runner] Tests completed with status $PYTEST_STATUS."
exit "$PYTEST_STATUS"
