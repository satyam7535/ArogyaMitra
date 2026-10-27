# ArogyaMitra — End-to-End Flow Trace

Living trace matrix tracking the 13 clinical flow steps defined in the v2 specification.
A step is **VERIFIED** only when executed against real running services, with raw outputs archived in `docs/evidence/` and mutation checks documented in `docs/evidence/mutation_checks.md`.

---

## 1. Flow Matrix

| Step | Flow Action | Status | Endpoint / UI Path | Request Payload / User Action | Response / Outcome | Evidence File & Line | Verified Against Code? |
|---|---|---|---|---|---|---|---|
| **0** | **Environment Baseline & Database Connectivity** | **VERIFIED** | MongoDB Atlas `arogyamitra_dev` & `http://127.0.0.1:5000/health` | `node src/scripts/seedDemo.js` | Database seeded with 2 orgs, 2 admins, 2 workers, 2 doctors, 3 patients, 2 consultations. Health check returns 200 on all 4 microservices. | [`docs/evidence/stage0_probes.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/stage0_probes.txt#L1)<br>[`docs/evidence/verify_all_initial.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/verify_all_initial.txt#L1) | YES — Real Atlas connection, real HTTP probes, 62 automated tests passing. |
| **1** | Admin login, adds health worker & medical officer | NOT STARTED | `POST /api/v1/admin/login`<br>`POST /api/v1/admin/worker`<br>`POST /api/v1/admin/doctor` | Admin credentials -> creates Worker & Doctor in admin's organization | JWT returned with role and orgId; Worker & Doctor created with org scoping. | Pending Stage 1 | Pending Stage 1 |
| **2** | Worker logs in, views empty dashboard | NOT STARTED | `POST /api/v1/worker/login`<br>`GET /api/v1/consultation/my` | Worker credentials | Returns 200 with worker's assigned consultations | Pending Stage 1 | Pending Stage 1 |
| **3** | Worker registers new patient with AES-256 encrypted PII & consent | NOT STARTED | `POST /api/v1/patient` | Full patient details + consent metadata | Encrypted phoneNumber/address/medicalHistory; audit logged | Pending Stage 2 | Pending Stage 2 |
| **4** | Cross-tenant access blocked (Worker 2 from Org 2 cannot read Patient 1) | NOT STARTED | `GET /api/v1/patient/:id`<br>`GET /api/v1/consultation/:id` | Worker 2 token on Org 1 records | Returns 404 Not Found (anti-enumeration) | [`docs/evidence/stage0_probes.txt:130`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/stage0_probes.txt#L130) | Baseline tested; Stage 1/2 will formalize automated gate. |
| **5** | Worker selects symptoms, verifies severity & dropout augmentation | NOT STARTED | `POST /api/v1/consultation/:id/analyze` | 3+ symptoms submitted for inference | TreeSHAP attributions and calibrated probabilities computed | Pending Stage 3 | Pending Stage 3 |
| **6** | Async job queue processing & polling | NOT STARTED | `POST /api/v1/consultation/:id/analyze/async`<br>`GET /api/v1/consultation/:id/analyze/status/:jobId` | Enqueue background analysis job | Returns 202 Accepted, polls to completion, durable queue | Pending Stage 4 | Pending Stage 4 |
| **7** | Safe LLM generation with strict fallback & no PII | NOT STARTED | LangGraph `llm_node` | Stripped non-PII medical context | Structured summary with clinical recommendations; deterministic fallback on failure | Pending Stage 4 | Pending Stage 4 |
| **8** | Multilingual PDF report generation (en, hi, mr) with TreeSHAP | NOT STARTED | LangGraph `report_node` | Binary PDF generation | Valid PDF with hospital banner, precautions, TreeSHAP explanation | [`docs/evidence/verify_all_initial.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/verify_all_initial.txt#L110) | Baseline test passed; Stage 4 will test live PDF generation. |
| **9** | Frontline Worker decision workflow (Accept / Escalate) | NOT STARTED | `PATCH /api/v1/consultation/:id/accept`<br>`PATCH /api/v1/consultation/:id/escalate` | Worker clinical decision with reason | Status updated to `accepted` or `escalated`; audited | Pending Stage 5 | Pending Stage 5 |
| **10** | Doctor review & second opinion response with OCC | NOT STARTED | `PATCH /api/v1/consultation/:id/respond` | Doctor diagnosis & prescription notes | Version incremented; concurrent conflict returns 409 Conflict | Pending Stage 5 | Pending Stage 5 |
| **11** | Streamlit thin-client UI workflow via Backend only | NOT STARTED | Streamlit UI (:8501) | Browser walkthrough of Triage & Review | Zero direct calls to :8000/:8001; no internal secret in UI | Pending Stage 6 | Pending Stage 6 |
| **12** | Admin operational dashboard & metrics | NOT STARTED | `GET /api/v1/admin/metrics`<br>`GET /api/v1/admin/audit-logs` | Admin metrics query | Disease distribution, escalation rate, audit trail with pagination | Pending Stage 7 | Pending Stage 7 |
| **13** | Concurrency, OCC conflict & transport security verification | NOT STARTED | Load test suites & HTTPS probes | 50 concurrent triage sessions; race conditions on second opinion | 100% data integrity; 409 Conflict on stale OCC writes; TLS/HSTS verified | Pending Stage 8-9 | Pending Stage 8-9 |

---

## 2. Stage 0 Verification Summary
- **Database**: MongoDB Atlas (`arogyamitra_dev`) verified active with IP access list configured.
- **Seeding**: Comprehensive seeder created 2 organizations (`PUNE-RHM`, `NASHIK-RHM`), 2 Admins, 2 Health Workers, 2 Doctors, 3 Patients, and 2 Consultations.
- **Probes**: All 11 security probes recorded in [`docs/evidence/stage0_probes.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/stage0_probes.txt):
  - Worker 1 login -> 200 OK with clean JWT and cookie
  - Worker 2 login -> 200 OK with clean Org 2 JWT and cookie
  - Doctor 1 login -> 200 OK
  - Admin 1 login -> 200 OK
  - Worker direct analysis write attempt -> 403 `DIRECT_ANALYSIS_WRITE_FORBIDDEN`
  - Cross-tenant read (Patient) -> 404 `Patient not found`
  - Cross-tenant read (Consultation) -> 404 `Consultation not found`
  - Legitimate same-tenant read -> 200 OK with decrypted PII
  - Mass assignment attempt -> 201 Created with auto-generated ID and server-pinned org
  - Unauthenticated ML call (:8000/predict) -> 401 `Missing internal service authentication token.`
  - Unauthenticated Graph call (:8001/analyze) -> 401 `Missing internal service authentication token.`
- **P0 Hotfixes Applied**:
  - Hotfix 1: Removed `resetToken` leak from `worker.service.js`, `admin.service.js`, `doctor.service.js`. Mutation check verified.
  - Hotfix 2: Bound ML service to `127.0.0.1` and added internal token verification dependency (`verify_internal_service_token`). Mutation check verified.
  - Hotfix 3: Updated `test_phase0.py` `test_symptoms_endpoint` to assert dictionary object structure.
  - Hotfix 4: Replaced `"AI Explanation (LIME)"` with `"AI Explanation (TreeSHAP)"` across en, hi, mr in `graph/utils/pdf_generator.py`. Mutation check verified.
- **Local Helper Scripts**: `setup_local.ps1/.sh`, `start_local.ps1/.sh`, `stop_local.ps1/.sh`, `health_check.ps1/.sh` tested and verified in [`docs/evidence/local_scripts_sanity.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/local_scripts_sanity.txt).
- **Verification Runner**: `scripts/verify_all.ps1` runs 62 automated tests across all suites with 100% green pass in [`docs/evidence/verify_all_initial.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/verify_all_initial.txt).
