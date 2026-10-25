# ArogyaMitra Project Progress Log

| Date | Task | Status | Notes |
|------|------|--------|-------|
| 2026-10-26 | Phase 0 Setup: Branch creation (`phase-0-baseline`) | DONE | Created and switched to branch `phase-0-baseline`. |
| 2026-10-26 | Task 0.1: Docs scaffolding, .editorconfig, .gitignore | DONE | Created `docs/PROGRESS.md`, `docs/DECISIONS.md`, `docs/evidence/.gitkeep`, root `.editorconfig`, updated `.gitignore` keeping model binaries/datasets ignored but keeping `.gitkeep`. |
| 2026-10-26 | Task 0.2: Reconstruct ML_Model/app.py & prediction contract | DONE | Created clean FastAPI microservice in `ML_Model/app.py` with `/`, `/health`, `/symptoms`, `/predict`, CORS from env, graceful artifact loading, and verified full prediction contract. Removed PDF logic from ML service. Created `ML_Model/scripts/train_baseline.py` and generated baseline model artifacts in `ML_Model/model/`. Created pytest suite in `ML_Model/tests/test_phase0.py` (4/4 tests passing). |
| 2026-10-26 | Task 0.3: Dataset documentation script | DONE | Created `ML_Model/scripts/download_dataset.md` detailing Kaggle datasets and layout. |
| 2026-10-26 | Task 0.4: Remove dead and boilerplate code | DONE | Deleted `Frontend/src/App.jsx`, `Frontend/src/App.css`, removed unused `express-session` from `Backend/package.json`, removed dead `generate_llm_prompt` from `graph/llm.py`. |
| 2026-10-26 | Task 0.5: Docker Compose stack with health checks | DONE | Created `docker-compose.yml` defining `mongo`, `ml`, `graph`, `backend`, and `frontend` services with container healthchecks, internal network, and env configurations. Added Dockerfiles for Backend and Frontend. |
| 2026-10-26 | Task 0.6: Update README with accurate paths & Mermaid diagram | DONE | Rewrote `README.md` with clinical decision support disclaimer, Mermaid system architecture flowchart, "Setup in 5 commands", manual setup steps, prediction contract, and Gemini OpenAI-compatible configuration. |
| 2026-10-26 | Task 0.7: Pin dependency versions | DONE | Pinned versions in `Backend/package.json`, `Frontend/package.json`, `ML_Model/requirements.txt`, and `graph/requirements.txt`. Cleaned `graph/requirements.txt` of unused ML libraries. Committed exact lockfiles. |
| 2026-10-26 | Phase 0 Gate Evaluation | PASSED | Automated test suite verified 4/4 passing tests; prediction contract verified; healthchecks defined on all services; raw empirical evidence logged to `docs/evidence/phase0_ml_contract.txt`. |
