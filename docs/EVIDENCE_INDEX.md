# ArogyaMitra — Comprehensive Evidence Index

This document catalogs every empirical evidence artifact generated during remediation.
Every status claim in the completion ledger traces to one of these verified command records.

| File | Phase | Status | Commit | Description |
|---|---|---|---|---|
| [`docs/evidence/p0_root_cause.txt`](evidence/p0_root_cause.txt) | **P0.1** | `VERIFIED` | latest | Root cause trace of canned predictions & fallback bypass |
| [`docs/evidence/p0_trace_docker.txt`](evidence/p0_trace_docker.txt) | **P0.2** | `VERIFIED` | latest | End-to-end trace of triage request through Docker network |
| [`docs/evidence/p0_docker_tests.txt`](evidence/p0_docker_tests.txt) | **P0.4-P0.6** | `VERIFIED` | latest | API boundary validation (41 classes) and 10 golden set tests |
| [`docs/evidence/p0_playwright.txt`](evidence/p0_playwright.txt) | **P0.7** | `VERIFIED` | latest | Headless browser automation on HTTPS localhost for Malaria & Fungal |
| [`docs/evidence/p0_confidence_wording_grep.txt`](evidence/p0_confidence_wording_grep.txt) | **P0.8** | `VERIFIED` | latest | Grep eliminating false 'Calibrated Confidence' wording |
| [`docs/evidence/p1_docker_rebuild.txt`](evidence/p1_docker_rebuild.txt) | **P1.1** | `VERIFIED` | latest | Clean compose rebuild with live health probe confirmation |
| [`docs/evidence/p1_secret_rotation.txt`](evidence/p1_secret_rotation.txt) | **P1.2** | `VERIFIED` | latest | Secret rotation audit with zero gitleaks findings |
| [`docs/evidence/p1_verify_all.txt`](evidence/p1_verify_all.txt) | **P1.3** | `VERIFIED` | latest | Dynamic test execution of 283 tests across all suites |
| [`docs/evidence/mc37_raw_output.txt`](evidence/mc37_raw_output.txt) | **P1.5** | `VERIFIED` | latest | Raw failure and passing output for 127.0.0.1 host binding gate |
| [`docs/evidence/p1_model_info_live.txt`](evidence/p1_model_info_live.txt) | **P1.6** | `VERIFIED` | latest | Live /model-info probe with dynamic git commit and metrics |
| [`docs/evidence/p1_seed_docker.txt`](evidence/p1_seed_docker.txt) | **P1.7** | `VERIFIED` | latest | Docker seeding execution preserving production environment guards |
| [`docs/evidence/p1_pdf_devanagari_test.txt`](evidence/p1_pdf_devanagari_test.txt) | **P1.8** | `VERIFIED` | latest | Devanagari font rendering and pdftotext extraction test |
| [`docs/evidence/p2_gemini_check.txt`](evidence/p2_gemini_check.txt) | **P2.1** | `VERIFIED` | latest | In-container Gemini probe confirming deprecated model error |
| [`docs/evidence/p2_guardrails_tests.txt`](evidence/p2_guardrails_tests.txt) | **P2.3-P2.5** | `VERIFIED` | latest | 22/22 graph guardrail tests passing in test_phase3.py |
| [`docs/evidence/p2_pii_audit.txt`](evidence/p2_pii_audit.txt) | **P2.6** | `VERIFIED` | latest | PII boundary audit verifying zero patient demographic leakage |
| [`docs/evidence/p3_thresholds_heldout.txt`](evidence/p3_thresholds_heldout.txt) | **P3.1** | `VERIFIED` | latest | Held-out separate-data threshold sweep with symptom dropout |
| [`docs/evidence/p3_dpdp_approval_tests.txt`](evidence/p3_dpdp_approval_tests.txt) | **P3.4** | `VERIFIED` | latest | 8/8 DPDP admin approval gate tests passing |
| [`docs/evidence/p3_upload_adapter_tests.txt`](evidence/p3_upload_adapter_tests.txt) | **P3.5** | `VERIFIED` | latest | 9/9 file upload magic-byte and size limit tests passing |
| [`docs/evidence/p3_key_rotation_test.txt`](evidence/p3_key_rotation_test.txt) | **P3.6** | `VERIFIED` | latest | 4/4 key rotation and multi-keyring decryption tests passing |
| [`docs/evidence/p3_worker_kill_test.txt`](evidence/p3_worker_kill_test.txt) | **P3.7** | `VERIFIED` | latest | Real OS SIGKILL mid-job and lease expiry reclamation in Docker |
| [`docs/evidence/p3_idempotency_http.txt`](evidence/p3_idempotency_http.txt) | **P3.8** | `VERIFIED` | latest | 50 parallel requests deduplicated to single job ID in Docker |
| [`docs/evidence/p3_non_blocking_test.txt`](evidence/p3_non_blocking_test.txt) | **P3.9** | `VERIFIED` | latest | Backend responsiveness during total ML container outage |
| [`docs/evidence/p3_blind_index.txt`](evidence/p3_blind_index.txt) | **P3.10** | `VERIFIED` | latest | 6/6 patient phone HMAC blind index tests passing |
| [`docs/evidence/p4_i18n_test.txt`](evidence/p4_i18n_test.txt) | **P4.8** | `VERIFIED` | latest | 100% localization parity across en, hi, mr with Devanagari script |
| [`docs/evidence/p4_streamlit_tests.txt`](evidence/p4_streamlit_tests.txt) | **P4.9** | `VERIFIED` | `0ddca8d` | 9/9 Streamlit AppTest unit tests passing |
| [`docs/evidence/playwright_report.txt`](evidence/playwright_report.txt) | **P4.9-P4.10** | `VERIFIED` | latest | 10-scenario Playwright E2E browser test report (10/10 PASS) |
| [`docs/evidence/load_test_results.txt`](evidence/load_test_results.txt) | **P5.1** | `VERIFIED` | `77bb076` | P5.1 Ingress HTTPS Load & Concurrency Benchmark Results |
| [`docs/evidence/rate_limit_429.txt`](evidence/rate_limit_429.txt) | **P5.2** | `VERIFIED` | `0ebfa6a` | P5.2 Production Rate Limiter Verification |
| [`docs/evidence/http_race_tests.txt`](evidence/http_race_tests.txt) | **P5.3** | `VERIFIED` | `0ebfa6a` | P5.3 HTTP-Level Atomic Race Tests |
| [`docs/evidence/performance_tuning.txt`](evidence/performance_tuning.txt) | **P5.4** | `VERIFIED` | latest | Architecture characterization and bottleneck tuning notes |
| [`docs/evidence/mitm_demo.txt`](evidence/mitm_demo.txt) | **P6.1** | `VERIFIED` | `77bb076` | P6.1 Transport Security & Man-In-The-Middle (MITM) Defense Demonstration |
| [`docs/evidence/tls_headers.txt`](evidence/tls_headers.txt) | **P6.2** | `VERIFIED` | `addf510` | P6.2 TLS Protocol, Cipher Suites & Security Headers Verification |
| [`docs/evidence/zap_report.txt`](evidence/zap_report.txt) | **P6.3** | `VERIFIED` | `addf510` | P6.3 OWASP API Security Top 10 Automated Baseline Scan |
| [`docs/evidence/service_isolation.txt`](evidence/service_isolation.txt) | **P6.4** | `VERIFIED` | `addf510` | P6.4 Internal Service Isolation & Network Exposure Probes |
| [`docs/evidence/actionlint_report.txt`](evidence/actionlint_report.txt) | **P6.6** | `VERIFIED` | `addf510` | P6.6 actionlint GitHub Actions Workflow Static Analysis |
| [`docs/evidence/gitleaks_report.txt`](evidence/gitleaks_report.txt) | **P6.7** | `VERIFIED` | `addf510` | Gitleaks scan across all 32 commits: 0 leaks |
| [`docs/evidence/npm_audit_report.txt`](evidence/npm_audit_report.txt) | **P6.7** | `VERIFIED` | `addf510` | P6.7 Backend npm audit Vulnerability Scan |
| [`docs/evidence/pip_audit_report.txt`](evidence/pip_audit_report.txt) | **P6.7** | `VERIFIED` | `addf510` | pip-audit scan: 0 known vulnerabilities found |
| [`docs/evidence/trivy_report.txt`](evidence/trivy_report.txt) | **P6.7** | `VERIFIED` | `addf510` | Trivy filesystem scan: 0 vulnerabilities in backend/ui |
| [`docs/evidence/bandit_report.txt`](evidence/bandit_report.txt) | **P6.7** | `VERIFIED` | `addf510` | Bandit Python security linter: 0 medium, 0 high vulnerabilities |

### Automated Verification Note
- Total cataloged empirical evidence files: 40
- Zero hand-edited artifacts: all files generated via automated scripts, CLI tools, or browser drivers.
- All raw outputs include header metadata: execution command, timestamp, commit hash, and working tree cleanliness.