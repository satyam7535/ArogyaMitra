#!/usr/bin/env bash
# Shell verification runner for ArogyaMitra
# Runs: lint -> ML tests -> Backend tests -> Graph tests -> UI tests
# Exits non-zero on any failure and writes each output to docs/evidence/verify_<suite>.txt

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$REPO_ROOT"

EVIDENCE_DIR="$REPO_ROOT/docs/evidence"
mkdir -p "$EVIDENCE_DIR"

echo "============================================================"
echo "  1. RUNNING LINT (Python & Node Syntax)"
echo "============================================================"
{
    echo "# Running ruff lint check on Python codebase..."
    uv run ruff check --select E9,F63,F7,F82 ML_Model graph ui
    echo "# Running Node syntax check on Backend/src..."
    find Backend/src -name "*.js" -exec node --check {} +
    echo "Lint checks completed successfully."
} 2>&1 | tee "$EVIDENCE_DIR/verify_lint.txt"

echo "============================================================"
echo "  2. RUNNING ML TESTS"
echo "============================================================"
{
    cd "$REPO_ROOT/ML_Model"
    PYTHONPATH="$REPO_ROOT/ML_Model" uv run pytest tests/test_phase1.py -v
} 2>&1 | tee "$EVIDENCE_DIR/verify_ml.txt"

echo "============================================================"
echo "  3. RUNNING BACKEND TESTS"
echo "============================================================"
{
    cd "$REPO_ROOT/Backend"
    npm test
} 2>&1 | tee "$EVIDENCE_DIR/verify_backend.txt"

echo "============================================================"
echo "  4. RUNNING GRAPH TESTS"
echo "============================================================"
{
    cd "$REPO_ROOT/graph"
    PYTHONPATH="$REPO_ROOT/graph" uv run pytest tests/test_phase3.py -v
} 2>&1 | tee "$EVIDENCE_DIR/verify_graph.txt"

echo "============================================================"
echo "  5. RUNNING UI TESTS"
echo "============================================================"
{
    cd "$REPO_ROOT/ui"
    PYTHONPATH="$REPO_ROOT/ui" uv run pytest tests/test_streamlit.py -v
} 2>&1 | tee "$EVIDENCE_DIR/verify_ui.txt"

echo "============================================================"
echo "  ALL SUITES PASSED VERIFICATION"
echo "============================================================"
exit 0
