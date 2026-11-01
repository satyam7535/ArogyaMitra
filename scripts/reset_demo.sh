#!/usr/bin/env bash
# ArogyaMitra — Clean Demo Data Reset Script (Linux/macOS)
set -euo pipefail

echo "Syncing reset script into arogya-backend container..."
docker cp backend/src/scripts/resetDemoData.js arogya-backend:/app/src/scripts/resetDemoData.js

echo "Resetting ArogyaMitra demo database to pristine state..."
docker exec -e NODE_ENV=development arogya-backend node src/scripts/resetDemoData.js

echo "Demo database reset successfully. Ready for evaluation demo."
