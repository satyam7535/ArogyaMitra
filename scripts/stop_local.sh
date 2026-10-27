#!/usr/bin/env bash
# ArogyaMitra — Local Services Shutdown Script (Bash)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
PID_FILE="$REPO_ROOT/.pids"

echo "============================================================"
echo "  STOPPING AROGYAMITRA LOCAL SERVICES"
echo "============================================================"

if [ -f "$PID_FILE" ]; then
    while IFS='=' read -r name pid; do
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            echo "[*] Stopping $name (PID $pid)..."
            kill -15 "$pid" 2>/dev/null || kill -9 "$pid" 2>/dev/null || true
        fi
    done < "$PID_FILE"
    rm -f "$PID_FILE"
fi

# Ensure ports 8000, 8001, 5000, 8501 are freed
for port in 8000 8001 5000 8501; do
    pids=$(lsof -ti :$port 2>/dev/null || true)
    if [ -n "$pids" ]; then
        echo "[*] Killing remaining process on port $port ($pids)..."
        kill -9 $pids 2>/dev/null || true
    fi
done

echo "[+] All ArogyaMitra services stopped and ports freed."
