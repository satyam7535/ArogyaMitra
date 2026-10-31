# Security Vulnerability Tracking and Risk Dispositions

This document records the exact state of all known third-party security vulnerabilities, audit scan findings, and mitigation rationales for ArogyaMitra.

## Scan Summary Baseline

| Tool | Target | Status | Findings / Breakdown |
| :--- | :--- | :--- | :--- |
| **npm audit** | `Backend/` | CLEAN | 0 vulnerabilities (exit code 0) |
| **pip-audit** | `.venv` | CLEAN | 0 vulnerabilities (exit code 0; `pyarrow 26.0.0`, `numpy 2.4.6`) |
| **Bandit** | `ML_Model`, `graph`, `ui` | CLEAN | 0 High, 0 Medium, 11 Low (exit code 0) |
| **Semgrep** | Full codebase | CLEAN | 0 findings across 484 rules on 99 files (exit code 0) |
| **Gitleaks** | Git commit history | CLEAN | 17 commits scanned, 0 leaks detected (exit code 0) |
| **Trivy** | Filesystem | VERIFIED | Trivy 0.76.1 installed (`Backend/package-lock.json`: 0 vulns, `uv.lock`: 0 vulns) |

---

## Resolved Vulnerability Analysis

### 1. PyArrow: PYSEC-2026-113 (RESOLVED)
- **Previous Affected Version:** `pyarrow==18.1.0`
- **Resolution:** Upgraded to `pyarrow 26.0.0` with `numpy 2.4.6`.
- **How Resolved:**
  - Benchmark-only tools (`shap`, `lightgbm`, `xgboost`) were removed from runtime production dependencies in `pyproject.toml` and segregated into `[project.optional-dependencies] benchmark`.
  - The live inference service (`ML_Model/app.py`) operates on Bernoulli Naive Bayes (`BernoulliNB v2.0.0`), which fully supports NumPy 2.x without SHAP C-extensions.
  - Production model artifacts were retrained under NumPy 2.x using `ML_Model/training/train_v2_naive_bayes.py`.
  - The full 248/248 test suite passed green.
  - `pip-audit` scan confirms: **No known vulnerabilities found**.

---

## Bandit Static Analysis Disposition (11 Low Issues)
- **B110 (`try_except_pass`):** 8 instances in helper fallback blocks (e.g. `sys.stdout.reconfigure(encoding='utf-8')` for Windows console or graceful empty array return in Streamlit client). No security impact.
- **B404 / B603 / B607 (`subprocess.run` with partial path):** 3 instances in `train_v2_naive_bayes.py` invoking `git rev-parse --short HEAD` to record the git commit into model metadata. Uses hardcoded string array, no shell execution (`shell=False`), no untrusted input.
