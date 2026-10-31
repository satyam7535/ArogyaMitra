# ArogyaMitra — Verification & Technical Audit Report

**Project**: ArogyaMitra (AI-Assisted Primary Healthcare Decision Support System)  
**Branch**: `remediation`  
**Repository Root**: `d:\Document\Projects\Internship\Arogyamitra`  
**Date**: 2026-10-31  
**Overall Verdict**: **CONDITIONAL PASS — CORE PLATFORM VERIFIED WITH DOCUMENTED EMPIRICAL METRICS & LIMITATIONS**  
**Independent Verifier Subagent Audit**: Completed (`docs/evidence/subagent_audit_report.txt`, `docs/evidence/independent_verifier_final_transcript.txt`)

---

## 1. Executive Status & Empirical Findings Ledger

This report documents the empirical state of the ArogyaMitra platform following exhaustive automated testing against the live Docker stack (`https://localhost`). All claims are backed by raw command outputs saved in `docs/evidence/`.

### Verified Core Platform Features
1. **Frontline Triage Architecture (P0)**: Live diagnosis path routes through authenticated backend proxy (`POST /api/v1/consultation/triage`). Direct external access to ML (:8000) and Graph (:8001) is blocked with HTTP 403. Upstream container outages fail closed with HTTP 503 (`MODEL_UNAVAILABLE`). All 20 clinical golden cases pass end-to-end with non-empty PDFs (9,332 - 12,400 bytes).
2. **Optimistic Concurrency Control (P5)**: Atomic state transitions under 50 concurrent HTTP requests produce exactly `{200: 1, 409: 49}`. Mixed race (25 accept vs 25 escalate) also yields `{200: 1, 409: 49}`.
3. **Idempotency Deduplication (P3)**: 50 concurrent requests with identical `Idempotency-Key` yield identical `jobId` and create exactly 1 database document in MongoDB.
4. **Transport Security & MITM Proxy Defense (P6)**: Edge reverse proxy enforces TLS 1.2/1.3 and HTTP 301 cleartext redirects. Active interception proxy demonstration (`scripts/test_p6_mitm_proxy_demo.py`) captures cleartext `Authorization: Bearer SECRET_WORKER_JWT_TOKEN_12345` and `X-Patient-Aadhaar` when certificate validation is disabled, while strict TLS clients abort the handshake (0 bytes leaked).
5. **Worker Mid-Job Recovery (P3)**: OS SIGKILL mid-job in Docker results in lease expiration (2000ms) and atomic job reclamation by a second worker.
6. **DPDP Compliance & Blind Index (P3)**: SHA-256 HMAC blind indexing on phone numbers, patient consent tracking, and admin-approved export/delete routes verified.
7. **Playwright E2E UI Suite (P4)**: 10 browser scenarios automated against `https://localhost` with full-page screenshots verified by independent execution verifier.
8. **Regression Test Suite**: 311 / 311 tests pass across ML (55), Backend (225), Graph (22), and UI (9).
9. **Live Clinical LLM (P2)**:
   - Pinned unified model name across `.env`, `graph/.env`, and `docker-compose.yml`: **`gemini-2.5-flash`**.
   - Cloud LLM latency is recorded as **"not measured"** until the daily Google Cloud API project quota resets.
   - **Confidence Filter Overhaul**: Replaced in-place regex substitutions with a multi-attempt regeneration loop (up to 2 attempts). If a banned phrase (`very high`, `high certainty`, `certainty`, `definitive`, `guaranteed`, `certain diagnosis`) is detected in ANY summary field, the LLM is prompted to regenerate once; if non-compliant on retry, the node falls back immediately to the deterministic clinical template. Standalone "certain" was dropped in favor of "certain diagnosis", correctly permitting legitimate clinical phrases ("certain clinical indicators"). Verified via `scripts/test_confidence_word_filter.py` with zero garbled output.
10. **Trivy Container Vulnerability Scans & Package Upgrades**:
    - Upgraded `setuptools>=84.1.0` (installed: `84.2.1`), `wheel>=0.46.2` (installed: `0.48.0`), `urllib3>=2.8.0` (installed: `2.8.0`), `starlette>=1.3.0` (installed: `1.10.0`), `fastapi>=0.115.11` (installed: `0.162.0`), `Pillow>=13.0.0` (installed: `13.0.0`).
    - **`--ignore-unfixed` Scan Results**:
      - `arogyamitra-backend:latest`: **0 vulnerabilities** total (CRITICAL: 0, HIGH: 0, MED: 0, LOW: 0) — completely clean.
      - `arogyamitra-frontend:latest`: **0 CRITICAL**, **2 HIGH** (both residing in pip's internal vendored urllib3), 2 Medium, 4 Low. Application packages clean.
      - `arogyamitra-ml:latest`: **0 CRITICAL**, **2 HIGH** (pip's internal vendored urllib3), 2 Medium, 4 Low. Application packages clean.
      - `arogyamitra-graph:latest`: **0 CRITICAL**, **2 HIGH** (pip's internal vendored urllib3), 2 Medium, 4 Low. Application packages clean.
    - **Pip-Audit Reconciliation**:
      - `ML_Model/requirements.txt`: `No known vulnerabilities found` (0 vulnerabilities).
      - `ui/requirements.txt`: `No known vulnerabilities found` (0 vulnerabilities).
      - `graph/requirements.txt`: 25 advisory entries across 7 transitive LangChain / LangGraph packages (e.g., `langgraph 0.3.5`, `langchain 0.3.20`).
11. **Gitleaks Audit**: Scanned all 36 git commits in repository history: 0 leaks found. All baseline exceptions justified in `docs/GITLEAKS_BASELINE.md`.
12. **Production Startup Environment Hardening & Security Guard Fix**:
    - Removed fallback keys from codebase. Verified via `Backend/tests/encryption_key_exit.test.js` that `node src/index.js` under `NODE_ENV=production` immediately exits with code 1 if `ENCRYPTION_KEY` is missing.
    - Fixed rate-limit guard error message in `security.middleware.js` to accurately reflect the limiter type (`api` vs `auth`):
      `SECURITY_VIOLATION: Rate limiter relaxation for api is strictly forbidden in production mode (NODE_ENV=production).`
      `SECURITY_VIOLATION: Rate limiter relaxation for auth is strictly forbidden in production mode (NODE_ENV=production).`
13. **Empirical Load Benchmark (>=200 req / endpoint / concurrency level)**:
    - Tested using `docker-compose.test.yml` (`ALLOW_LOAD_TEST=true`, `LLM_ENABLED=false`) across 4 real endpoints (`health`, `worker_list`, `submit_triage`, `doctor_respond`) with 200 requests per endpoint per level (800 requests per batch, 2,400 requests total):
      - **C=1 (800 requests)**: 100% success on valid targets, 0 failures (0 401s, 0 429s, 0 5xx), 8.3 req/s, p50=87.6 ms, p90=234.3 ms, p95=291.3 ms, p99=504.2 ms.
      - **C=10 (800 requests)**: 100% success on valid targets, 0 failures (0 401s, 0 429s, 0 5xx), 10.0 req/s, p50=942.1 ms, p90=1908.3 ms, p95=2270.9 ms, p99=3374.7 ms.
      - **C=50 (800 requests)**: 100% success on valid targets, 0 failures (0 401s, 0 429s, 0 5xx), 9.1 req/s, p50=6163.6 ms, p90=8932.6 ms, p95=9751.6 ms, p99=10949.3 ms.
    - **Worker List Bottleneck Analysis (`GET /api/v1/consultation/my`)**:
      - Exhibits highest latency (p50=193.0 ms, p99=660.6 ms at C=1; p95=3046.8 ms at C=10; p95=10581.0 ms at C=50).
      - **Root Cause**: Dominated by an unpaginated query returning 250+ historical records, double foreign populates (`patient`, `assignedDoctor`), and synchronous Node.js `crypto` AES-256-GCM decryption of patient PII (`name`, `phoneNumber`) on each populated document inside Mongoose hydration getters, blocking the single-threaded event loop.
    - **Empirical Triage Latency Profile**:
      - ML Bayesian Inference (internal proxy network): 1.79 ms (1.5%)
      - ReportLab Devanagari PDF Generation: 26.27 ms (21.7%)
      - Ingress / Express Middleware / DB Overhead: 92.88 ms (76.8%)
      - Total End-to-End Triage Latency (LLM Off): 120.94 ms (100.0%)

### Documented Operational Gaps & Draft Classifications
1. **Live Gemini LLM Quota**:
   - Google's free-tier quota for Gemini is strictly 20 requests/day per API project.
   - When quota is reached (HTTP 429 RESOURCE_EXHAUSTED), the system engages **Deterministic Clinical Fallback Mode** (`llmFallback: true`), using safe pre-compiled guidelines (`DISEASE_DRAFT_GUIDELINES`) with zero dosage claims.
2. **Official OWASP ZAP Baseline Scan — NOT RUN**:
   - Docker pull of `zaproxy/zap-stable` failed due to Docker host disk space exhaustion (`unexpected EOF`). Raw error captured in `docs/evidence/zap_pull_error.txt`.
   - Status remains strictly **NOT RUN** pending user moving Docker's disk image to Drive D:. Custom script labeled "10 custom basic checks" in `docs/evidence/custom_owasp_check_report.txt`.
3. **Clinical Red-Flag Rules — STATUS: DRAFT**:
   - 7 symptom red flags and 4 physiological vital thresholds trigger emergency escalation in `config/red_flags.yaml`.
   - Worker accept returns HTTP 409 `RED_FLAG_ACCEPT_BLOCKED`. Status remains **`status: DRAFT`**, awaiting clinician review.
   - Categorized 131 vocabulary symptoms and candidate unmapped emergency symptoms in `docs/RED_FLAG_REVIEW.md` without modifying `config/red_flags.yaml`.

---

## 2. Deliverables Matrix

| Phase | Item | Status | Evidence Record | Empirical Finding |
|---|---|---|---|---|
| **P0** | Prediction & Triage Remediation | `VERIFIED` | `docs/evidence/p0_docker_tests.txt` | Canned mock eliminated; 20 golden set cases pass; fail-closed 503 verified. |
| **P1** | Environment & Live Health | `VERIFIED` | `docs/evidence/p1_docker_rebuild.txt` | 6/6 containers healthy; live `/model-info` dynamically reports commit and metrics. |
| **P2** | Clinical Orchestration & Fallback | `VERIFIED` | `docs/evidence/gemini_live_run.txt` | Unified model `gemini-2.5-flash`; non-garbled regeneration filter verified; templates with 0 drug dosages. |
| **P3** | Technical Controls & Security | `VERIFIED` | `docs/evidence/p3_idempotency_http.txt`, `Backend/tests/encryption_key_exit.test.js` | 50-way idempotency deduplication; lease timeout SIGKILL recovery; HMAC blind index; production env exit test. |
| **P4** | UI Overhaul & Browser E2E | `VERIFIED` | `docs/evidence/playwright_report.txt` | 10 Playwright scenarios passed at https://localhost; 15 screenshots saved. |
| **P5** | Concurrency & Load Benchmarks | `VERIFIED` | `docs/evidence/load_test_testmode_results.txt`, `http_race_tests.txt` | >=200 req/endpoint across C=1, 10, 50 (0 failures for 401/429/5xx); 50-way atomic race: `{200: 1, 409: 49}`. |
| **P6** | Transport & Vulnerability Scans | `PARTIAL` | `docs/evidence/mitm_proxy_interception_demo.txt`, `trivy_all_images_scan.txt`, `zap_pull_error.txt` | Real MITM proxy demo passed; ZAP is NOT RUN; Trivy: Backend 0 vulns, 0 Criticals, Python images 2 High in pip vendored urllib3; Gitleaks clean. |
| **P7** | Master Documentation & QA | `VERIFIED` | `README.md`, `docs/VIVA_QA.md`, `docs/EVIDENCE_INDEX.md` | Reproduction script, 42-question viva guide, complete evidence mapping, RED_FLAG_REVIEW.md. |
| **P8** | Disinterested Subagent Audit | `VERIFIED` | `docs/evidence/independent_verifier_final_transcript.txt` | Independent verification subagent conducted objective audit without self-grading. |

---

## 3. Rate Limits & Concurrency Specifications

| Component | Policy | Window | Ceiling / Rate | Burst | Bypass Gating |
|---|---|---|---|---|---|
| **Edge Nginx (`/api/`)** | General API Limiting | 1 second | 15 req/sec | 50 requests (nodelay) | None (always active) |
| **Edge Nginx (`/api/v1/auth/`)** | Auth Brute-Force | 1 minute | 3 req/min | 5 requests (nodelay) | None (always active) |
| **Express Middleware** | General API Limiting | 1 minute | 150 req/min | N/A | Strictly rejected in production |
| **Express Middleware** | Auth Endpoints | 15 minutes | 15 req/15min | N/A | Strictly rejected in production |

---

## 4. Test Suite Execution Summary

Dynamically executed via `scripts/verify_all.ps1`:

```
============================================================
  ALL SUITES PASSED VERIFICATION
  Test Summary (Dynamically Parsed):
    - ML Tests:      55 passed (pytest ML_Model/tests/)
    - Backend Tests: 225 passed (npm --prefix Backend test)
    - Graph Tests:   22 passed (pytest graph/tests/)
    - UI Tests:      9 passed (pytest ui/tests/)
    - Total Tests:   311 passed (0 failed)
============================================================
```

---

## 5. Artifact Reference Index

- **Subagent Audit Report**: [`docs/evidence/subagent_audit_report.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/subagent_audit_report.txt)
- **MITM Proxy Interception Demo**: [`docs/evidence/mitm_proxy_interception_demo.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/mitm_proxy_interception_demo.txt)
- **HTTP Concurrency Race Proof**: [`docs/evidence/http_race_tests.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/http_race_tests.txt)
- **Trivy Image Scan**: [`docs/evidence/trivy_all_images_scan.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/trivy_all_images_scan.txt)
- **Trivy Image Scan Notes**: [`docs/evidence/trivy_all_images_scan_notes.md`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/trivy_all_images_scan_notes.md)
- **Load Test Results (Test Mode)**: [`docs/evidence/load_test_testmode_results.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/load_test_testmode_results.txt)
- **Load Test JSON Data**: [`docs/evidence/load_test_testmode_results.json`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/load_test_testmode_results.json)
- **Gemini Live Run**: [`docs/evidence/gemini_live_run.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/gemini_live_run.txt)
- **ZAP Pull Error**: [`docs/evidence/zap_pull_error.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/zap_pull_error.txt)
- **Custom 10 Basic Checks**: [`docs/evidence/custom_owasp_check_report.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/custom_owasp_check_report.txt)
- **Red Flag Review & Governance**: [`docs/RED_FLAG_REVIEW.md`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/RED_FLAG_REVIEW.md)
