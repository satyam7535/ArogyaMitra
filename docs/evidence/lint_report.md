# ArogyaMitra — Comprehensive Code Quality & Lint Audit Report

## 1. Node.js Backend Linting (ESLint)

- **Tool**: ESLint v9.21.0
- **Target**: `Backend/src/`
- **Configuration**: Flat config in `Backend/eslint.config.js` with ES2022 and Node.js global environment bindings.
- **Command**: `npm --prefix Backend run lint`
- **Status**: **PASS (0 errors, 0 warnings)**

Raw execution output:
```
> techathon-3.0@1.0.0 lint
> eslint src/
```

---

## 2. Python Codebase Linting (Ruff Default Rules)

- **Tool**: Ruff v0.17.2 (standard / default rule suite)
- **Target**: `ML_Model/`, `graph/`, `ui/`
- **Command**: `ruff check ML_Model graph ui`
- **Initial Errors**: 216 errors
- **Errors Fixed**: 191 errors resolved (automated syntax and idiom cleanup, unused variables, UTC timezone standardization, and Pydantic exception specificity).
- **Remaining Findings**: 25 documented and categorized findings (listed below).

### Categorization and Rationale for Remaining 25 Python Findings

| Rule | File | Location | Reason / Justification |
| :--- | :--- | :--- | :--- |
| **N999** | `ML_Model/__init__.py`, `ML_Model/training/__init__.py` | Module name | Repository legacy structure uses `ML_Model` folder name; renaming would break root paths and imports across external services. |
| **S110 / BLE001** | `ML_Model/training/train_final.py`, `ML_Model/training/evaluate.py`, `ML_Model/training/benchmark.py`, `ML_Model/scripts/train_baseline.py` | `sys.stdout.reconfigure` | Terminal UTF-8 reconfigure fallback for Windows PowerShell consoles; failing silently is standard practice if the stream is non-redirectable. |
| **BLE001** | `ML_Model/training/train_final.py` | `get_git_commit_hash` | Fallback to "unknown" when git binary or repo metadata is unavailable (e.g. inside stripped Docker container). |
| **BLE001** | `ML_Model/training/benchmark.py` | `log_loss` | Some benchmark models with non-finite outputs in extreme noise folds can throw; caught to append `NaN` rather than abort cross-validation. |
| **BLE001** | `ML_Model/app.py` | Model loading & SHAP attribution | Resilient fallback: if SHAP C-extensions fail or model weights are missing at runtime, the service logs an error and delivers top features or graceful 503 instead of crashing. |
| **BLE001** | `graph/llm.py` | Safe LLM invocation | Clinical safety guarantee: if the external Gemini API times out or throws, the system deterministically catches the exception and falls back to the rules-based clinical engine. |
| **BLE001** | `graph/server.py` | `verify_service_token` | Catch-all for malformed JWT tokens to return HTTP 403 Forbidden with sanitized detail rather than 500 internal server error. |
| **BLE001** | `graph/utils/pdf_generator.py` | Font registration | If system fonts or Noto Sans are absent, ReportLab safely falls back to standard Helvetica. |
| **S110 / BLE001** | `ui/utils/api_client.py` | Healthchecks, symptom fetching, offline triage | Distributed resilience: when backend microservices are unreachable, the UI catches connection errors and gracefully falls back to the embedded in-process offline engine. |
