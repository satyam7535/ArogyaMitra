# Security Vulnerability Tracking and Risk Dispositions

This document records the exact state of all known third-party security vulnerabilities, audit scan findings, and mitigation rationales for ArogyaMitra.

## Scan Summary Baseline

| Tool | Target | Status | Findings / Breakdown |
| :--- | :--- | :--- | :--- |
| **npm audit** | `Backend/` | CLEAN | 0 vulnerabilities (exit code 0) |
| **pip-audit** | `.venv` | ADVISORY NOTED | 1 package flagged (`pyarrow 18.1.0`), 0 other findings |
| **Bandit** | `ML_Model`, `graph`, `ui` | CLEAN | 0 High, 0 Medium, 11 Low (exit code 0) |
| **Semgrep** | Full codebase | CLEAN | 0 findings across 484 rules on 99 files (exit code 0) |
| **Gitleaks** | Git commit history | CLEAN | 17 commits scanned, 0 leaks detected (exit code 0) |
| **Trivy** | Filesystem | NOT RUN | Binary not present in `D:\tools` and not on PATH |

---

## Detailed Vulnerability Analysis

### 1. PyArrow: PYSEC-2026-113 (GHSA-xxxx)
- **Affected Version:** `pyarrow==18.1.0`
- **Fixed Version:** `23.0.1`
- **CVSS / Severity:** High (Score 7.5 - 8.1 depending on context)
- **Vulnerability Description:** Arbitrary code execution or buffer overflow vulnerability when parsing untrusted Arrow IPC messages or malformed Arrow/Parquet file headers.
- **Why the Pin is Needed:**
  - Upgrading `pyarrow>=19.0.0` or `>=23.0.1` on Windows Python 3.11 requires `numpy>=2.0.0`.
  - ArogyaMitra requires `numpy<2.0.0` (1.26.4) due to binary model deserialization constraints in `scikit-learn==1.6.1`, `shap==0.46.0`, and `lime==0.2.0`.
  - Attempting to import `pyarrow>=19` under NumPy 1.26.4 raises `ImportError: pyarrow requires NumPy 2.0 or newer, found 1.26.4`.
  - Streamlit requires `pyarrow` internally for `st.dataframe()` rendering in `ui/pages/3_Admin_Dashboard.py`.
- **Exploitation Assessment:**
  - `pyarrow` is never exposed to user input or network-facing deserialization in ArogyaMitra.
  - All external requests to the AI services and Backend pass through Pydantic (FastAPI) and Zod (Express) validation schemas.
  - Streamlit only uses PyArrow to transfer local sanitized audit logs from Python memory to browser canvas elements.
  - Real attack surface: **None / Not exploitable in current architecture**.

---

## Bandit Static Analysis Disposition (11 Low Issues)
- **B110 (`try_except_pass`):** 8 instances in helper fallback blocks (e.g. `sys.stdout.reconfigure(encoding='utf-8')` for Windows console or graceful empty array return in Streamlit client). No security impact.
- **B404 / B603 / B607 (`subprocess.run` with partial path):** 3 instances in `train_v2_naive_bayes.py` invoking `git rev-parse --short HEAD` to record the git commit into model metadata. Uses hardcoded string array, no shell execution (`shell=False`), no untrusted input.

