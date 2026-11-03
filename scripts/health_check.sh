#!/usr/bin/env bash
# ArogyaMitra — Service Health Check (Bash)
# Probes ports 8000, 8001, 5000, 8501 and returns a single-line status per service

ALL_HEALTHY=true

echo "============================================================"
echo "  AROGYAMITRA SERVICES HEALTH STATUS"
echo "============================================================"

check_svc() {
    local name="$1"
    local url="$2"
    local code
    code=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 "$url" || echo "000")
    if [[ "$code" =~ ^[23] ]]; then
        printf "%-35s : HEALTHY (HTTP %s)\n" "$name" "$code"
    else
        printf "%-35s : DOWN (HTTP %s)\n" "$name" "$code"
        ALL_HEALTHY=false
    fi
}

check_svc "ML Microservice (:8000)" "http://127.0.0.1:8000/health"
check_svc "Graph AI Service (:8001)" "http://127.0.0.1:8001/health"
check_svc "Backend Gateway API (:5000)" "http://127.0.0.1:5000/health"
check_svc "Streamlit Thin-Client (:8501)" "http://127.0.0.1:8501/"

echo "============================================================"
if [ "$ALL_HEALTHY" = true ]; then
    echo "STATUS: ALL 4 SERVICES OPERATIONAL"
    exit 0
else
    echo "STATUS: ONE OR MORE SERVICES DOWN OR DEGRADED"
    exit 1
fi
