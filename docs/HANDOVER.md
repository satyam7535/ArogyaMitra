# ArogyaMitra — Project Handover & Remediation Verification Dossier

**Date**: November 1, 2026  
**Branch**: `remediation`  
**Repository**: `https://github.com/satyam7535/ArogyaMitra.git`  
**System Status**: All 6 microservices healthy, 322/322 automated tests passing (100%), fail-closed clinical workflow operational end-to-end.

---

## 1. Executive Summary

This document summarizes the comprehensive remediation and formal report synthesis for **ArogyaMitra**, a privacy-first, explainable, and fail-closed AI-assisted primary healthcare clinical decision support system designed for rural frontline health workers.

All requirements across **Part A (Workflow Remediation & UI Verification)**, **Part B (Academic Report Generation & Verification)**, and **Part C (Final Quality Gate & Verification)** have been executed, empirically verified against live command outputs, and committed strictly to the `remediation` branch.

---

## 2. Part A: Clinical Workflow Defect Remediation & Verification

### 2.1 Workflow Defects Diagnosed & Remediated

| # | Clinical Workflow Defect | Root Cause Analysis | Remediation Fix Implemented | Verification Evidence |
|---|--------------------------|---------------------|-----------------------------|-----------------------|
| 1 | **Consultation not saved on worker escalation** | Backend Mongoose schema `status` enum permitted only `["pending", "completed", "cancelled"]`, rejecting `"escalated"` with validation error; patient auto-creation missed required `registeredBy` field. | Updated `consultation.model.js` enum to include `"escalated"`; added `registeredBy: req.user.id` on patient creation. | `scripts/test_p4_playwright_suite.mjs` (Scenario 3) & `scripts/test_part_a_workflow.mjs` (Step 2) |
| 2 | **Doctor review queue empty** | `ui/pages/2_Doctor_Review.py` used static `SAMPLE_PENDING_CASES` mock array that did not fetch escalated cases from backend API. | Replaced mock with live `api_client.get_pending_reviews()` querying `GET /api/v1/doctor/consultations/pending`. | `docs/evidence/ui_screenshots/07_doctor_queue_real.png` |
| 3 | **Doctor response & prescription not saved** | Consultation schema lacked `prescription` field under `secondOpinion`; concurrent submission caused 409 or 400 when status was closed. | Added `prescription` field to `secondOpinion` subdocument; added graceful handling for `ALREADY_REVIEWED` (409) and closed status. | `scripts/test_part_a_workflow.mjs` (Step 4) & `docs/evidence/ui_screenshots/08_doctor_response.png` |
| 4 | **Worker does not see reviewed status** | Worker consultation list lacked visual feedback for doctor second opinions and prescriptions. | Connected review pane to live backend consultation record, displaying physician notes, prescription, and confirmation status. | `docs/evidence/ui_screenshots/09_worker_reviewed.png` |
| 5 | **Session expired leaves worker stranded** | Streamlit held stale JWT in `st.session_state["token"]` on HTTP 401; repeated clicks flooded login endpoint resulting in HTTP 429. | Cleared token and cookies on 401, displayed re-authentication prompt, and added `login_failed` flag to prevent request loops. | `ui/tests/test_streamlit.py::test_ui_401_expired_session_handling` (PASS) |

### 2.2 Visual & End-to-End Proof
- **10 UI Screenshots Captured**: Stored in `docs/evidence/ui_screenshots/` (`01_worker_result.png` through `10_admin_audit_log.png`).
- **Composite Panel (Figure 4.5)**: Embedded in the final academic report, showing Worker Intake, Emergency Red-Flag Override, Live Doctor Review Queue, and Worker Reviewed View.
- **Multilingual Clinical PDFs**: Page 1 rasterized to PNG (`report_page1_hindi.png`, `report_page1_marathi.png`) via `pypdfium2`.
- **Backend Access Log Sample**: Real Apache/Nginx combined access log saved to `docs/evidence/backend_access_log_sample.txt`.
- **Playwright Suite**: 11/11 browser journeys passing (`node scripts/test_p4_playwright_suite.mjs`).

---

## 3. Part B: Academic Project Report Synthesis

### 3.1 Report Metrics & Verification
- **Generated PDF Path**: `docs/REPORT_FINAL/ArogyaMitra_BTech_Project_Report.pdf` (and `docs/REPORT/ArogyaMitra_BTech_Project_Report.pdf`).
- **Verified Page Count**: **36 Pages** (strictly within the 35–38 page target).
- **Generation Method**: Microsoft Word COM Automation (`win32com.client`) ensuring native typography, clean page breaks, and zero text collisions.
- **Rasterized Verification**: All 36 pages rendered to PNG in `docs/REPORT_FINAL/pdf_pages/` and inspected for formatting integrity.

### 3.2 Formal References & Citation Audit
- **Citation Pass Rate**: **100% PASS** on all 15 formal references `[1]` through `[15]` (`docs/evidence/report_citation_check.txt`).
- **Key Attributions**:
  - `[1]` Wallace et al. (2022) *npj Digital Medicine*: 10 studies, 48 symptom checkers, QUADAS-2, 19.0–37.9% diagnostic accuracy.
  - `[2]` Niculescu-Mizil & Caruana (2005) *ICML*: 10 supervised learning families; Naive Bayes pushes probabilities to 0 and 1.
  - **Platt Scaling Attribution**: Clearly identified as our independent empirical test on the 304 unique rows (log loss worsened from 0.0061 to 0.1643), not misattributed to literature.
  - `[9]` Kung & Robinson (1981): Optimistic Concurrency Control.
  - `[10]` Ribeiro et al. (2016): LIME local surrogate interpretability.
  - `[11]` DPDP Act 2023, `[12]` WHO 2021 Guidance, `[13]` ICMR 2023 Guidelines.

### 3.3 Empirical Latency & Model Performance Metrics
- **ML Inference Execution Time**: Measured directly inside the `arogya-ml` container across 200 iterations:
  - **Mean**: 10.72 ms
  - **p50**: 9.00 ms
  - **p95**: 18.47 ms
  - **p99**: 37.63 ms
  - **Min / Max**: 4.10 ms / 44.40 ms
  - **Saved Evidence**: `docs/evidence/ml_inference_latency.txt`
- **Model Accuracy vs. Dropout (5x3 Repeated Stratified K-Fold CV on 304 Unique Rows)**:
  - 0% Dropout: BernoulliNB **1.000 ± 0.000** | LightGBM **0.989** | XGBoost **0.984**
  - 30% Dropout: BernoulliNB **0.989 ± 0.014** | LightGBM **0.864** | XGBoost **0.868**
  - 50% Dropout: BernoulliNB **0.919 ± 0.023** | LightGBM **0.683** | XGBoost **0.720**
- **Load Test Results (2,400 Requests in Test Mode)**:
  - C=1: Throughput 5.2 req/s, p50 190.6 ms, 100% 200 OK
  - C=10: Throughput 11.2 req/s, p50 439.1 ms, 100% 200 OK
  - C=50: Throughput 14.7 req/s, p50 2314.9 ms, 100% 200 OK
- **Worker List Optimization (GET /consultation/my)**:
  - C=1: p50 reduced from 193.0 ms to 76.2 ms (60.5% speedup)
  - C=1: p99 reduced from 660.6 ms to 152.0 ms (77.0% speedup)

### 3.4 Prohibited Words & Neutral Tone Audit
- Verified **0 occurrences** of banned words (`sub-millisecond`, `proves`, `eliminated`, `guaranteed`, `physically impossible`, `enterprise-grade`, `state-of-the-art`) across report scripts, markdown reports, and README.
- Model scores consistently labeled as **"uncalibrated posterior estimates from Bernoulli Naive Bayes"**.
- Academic supervisor placeholders strictly preserved for candidate confirmation:
  - `[CONFIRM TITLE] Ashish Singh`
  - `[CONFIRM HOD NAME]`
  - `[CONFIRM DIRECTOR NAME]`

---

## 4. Part C: Verification & Quality Gate Summary

### 4.1 Automated Test Suite Breakdown (322 Tests Passing)
| Subsystem / Test Suite | Framework / Tool | Test Files | Tests Run | Pass Rate | Evidence Log |
|------------------------|------------------|------------|-----------|-----------|--------------|
| **Lint & Syntax Check** | Ruff / ESLint | 3 Subsystems | All Files | 0 Errors | `verify_all.ps1` output |
| **ML Inference & Safety Contracts** | Pytest / NumPy / Scikit-learn | 5 Files | 55 | 100% (55/55) | `docs/evidence/verify_ml.txt:47` |
| **Backend API, Auth & Concurrency** | Jest / Supertest | 13 Files | 231 | 100% (231/231) | `docs/evidence/verify_backend.txt:85` |
| **Guarded Graph, Timeout & Guardrails** | Pytest / LangGraph | 2 Files | 26 | 100% (26/26) | `docs/evidence/verify_graph.txt:32` |
| **Frontend UI Headless AppTest** | Pytest / Streamlit AppTest | 1 File | 10 | 100% (10/10) | `docs/evidence/verify_ui.txt:21` |
| **Total Prototype Suite** | **Multi-Framework** | **21 Files** | **322** | **100% (322/322)** | `powershell -File scripts/verify_all.ps1` |
| **Golden Set Evaluation** | Live Python HTTP Client | 1 File | 20 Cases | 100% (20/20) | `docs/evidence/p0_docker_tests.txt` |
| **Playwright Browser Journeys** | Playwright / Chromium | 1 Suite | 11 Journeys | 100% (11/11) | `docs/evidence/p4_playwright_suite.txt:72` |

### 4.2 Docker Container Health Status
All 6 services run as isolated containers on the `arogya-net` private bridge network:
- `arogya-proxy`: Nginx 1.27-alpine (healthy)
- `arogya-frontend`: Streamlit 1.66 / Python 3.11-slim (healthy)
- `arogya-backend`: Node 22-alpine / Express 5.2 (healthy)
- `arogya-ml`: Python 3.11-slim / FastAPI / Scikit-learn (healthy)
- `arogya-graph`: Python 3.11-slim / FastAPI / LangGraph (healthy)
- `arogya-mongo`: MongoDB 7.0 Community (healthy, internal only, no exposed host ports)

---

## 5. Reproduction Playbook

To replicate the complete environment, verify test suites, and rebuild the academic report:

```powershell
# 1. Start Docker microservice cluster
docker compose -f docker-compose.yml up -d
powershell -File scripts/health_check.ps1

# 2. Seed clean demo database
powershell -File scripts/seed_docker.ps1

# 3. Run complete automated test suite (322 tests)
powershell -File scripts/verify_all.ps1

# 4. Run Golden Clinical Set (20 cases)
python scripts/test_p0_golden_set.py

# 5. Run Playwright End-to-End Suite (11 browser journeys)
node scripts/test_p4_playwright_suite.mjs

# 6. Audit Citation Integrity (15 references)
python scripts/check_report_citations.py

# 7. Generate All Publication Figures
.venv\Scripts\python.exe scripts/generate_corrected_figures.py

# 8. Compile Complete Academic Report DOCX & PDF (Word COM)
python scripts/build_full_report.py
```

---

## 6. Known Structural Limitations

In compliance with engineering and clinical disclosure standards, the following 10 structural limitations are maintained in `docs/KNOWN_LIMITATIONS.md`:
1. **Synthetic Training Data**: 304 unique rows across 41 classes derived by deduplicating a 4,920-row public dataset (93.8% duplicate rate). No real patient EHR cohort validation.
2. **Conditional Feature Independence**: Correlated symptoms multiply likelihoods, pushing posterior confidence to extremes.
3. **Uncalibrated Model Confidence**: Scores represent relative ranking log-odds, not true empirical probabilities.
4. **Frontline Decision Support Scope**: Assistive screening tool; does not replace physician diagnosis or laboratory testing.
5. **Deterministic Safe Mode Default**: Due to external Gemini API rate limits and deprecation cycles, deterministic fallback templates represent the primary execution path.
6. **Draft Clinical Templates**: Fallback templates remain labeled DRAFT pending review by a licensed medical board.
7. **Self-Signed TLS Certificate**: Gateway uses self-signed certificate for `arogyamitra.local`.
8. **Single-Replica Deployment**: Single-host Docker Compose deployment without Kubernetes multi-node clustering.
9. **In-Memory Rate Limiting**: Quota counters reside in Node.js process memory rather than shared Redis.
10. **Devanagari PDF Typography**: ReportLab lacks HarfBuzz complex shaping, occasionally mispositioning Hindi/Marathi vowel matras.

---
*Signed off by Engineering Team — Remediation Branch — November 1, 2026*
