#!/usr/bin/env bash
# ArogyaMitra — Local Services Startup Script (Bash)

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$REPO_ROOT"

PID_FILE="$REPO_ROOT/.pids"

echo "============================================================"
echo "  STARTING AROGYAMITRA LOCAL SERVICES"
echo "============================================================"

if [ -f "$PID_FILE" ]; then
    echo "[!] Found existing .pids file. Cleaning up prior processes first..."
    bash "$SCRIPT_DIR/stop_local.sh" || true
fi

# 1. Start ML Microservice (:8000)
echo "[*] Launching ML Microservice on port 8000..."
uv run python ML_Model/app.py > /dev/null 2>&1 &
ML_PID=$!
echo "ml=$ML_PID" >> "$PID_FILE"

# 2. Start Graph AI Service (:8001)
echo "[*] Launching Graph AI Reasoning Service on port 8001..."
uv run python graph/server.py > /dev/null 2>&1 &
GRAPH_PID=$!
echo "graph=$GRAPH_PID" >> "$PID_FILE"

# 3. Start Backend Gateway (:5000)
echo "[*] Launching Node Backend Gateway on port 5000..."
(cd "$REPO_ROOT/Backend" && node src/index.js > /dev/null 2>&1 & echo "backend=$!" >> "$PID_FILE")

# 4. Start Streamlit UI (:8501)
echo "[*] Launching Streamlit Clinical UI on port 8501..."
(cd "$REPO_ROOT/ui" && uv run streamlit run Home.py --server.port 8501 --server.headless true > /dev/null 2>&1 & echo "ui=$!" >> "$PID_FILE")

echo "[+] Saved process IDs to: $PID_FILE"

# Await health convergence
echo "[*] Awaiting health convergence on all 4 endpoints..."
MAX_ATTEMPTS=15
ALL_UP=false

for i in $(seq 1 $MAX_ATTEMPTS); do
    sleep 2
    if bash "$SCRIPT_DIR/health_check.sh" > /dev/null 2>&1; then
        ALL_UP=true
        break
    fi
    echo "    Attempt $i/$MAX_ATTEMPTS: warming up..."
done

if [ "$ALL_UP" = true ]; then
    echo "[+] All 4 services confirmed healthy and operational!"
    bash "$SCRIPT_DIR/health_check.sh"
    exit 0
else
    echo "[!] Timeout waiting for services to converge."
    bash "$SCRIPT_DIR/health_check.sh"
    exit 1
fi
