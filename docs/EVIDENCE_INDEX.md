# ArogyaMitra — Master Evidence & Empirical Verification Index

This index catalogs every empirical artifact, benchmark log, test output, cryptographic verification, and probe run generated throughout the project lifecycle. In accordance with the system's strict evidence rules, **all metrics and figures originate from reproducible commands and real executions**.

---

## 1. Master Artifact Catalog

| # | Evidence Artifact | Component / Scope | Verified Flow / Phase | Generation Command | Empirical Outcome / Result |
| :-: | :--- | :--- | :---: | :--- | :--- |
| **1** | [`stage1_probes.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/stage1_probes.txt) | Backend Auth & RBAC | Flow Steps 1–2 | `node Backend/src/scripts/runStage1Probes.js` | 100% pass on route table introspection, token rotation, positive write controls, cross-org 404 anti-enumeration, and role casing validation. |
| **2** | [`stage2_probes.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/stage2_probes.txt) | Patient PII & Encryption | Flow Steps 3–4 | `node Backend/src/scripts/runStage2Probes.js` | AES-256-GCM field encryption, DPDP consent tracking, duplicate detection, and key rotation. |
| **3** | [`stage3_probes.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/stage3_probes.txt) | ML Microservice (:8000) | Flow Step 6 | `node Backend/src/scripts/runStage3Probes.js` | Bernoulli Naive Bayes (v2.0.0) inference, calibrated probabilities, exact Bayesian log-odds feature attributions, and uncertainty escalation. |
| **4** | [`stage4_probes.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/stage4_probes.txt) | Job Queue & AI Pipeline | Flow Steps 6, 7, 8 | `node Backend/src/scripts/runStage4Probes.js` | Asynchronous job queue, safe LLM reasoning, deterministic fallback (`llmFallback: true`), and ReportLab multilingual PDF generation. |
| **5** | [`stage5_probes.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/stage5_probes.txt) | Clinical Decisions & OCC | Flow Steps 10, 11 | `node Backend/src/scripts/runStage5Probes.js` | Worker accept (`/:id/accept`), Worker escalate (`/:id/escalate`), Doctor queue (`/pending`), Doctor response (`/:id/respond`), OCC collision rejection (409 Conflict), and immutable audit log persistence. |
| **6** | [`model_benchmark.md`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/model_benchmark.md)<br>[`tuned_tree_benchmark.md`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/tuned_tree_benchmark.md) | Machine Learning Benchmark | Phase 3 / Decision B | `uv run python ML_Model/scripts/run_repeated_cv_benchmark.py` | Repeated Stratified K-Fold CV (5x3) benchmark across 6 model families at 0%, 30%, 50% missing symptoms. BernoulliNB ranked #1 (98.9% top-1 @ 30%, 91.9% top-1 @ 50%, log-loss 0.28, ECE 0.07). |
| **7** | [`threshold_coverage.md`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/threshold_coverage.md) | ML Uncertainty Safety | Phase 3 / Decision B | `uv run python ML_Model/scripts/evaluate_thresholds.py` | Empirical validation fold threshold derivation: confidence threshold 0.40, severity threshold 4.0, escalation coverage rate 14.8%. |
| **8** | [`concurrency_investigation.md`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/concurrency_investigation.md) | Job Queue Durability | Phase 4 / Group E | `Backend/tests/concurrency.test.js` | 50 concurrent worker contention simulation: exactly 10 claims, 40 backoffs, 0 duplicates, 0 lost updates; lease recovery verified. |
| **9** | [`load_test.md`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/load_test.md) | Multi-VU Load Benchmark | Phase 4 / Group E | `node Backend/src/scripts/run_load_test.js` | 1,600 simulated requests across 10, 50, 100 Virtual Users. Peak throughput: **193.4 req/s**, 0% error rate, sub-50ms p50 latency. |
| **10** | [`pdf_generation_evidence.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/pdf_generation_evidence.txt)<br>[`sample_report_preview.png`](file:///d:/Document/Projects/Internship/Arogyamitra/graph/scripts/output/sample_report_preview.png) | Multilingual PDF Generation | Phase 4 / Group E | `uv run python graph/scripts/verify_pdf_generation.py` | Bundled DejaVuSans font rendering bilingual English/Hindi/Marathi clinical report, Bayesian evidence horizontal bars, red-flag alert banner. |
| **11** | [`mutation_checks.md`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/mutation_checks.md) | Mutation Testing Suite | Stages 0–6 | Production Code Mutation | **32 verified mutation checks (MC1–MC32)** covering security guards, role casing, reset tokens, OCC, DPDP consent, magic bytes, LLM sanity, and thin-client validation. |
| **12** | [`netstat_proof.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/netstat_proof.txt) | Network Security | Stages 0–6 | `netstat -ano` | Verifies loopback-only binding (`127.0.0.1`) across Express (5000), FastAPI ML (8000), LangGraph (8001), and Streamlit (8501). |
| **13** | [`npm_audit.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/npm_audit.txt) | Node Dependencies | Phase 5 Security | `npm --prefix Backend audit` | **0 vulnerabilities found** (clean pass). |
| **14** | [`pip_audit.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/pip_audit.txt) | Python Dependencies | Phase 5 Security | `uv run --with pip-audit pip-audit` | Evaluated PYSEC-2026-113 in pyarrow 18.1.0; documented non-exposure in memory-only internal dataframe rendering. |
| **15** | [`bandit_report.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/bandit_report.txt) | Python AST Static Analysis | Phase 5 Security | `uv run --with bandit bandit -r ML_Model graph ui` | **0 High, 0 Medium severity issues** across 5,547 lines of Python code. |
| **16** | [`gitleaks_report.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/gitleaks_report.txt) | Repository History Audit | Phase 5 Security | `D:\tools\gitleaks.exe detect --source . -v --redact` | **No leaks found** across all 17 git commits. |
| **17** | [`FLOW_TRACE.md`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/FLOW_TRACE.md) | End-to-End Clinical Flow | Flow Steps 1–13 | Verification Matrix | 13/13 Flow Steps marked `VERIFIED` with concrete log links. |

---

## 2. Automated Test Suite Metrics

| Test Suite | Framework / Runner | Test Scope | Number of Tests | Status |
| :--- | :--- | :--- | :---: | :---: |
| **ML Engine Tests** | `uv run pytest ML_Model/tests/` | Phase 0 contracts, Phase 1 schemas, model consistency, hypothesis property tests, clinical red flags fail-closed validation | **55** | **PASSED (100%)** |
| **Backend Tests** | `npm --prefix Backend test` (Vitest) | Express route auth matrix (87), Concurrency & Durable Queue (10), Security, Cryptography, OCC & Flow Steps 10-11 (64) | **161** | **PASSED (100%)** |
| **Graph AI Pipeline Tests** | `uv run pytest graph/tests/` | Safe LLM reasoning, 20 prompt injection defenses, deterministic fallback, output sanity drug checks, ReportLab PDF generation | **22** | **PASSED (100%)** |
| **Streamlit UI Tests** | `uv run pytest ui/tests/` | Headless `AppTest` multi-page mounting, localization integrity, Plotly viz robustness, thin-client auth role constraints | **9** | **PASSED (100%)** |
| **Grand Total** | `scripts/verify_all.ps1` | Full End-to-End Regression Harness | **247** | **PASSED (100%)** |
