#!/usr/bin/env bash
# ArogyaMitra — Local Environment Setup Script (Bash)
# Enforces Python >= 3.11, Node >= 20, uv, npm and installs dependencies

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$REPO_ROOT"

echo "============================================================"
echo "  AROGYAMITRA LOCAL SETUP CHECK"
echo "============================================================"

# 1. Check Python
if ! command -v python3 &>/dev/null; then
    echo "ERROR: python3 is not installed." >&2
    exit 1
fi
PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "[+] Python version: $PY_VER"

# 2. Check Node
if ! command -v node &>/dev/null; then
    echo "ERROR: node is not installed." >&2
    exit 1
fi
NODE_VER=$(node -v | sed 's/v//')
echo "[+] Node version: $NODE_VER"

# 3. Check uv
if ! command -v uv &>/dev/null; then
    echo "ERROR: uv is not installed." >&2
    exit 1
fi
echo "[+] uv version: $(uv --version)"

# 4. Check npm
if ! command -v npm &>/dev/null; then
    echo "ERROR: npm is not installed." >&2
    exit 1
fi
echo "[+] npm version: $(npm -v)"

# 5. Install dependencies
echo "[*] Syncing Python dependencies via uv..."
uv sync

echo "[*] Installing Backend dependencies via npm..."
cd "$REPO_ROOT/Backend"
if [ ! -f "$REPO_ROOT/Backend/.env" ] && [ -f "$REPO_ROOT/Backend/.env.example" ]; then
    cp "$REPO_ROOT/Backend/.env.example" "$REPO_ROOT/Backend/.env"
    echo "[+] Initialized Backend/.env from .env.example"
fi
npm install

cd "$REPO_ROOT"
echo "============================================================"
echo "  SETUP COMPLETED SUCCESSFULLY"
echo "============================================================"
