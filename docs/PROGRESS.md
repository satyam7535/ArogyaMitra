# ArogyaMitra Project Progress Log

| Date | Task | Status | Notes |
|------|------|--------|-------|
| 2026-10-26 | Phase 0 Setup: Branch creation (`phase-0-baseline`) | DONE | Created and switched to branch `phase-0-baseline`. |
| 2026-10-26 | Task 0.1: Docs scaffolding, .editorconfig, .gitignore | DONE | Created `docs/PROGRESS.md`, `docs/DECISIONS.md`, `docs/evidence/.gitkeep`, root `.editorconfig`, updated `.gitignore` keeping model binaries/datasets ignored while tracking `.gitkeep`. Confirmed no real `.env` committed to git. |
| 2026-10-26 | Task 0.2: Reconstruct ML_Model/app.py & prediction contract | DONE | Created clean FastAPI microservice in `ML_Model/app.py` with `/`, `/health`, `/symptoms`, `/predict`, CORS from env, graceful artifact loading, and verified full prediction contract. Removed duplicate PDF logic. Baseline artifacts generated in `ML_Model/model/`. Created pytest suite in `ML_Model/tests/test_phase0.py` (4/4 tests passing). |
| 2026-10-26 | Task 0.3: Dataset documentation script | DONE | Created `ML_Model/scripts/download_dataset.md` detailing Kaggle datasets and layout. |
| 2026-10-26 | Task 0.4: Remove dead and boilerplate code | DONE | Deleted `Frontend/src/App.jsx`, `Frontend/src/App.css`, removed unused `express-session` from `Backend/package.json`, removed dead `generate_llm_prompt` from `graph/llm.py`. Standardized `graph/.env` with `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL`. |
| 2026-10-26 | Task 0.5: Docker Compose stack with health checks | DONE | Created `docker-compose.yml` defining `mongo`, `ml`, `graph`, `backend`, and `frontend` services with container healthchecks, internal network, and env configurations. Added Dockerfiles for Backend and Frontend. |
| 2026-10-26 | Task 0.6: Update README with accurate paths & Mermaid diagram | DONE | Rewrote `README.md` with clinical decision support disclaimer, Mermaid system architecture flowchart, "Setup in 5 commands", manual setup steps, prediction contract, and Gemini OpenAI-compatible configuration. |
| 2026-10-26 | Task 0.7: Pin dependency versions | DONE | Pinned versions in `Backend/package.json`, `Frontend/package.json`, `ML_Model/requirements.txt`, and `graph/requirements.txt`. Installed all pinned requirements into `.venv` on `D:\` verifying 100% resolution with zero conflicts. Committed exact lockfiles. |
| 2026-10-26 | Phase 0 Gate Evaluation | PARTIAL | Automated tests passed (4/4) and pinned requirements resolved. Docker compose up execution deferred due to C: drive space limit on host Docker engine VM; marked partial. Proceeding with ML-only Phase 1. Docker validation required before Phase 2 gate. |
| 2026-10-26 | Phase 1 Setup: Branch creation (`phase-1-ml`) | IN_PROGRESS | Branching to `phase-1-ml`. |
