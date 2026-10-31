# [HISTORICAL] ArogyaMitra — Truth Audit Matrix (`docs/AUDIT.md`)

> [!NOTE]
> **HISTORICAL ARCHIVE**: This document is an immutable historical audit record from earlier remediation phases.
> For the current, active, and comprehensive verification status across all system requirements, refer to the canonical [`docs/COMPLETION_LEDGER.md`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/COMPLETION_LEDGER.md) and [`docs/VERIFICATION_REPORT.md`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/VERIFICATION_REPORT.md).

This audit document evaluates every task and gate across Phases 0 through 7 against strict evidentiary standards:
- **PASS**: Verified by real command execution and evidence output file in this repository.
- **PARTIAL**: Partially implemented or verified, with documented gaps, limitations, or unverified edge cases.
- **FAIL**: Claimed to be functional, but broken, untested, or contradicts empirical results.
- **NOT RUN / NOT DONE**: Required by the specification, but never executed, implemented, or tested.

---

## Audit Table (Tasks 0.1 – 7.4 & Gates 0 – 7)

| Item | Description | Status | Evidence File / Reason |
| :--- | :--- | :---: | :--- |
| **Task 0.1** | Docs scaffolding, .editorconfig, .gitignore | **PASS** | `.editorconfig`, `.gitignore`, `docs/` |
| **Task 0.2** | Reconstruct ML_Model/app.py & prediction contract | **PASS** | [`docs/evidence/phase0_ml_contract.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/phase0_ml_contract.txt), `ML_Model/app.py` |
| **Task 0.3** | Dataset documentation script | **PASS** | `ML_Model/scripts/download_dataset.md` |
| **Task 0.4** | Remove dead and boilerplate code | **PASS** | Git commits: deleted `Frontend/src/App.jsx`, unused `express-session` |
| **Task 0.5** | Docker Compose stack with health checks | **NOT RUN** | Docker daemon was never launched due to host C: drive storage exhaustion. |
| **Task 0.6** | Update README with accurate paths & Mermaid | **PASS** | `README.md` |
| **Task 0.7** | Pin dependency versions | **PASS** | `Backend/package.json`, `ML_Model/requirements.txt`, `graph/requirements.txt` |
| **Gate 0** | Baseline & Hygiene Gate | **PARTIAL** | Core microservice and contract passed; Docker compose was NOT RUN. |
| **Task 1.1** | Data hygiene, deduplication, & augmentation | **PASS** | `ML_Model/training/prepare_data.py` (304 unique rows, normalized typos) |
| **Task 1.2** | Empirical benchmark of 6 model families | **PASS** | [`docs/evidence/model_benchmark.md`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/model_benchmark.md), [`model_benchmark.csv`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/model_benchmark.csv) |
| **Task 1.3** | Bayesian optimization & artifact export | **PASS** | `ML_Model/model/v1/` |
| **Task 1.4** | Reliability calibration & diagnostic report | **PARTIAL** | [`docs/evidence/calibration_reliability.png`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/calibration_reliability.png). Calibration evaluated in-sample/simple split; out-of-fold nested calibration audit pending (Stage C). |
| **Task 1.5** | Production ML microservice upgrade | **PASS** | `ML_Model/app.py` |
| **Task 1.6** | Model Card documentation | **PARTIAL** | `docs/MODEL_CARD.md` incorrectly claimed 42 classes instead of 41, and contained unverified claims. |
| **Task 1.7** | Phase 1 automated test suite | **PASS** | [`docs/evidence/verify_ml.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/verify_ml.txt) (9 / 9 passed) |
| **Gate 1** | ML & Calibration Gate | **PARTIAL** | Benchmark and contract passed; calibration out-of-fold audit and class count correction pending. |
| **Task 2.1** | Central validated config with Zod | **PASS** | `Backend/src/config/serverConfig.js` (hardcoded defaults removed in Stage A) |
| **Task 2.2** | Multi-tenant organization scoping & anti-enumeration | **PASS** | `Backend/src/middlewares/orgScope.middleware.js`, [`docs/evidence/verify_backend.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/verify_backend.txt) |
| **Task 2.3** | Authentication hardening (Argon2id, lockout, refresh token rotation, CLI seedAdmin) | **PASS** | `Backend/src/utils/crypto.js`, `Backend/src/service/auth.service.js`, [`docs/evidence/verify_backend.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/verify_backend.txt) |
| **Task 2.4** | HTTP security suite (Helmet, rate limits, NoSQL injection sanitizer) | **PASS** | `Backend/src/middlewares/security.middleware.js`, [`docs/evidence/verify_backend.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/verify_backend.txt) |
| **Task 2.5** | Field-level AES-256-GCM encryption & audit logging | **PASS** | `Backend/src/models/patient/patientSchema.js`, `Backend/src/models/audit/auditLogSchema.js`, [`docs/evidence/verify_backend.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/verify_backend.txt) |
| **Task 2.6** | Security test suite & evidence | **PASS** | [`docs/evidence/verify_backend.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/verify_backend.txt) (19 / 19 security tests passed) |
| **Phase 2 Gap** | Forgot/reset password email delivery, CSRF, upload magic bytes, signed Cloudinary URLs | **NOT DONE** | Mentioned in prompt but omitted from initial implementation; scheduled for Stage D. |
| **Gate 2** | Security & Scoping Gate | **PARTIAL** | Core auth, crypto, and tenant isolation verified (19/19); upload validation and CSRF missing. |
| **Task 3.1** | Server-side AI orchestration endpoint | **PASS** | `Backend/src/routes/consultation.routes.js`, `Backend/src/controllers/consultation.controller.js` |
| **Task 3.2** | Inter-service JWT authentication | **PASS** | `Backend/src/service/consultation.service.js`, `graph/server.py`, [`docs/evidence/verify_graph.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/verify_graph.txt) |
| **Task 3.3** | Safe LLM orchestrator & prompt injection defense | **PASS** | `graph/llm.py`, [`docs/evidence/verify_graph.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/verify_graph.txt) |
| **Task 3.4** | Deterministic clinical fallback & multilingual support | **PASS** | `graph/llm.py`, [`docs/evidence/verify_graph.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/verify_graph.txt) |
| **Task 3.5** | Multilingual ReportLab PDF generation | **PARTIAL** | `graph/utils/pdf_generator.py` uses OS system fonts; bundled Noto Sans Devanagari font is missing; visual glyph verification pending (Stage E). |
| **Task 3.6** | Phase 3 automated test suite & evidence | **PASS** | [`docs/evidence/verify_graph.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/verify_graph.txt) (12 / 12 passed) |
| **Gate 3** | Clinical Reasoning & Fallback Gate | **PARTIAL** | Automated pipeline logic passes; bundled Devanagari font and visual rendering checks pending. |
| **Task 4.1** | Asynchronous analysis job queue | **PARTIAL** | `Backend/src/service/jobQueue.service.js` implemented an in-memory queue, not Redis. Jobs do not survive restarts. |
| **Task 4.2** | Optimistic concurrency control (`__v`, VersionError) | **PASS** | `Backend/src/models/consultation/consultationSchema.js`, [`docs/evidence/verify_backend.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/verify_backend.txt) |
| **Task 4.3** | Non-blocking microservice connection pooling | **PASS** | `graph/nodes/xai_node.py` (persistent `httpx.Client`) |
| **Task 4.4** | Concurrency test suite | **PASS** | [`docs/evidence/verify_backend.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/verify_backend.txt) (7 / 7 concurrency tests passed) |
| **Task 4.5** | Empirical load test benchmark | **PARTIAL** | [`docs/evidence/load_test.md`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/load_test.md). Flat throughput (~13 req/s) with latency scaling linearly indicates single-threaded queueing. No Locust/k6 benchmark. |
| **Gate 4** | High-Throughput Concurrency Gate | **PARTIAL** | OCC works; in-memory queue is non-durable and serialized under load. Scheduled for overhaul in Stage F. |
| **Task 5.1** | Threat modeling with STRIDE framework | **PARTIAL** | `docs/THREAT_MODEL.md` created as descriptive text; not linked to dynamic scanners or packet captures. |
| **Task 5.2** | Production edge reverse proxy configuration | **PARTIAL** | `deploy/nginx.conf` created as text; never verified with live TLS termination or sslyze. |
| **Task 5.3** | MITM packet capture demonstration | **FAIL / NOT RUN** | `docs/evidence/mitm_demo.md` was written as prose; no real wireshark/tcpdump/mitmproxy pcap captured. |
| **Task 5.4** | DPDP Act 2023 compliance | **PASS** | `docs/PRIVACY.md` |
| **Task 5.5** | Automated security and dependency audit | **PARTIAL** | `npm audit fix` ran, but Trivy, Semgrep, ZAP, Bandit were NOT RUN. |
| **Gate 5** | Infrastructure Security Gate | **FAIL** | Text artifacts were produced without real dynamic scanning, packet captures, or live TLS validation. |
| **Task 6.1** | Move legacy React frontend to `legacy/frontend` | **PASS** | `legacy/frontend/` preserved with git history. |
| **Task 6.2** | Build multi-page Streamlit healthcare application | **PASS** | `ui/Home.py`, `ui/pages/1_Worker_Triage.py`, `ui/pages/2_Doctor_Review.py`, `ui/pages/3_Admin_Dashboard.py` |
| **Task 6.3** | Streamlit multilingual localization (en, hi, mr) | **PASS** | `ui/utils/i18n.py` |
| **Task 6.4** | Resilient client adapter & containerization | **PASS** | `ui/utils/api_client.py`, `ui/Dockerfile` |
| **Task 6.5** | Streamlit AppTest test suite & evidence | **PASS** | [`docs/evidence/verify_ui.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/verify_ui.txt) (6 / 6 passed) |
| **Phase 6 Gap** | Full 3-role auth parity, patient registration, Playwright E2E | **NOT RUN** | Live auth against Express backend, role guards, and browser E2E tests pending (Stage H). |
| **Gate 6** | Streamlit Interface Gate | **PARTIAL** | Headless AppTests pass; live backend parity and Playwright tests pending. |
| **Task 7.1** | Continuous Integration workflow | **PARTIAL** | `.github/workflows/ci.yml` authored, but not verified on a live runner. |
| **Task 7.2** | Demo data seeding script | **PASS** | `Backend/src/scripts/seedDemo.js` |
| **Task 7.3** | Academic documentation suite | **PARTIAL** | Generated in a single pass; literature citations, claims, and numbers must be traced to raw evidence. |
| **Task 7.4** | Master evidence index | **PARTIAL** | `docs/EVIDENCE_INDEX.md` indexed previous text and test outputs; needs cleanup of unverified claims. |
| **Task 7.5** | Viva Q&A prep document | **PARTIAL** | `docs/VIVA_QA.md` authored, but contains unverified claims (e.g. 42 diseases, enterprise-grade calibration); scheduled for audit & scrub in Stage I. |
| **Task 7.6** | Live demo script | **PARTIAL** | `docs/DEMO.md` authored; relies on unverified live Docker stack and placeholder IDs; needs verification in Stage I. |
| **Task 7.7** | Operations runbook | **PARTIAL** | `docs/OPERATIONS.md` documents deployment, backup, and restore procedures; Docker deployment untested due to host C: drive storage limit. |
| **Task 7.8** | Testing guide | **PASS** | `docs/TESTING.md` accurately documents test runners, unit/integration suites, and mock structures. |
| **Task 7.9** | Release tagging and final verification | **PARTIAL** | Premature `v1.0.0` tag renamed to `v0.9-unreviewed` on branch `remediation`; final tagging deferred until Stage J passes all gates. |
| **Gate 7** | Academic Deliverables Gate | **PARTIAL** | Deliverable documents drafted; claims tracing, citation verification, and Docker operations testing required. |
