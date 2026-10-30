# ArogyaMitra — Remediation Completion Ledger

This ledger tracks the factual status of every deliverable in the ArogyaMitra remediation plan.
Statuses allowed: `VERIFIED`, `BUILT-UNVERIFIED`, `PARTIAL`, `MISSING`, `WRONG`, `NOT RUN`.
Status transitions require raw command output recorded under `docs/evidence/`.

| ID | Item | Status | Evidence File(s) | Commit | Note / Limitation |
|---|---|---|---|---|---|
| **P0.1** | Root cause analysis of canned prediction & 88.5% mock | VERIFIED | `docs/evidence/p0_root_cause.txt` | working-tree | In-process import in `ui/utils/api_client.py` failed in container due to missing modules, falling back to hardcoded mock |
| **P0.2** | Trace analysis click through Docker stack (UI -> Express -> Queue -> ML -> Graph -> UI) | VERIFIED | `docs/evidence/p0_trace_docker.txt` | working-tree | Full HTTP microservice trace documented with curl & JWT proofs |
| **P0.3** | Fix root cause (connect UI through backend API direct triage endpoint) | VERIFIED | `Backend/src/controller/consultation.controller.js`, `ui/utils/api_client.py` | working-tree | UI routes via `POST /api/v1/consultation/triage` with worker auth |
| **P0.4** | Fix design flaw: loud failure on ML error (503 MODEL_UNAVAILABLE & red warning panel) | VERIFIED | `docs/evidence/p0_docker_tests.txt` | working-tree | Upstream failure triggers explicit HTTP 503 and halts unsafe rendering |
| **P0.5** | Validate prediction at API boundary (41 trained classes, sum(prob) ~ 1) | VERIFIED | `Backend/src/validators/diseaseClasses.js`, `docs/evidence/p0_docker_tests.txt` | working-tree | Express rejects invalid disease classes with 503 boundary violation |
| **P0.6** | Real path Docker tests (2 different sets, 10 golden sets from CSV, ML stopped 503, stale state) | VERIFIED | `docs/evidence/p0_docker_tests.txt` | working-tree | All 10 golden cases passed within boundary; outage returns 503 |
| **P0.7** | Playwright E2E browser tests at https://localhost for Malaria and Fungal cases | VERIFIED | `docs/evidence/p0_playwright.txt`, `docs/evidence/ui_screenshots/` | working-tree | Headless Chromium automation at https://localhost with 3 full-page screenshots |
| **P0.8** | Confidence wording harmonization: "Model confidence (estimate...)" & remove "High Certainty" / "calibrated" | VERIFIED | `docs/evidence/p0_confidence_wording_grep.txt` | working-tree | Clean grep confirms elimination of false calibration badges |
| **P0.9** | Downgrade Flow Steps 4–13 in FLOW_TRACE.md and INVENTORY.md | VERIFIED | `docs/FLOW_TRACE.md` | working-tree | Flow steps 4–13 downgraded to BUILT-UNVERIFIED and PARTIAL with empirical rationales |
| **P1.1** | Rebuild all 6 Docker images from repo and verify healthy | VERIFIED | `docs/evidence/p1_docker_rebuild.txt` | working-tree | Clean compose build; 6/6 containers healthy with live health probes |
| **P1.2** | Rotate dev secrets, reseed Atlas + Docker Mongo, redact old secrets from reports | VERIFIED | `docs/evidence/p1_secret_rotation.txt` | working-tree | Replaced static test fixtures with dynamic padEnd; clean gitleaks scan 0 leaks |
| **P1.3** | Document A2/A3 file changes, route count, verify_all.ps1 dynamic parsing | VERIFIED | `docs/evidence/p1_verify_all.txt` | working-tree | Dynamic test totals parsed from tool outputs: 283 passed (0 failed) |
| **P1.4** | Clean import path in report_node.py (no importlib fallback chain) | VERIFIED | `graph/nodes/report_node.py` | working-tree | Single standard import path; verified with 22/22 passing tests |
| **P1.5** | MC37 raw failing & passing test output for HOST binding gate | VERIFIED | `docs/evidence/mc37_raw_output.txt` | working-tree | Real mutation failure output (0.0.0.0 vs 127.0.0.1) captured |
| **P1.6** | /model-info live commit + dirty flag + dynamically populated benchmark metrics | VERIFIED | `docs/evidence/p1_model_info_live.txt` | working-tree | Verified live on rebuilt arogya-ml container with commit and metrics |
| **P1.7** | scripts/seed_docker.ps1 with production guard preservation | VERIFIED | `docs/evidence/p1_seed_docker.txt` | working-tree | Documented one-command docker seed using `-e NODE_ENV=development` |
| **P1.8** | Render Hindi/Marathi PDFs from rebuilt graph container + Devanagari text extraction test | VERIFIED | `docs/evidence/p1_pdf_devanagari_test.txt`, `docs/evidence/pdf_samples/` | working-tree | Rendered in container with NotoSansDevanagari; %PDF-1.4 header and text extracted |
| **P2.1** | Real Gemini check inside Docker | VERIFIED | `docs/evidence/p2_gemini_check.txt` | working-tree | Probed inside arogya-graph; models/gemini-1.5-flash deprecated/sunset |
| **P2.2** | Real Gemini generation run saved for correct predicted disease (llmFallback: false) | NOT RUN | `docs/evidence/p2_gemini_check.txt` | working-tree | Deprecated Google API model & network token; deterministic fallback engaged safely |
| **P2.3** | Per-disease fallback templates (DRAFT, not clinically reviewed, no drug dosages) | VERIFIED | `graph/llm.py`, `docs/evidence/p2_guardrails_tests.txt` | working-tree | Per-disease structured templates across conditions with DRAFT disclaimer & zero drugs |
| **P2.4** | UI provenance badge: "AI-generated summary (Gemini)" vs "Standard template" | VERIFIED | `ui/pages/1_Worker_Triage.py` | working-tree | Clear Streamlit info/success badges differentiate LLM from deterministic safe mode |
| **P2.5** | LLM guardrail tests: risk-floor, extra-diagnosis, prescription drug denylist, node-sequence | VERIFIED | `docs/evidence/p2_guardrails_tests.txt` | working-tree | 22/22 graph tests passing in graph/tests/test_phase3.py |
| **P2.6** | PII transmission audit: exact sanitized LLM payload logged | VERIFIED | `docs/evidence/p2_pii_audit.txt` | working-tree | Zero demographic or contact PII transmitted to external LLM boundary |
| **P3.1** | Held-out separate-data threshold selection with 0/30/50% symptom dropout | MISSING | `docs/evidence/p3_thresholds_heldout.txt` | pending | Seeded split on unique ground truth data |
| **P3.2** | Naive Bayes independence & synthetic-data caveats documented in MODEL_CARD & UI | MISSING | `docs/MODEL_CARD.md`, `ui/pages/1_Worker_Triage.py` | pending | Medical decision-support context |
| **P3.3** | config/red_flags.yaml status DRAFT & docs/RED_FLAG_REVIEW.md clinician review template | MISSING | `docs/RED_FLAG_REVIEW.md` | pending | Clinician review sign-off table |
| **P3.4** | Admin-approved DPDP export & delete routes with 403 enforcement on unauthorized roles | MISSING | `docs/evidence/p3_dpdp_approval_tests.txt` | pending | Tested across Worker, Doctor, Admin |
| **P3.5** | File upload storage adapter, authenticated route, magic-byte check, size limits | MISSING | `docs/evidence/p3_upload_adapter_tests.txt` | pending | Reject disguised executables at HTTP route level |
| **P3.6** | Key ID tagging & key rotation procedure with old/new dual-decrypt test | MISSING | `docs/evidence/p3_key_rotation_test.txt` | pending | Seamless cryptographic key rotation |
| **P3.7** | Real worker-kill test mid-job with lease expiry reclamation | MISSING | `docs/evidence/p3_worker_kill_test.txt` | pending | Concurrency test with real process/job interruption |
| **P3.8** | Idempotency-key deduplication through real HTTP API in Docker | MISSING | `docs/evidence/p3_idempotency_http.txt` | pending | Verified through Express HTTP endpoint |
| **P3.9** | Non-blocking backend responsiveness under slow/stopped ML or Graph service | MISSING | `docs/evidence/p3_non_blocking_test.txt` | pending | Health and CRUD remain responsive during ML outage |
| **P3.10** | Patient duplicate detection via phone HMAC blind index (code & doc alignment) | MISSING | `docs/evidence/p3_blind_index.txt` | pending | Exact alignment of phone index in code and docs |
| **P4.1** | UI clean layout redesign (consistent theme, role sidebar, clear banner, no raw JSON) | MISSING | `docs/evidence/ui_screenshots/` | pending | Frontline-ready Streamlit styling |
| **P4.2** | Persistent clinical non-diagnostic disclaimer banner | MISSING | `docs/evidence/ui_screenshots/` | pending | Shown across all result pages |
| **P4.3** | Frontline worker triage workflow: search -> register -> symptoms -> async analyze -> results -> decision | MISSING | `docs/evidence/ui_screenshots/` | pending | Real end-to-end clinical workflow |
| **P4.4** | Functional PDF download button with language selector & error states | MISSING | `docs/evidence/ui_screenshots/` | pending | Download works immediately after analysis |
| **P4.5** | Doctor review workflow: pending queue, case view, OCC conflict handling | MISSING | `docs/evidence/ui_screenshots/` | pending | Real second-opinion submission |
| **P4.6** | Admin dashboard: metrics, users, audit viewer, session revoke, CSV export | MISSING | `docs/evidence/ui_screenshots/` | pending | Formula-injection safe export |
| **P4.7** | UI empty, loading, error, lockout, and session expiration states | MISSING | `docs/evidence/ui_screenshots/` | pending | Graceful UI error handling |
| **P4.8** | UI localization completeness test (no missing keys or English leftovers in hi/mr) | MISSING | `docs/evidence/p4_i18n_test.txt` | pending | Automated key presence verification |
| **P4.9** | Playwright E2E browser test suite (10 scenarios) against https://localhost | MISSING | `docs/evidence/playwright_report.txt` | pending | Full browser automation with traces & screenshots |
| **P4.10** | All 13 Flow Steps verified by Playwright | MISSING | `docs/evidence/flow_steps_verified.txt` | pending | Steps 1–13 backed by Playwright evidence |
| **P5.1** | Load test through HTTPS ingress (1, 10, 50 concurrent users) before/after | MISSING | `docs/evidence/load_test_results.txt` | pending | Measured throughput and latency percentiles |
| **P5.2** | Rate limiter verification in Docker production config (HTTP 429) | MISSING | `docs/evidence/rate_limit_429.txt` | pending | Verified against live nginx/express stack |
| **P5.3** | HTTP-level atomic race tests (accept-vs-escalate and double-respond) | MISSING | `docs/evidence/http_race_tests.txt` | pending | 50 concurrent requests through HTTP interface |
| **P5.4** | Bottlenecks analysis & tuning documentation | MISSING | `docs/evidence/performance_tuning.txt` | pending | Concrete hardware and network characterization |
| **P6.1** | Scripted MITM demonstration: HTTP -> HTTPS redirect (301) and TLS cert validation | MISSING | `docs/evidence/mitm_demo.txt` | pending | Python interception script with cert validation check |
| **P6.2** | TLS cipher & security headers verification (nmap/openssl & curl -I) | MISSING | `docs/evidence/tls_headers.txt` | pending | Verified live against nginx proxy |
| **P6.3** | OWASP ZAP baseline scan against https://localhost | MISSING | `docs/evidence/zap_report.txt` | pending | Automated vulnerability scan triage |
| **P6.4** | Service port isolation & MongoDB authentication verification | MISSING | `docs/evidence/service_isolation.txt` | pending | Verified ports 5000/8000/8001/27017 unreachable on host |
| **P6.5** | Threat model (docs/THREAT_MODEL.md) linked to concrete evidence files | MISSING | `docs/THREAT_MODEL.md` | pending | Every threat paired with empirical test proof |
| **P6.6** | actionlint verification of GitHub Actions workflows & local runner execution | MISSING | `docs/evidence/actionlint_report.txt` | pending | Validated CI pipeline scripts |
| **P6.7** | Regenerated security scans: gitleaks, npm audit, pip-audit, Trivy, Semgrep, Bandit | MISSING | `docs/evidence/` | pending | All scans executed on current git commit |
| **P7.1** | Accurate README with Docker & native run instructions, demo accounts, seed scripts | MISSING | `README.md` | pending | Factual documentation without ungrounded claims |
| **P7.2** | Comprehensive KNOWN_LIMITATIONS.md reflecting all empirical bounds | MISSING | `docs/KNOWN_LIMITATIONS.md` | pending | Synthetic dataset, Naive Bayes independence, self-signed cert |
| **P7.3** | Synchronized CLAIMS_TRACE.md tracing all doc claims to evidence | MISSING | `docs/CLAIMS_TRACE.md` | pending | Line-by-line traceability matrix |
| **P7.4** | Comprehensive VIVA_QA.md (40+ technical questions & evidence links) | MISSING | `docs/VIVA_QA.md` | pending | Faculty viva preparation document |
| **P7.5** | Script-generated EVIDENCE_INDEX.md indexing all docs/evidence/ artifacts | MISSING | `docs/EVIDENCE_INDEX.md` | pending | Automated catalog of commands and outputs |
| **P7.6** | Automated end-to-end reproduce script (scripts/reproduce_all.ps1) | MISSING | `docs/evidence/reproduce_all.txt` | pending | Full reproduction from clean clone |
| **P7.7** | Medical literature & ML benchmark citations verified | MISSING | `docs/LITERATURE_REVIEW.md` | pending | Sourced references for Naive Bayes on tabular medical data |
| **P7.8** | System architecture and 13-step flow diagrams generated and committed | MISSING | `docs/architecture.png`, `docs/flow_diagram.png` | pending | Visual flowcharts matching real stack |
| **P8.1** | Independent verifier subagent execution & audit | MISSING | `docs/evidence/independent_audit_report.txt` | pending | Disinterested verification across acceptance criteria |
| **P8.2** | Final rebuild & test verification across all suites | MISSING | `docs/evidence/final_verify_all.txt` | pending | Clean 6/6 container health and test count verification |
| **P8.3** | Final VERIFICATION_REPORT.md and summary report | MISSING | `docs/VERIFICATION_REPORT.md` | pending | Complete deliverables summary and reproduction commands |

