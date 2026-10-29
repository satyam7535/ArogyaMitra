# ArogyaMitra — Claims Trace Matrix (`docs/CLAIMS_TRACE.md`)

This living trace links every technical, architectural, and safety claim made across the ArogyaMitra documentation to exact empirical benchmarks, automated test suites, mutation checks, and reproduction commands.

---

## 1. Machine Learning & Clinical Explainability Claims

| Claim ID | Claim Description | Status | Verification Proof | Evidence File & Line | Mutation Check / Test Name | Reproducing Command |
|---|---|---|---|---|---|---|
| **CLM-ML-01** | Bernoulli Naive Bayes outperforms tuned tree models on binary symptom vectors. | **VERIFIED** | Nested CV benchmark: BernoulliNB 98.90 ± 1.36% vs Tuned XGBoost 86.83 ± 4.13% vs Tuned LightGBM 86.40 ± 3.99%. | [`docs/evidence/tuned_tree_benchmark.md`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/tuned_tree_benchmark.md) | None (Empirical comparison) | `python ML_Model/scripts/compare_tuned_trees.py` |
| **CLM-ML-02** | Additive Bayesian Log-Odds satisfies efficiency axiom ($\sum \Delta w_j = \Delta \log P$) to machine precision ($< 10^{-10}$). | **VERIFIED** | Exact mathematical log-odds computed; test asserts error $< 10^{-10}$ across all disease classes. | [`ML_Model/tests/test_hypothesis_properties.py`](file:///d:/Document/Projects/Internship/Arogyamitra/ML_Model/tests/test_hypothesis_properties.py) | MC22 (`docs/evidence/mutation_checks.md#MC22`) | `pytest ML_Model/tests/test_hypothesis_properties.py` |
| **CLM-ML-03** | Calibrated escalation policy achieves 5.26% escalation rate and 94.74% frontline coverage. | **VERIFIED** | Out-of-fold threshold sweep: Confidence < 70% OR Margin < 25% yields 16/304 escalations (5.26%), 1.39% direct coverage error. | [`docs/evidence/threshold_coverage.md`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/threshold_coverage.md) | MC23 (`docs/evidence/mutation_checks.md#MC23`) | `python ML_Model/scripts/evaluate_threshold_coverage.py` |
| **CLM-ML-04** | High-acuity symptoms (`chest_pain`, `breathlessness`) trigger Decision A automatic doctor escalation. | **VERIFIED** | Schema-validated red flag intercept forces `redFlag: true`, `needsEscalation: true`, and `risk: "High"`. | [`ML_Model/tests/test_clinical_red_flags.py`](file:///d:/Document/Projects/Internship/Arogyamitra/ML_Model/tests/test_clinical_red_flags.py) | MC27 (`docs/evidence/mutation_checks.md#MC27`) | `pytest ML_Model/tests/test_clinical_red_flags.py` |

---

## 2. Security, Privacy & DPDP Compliance Claims

| Claim ID | Claim Description | Status | Verification Proof | Evidence File & Line | Mutation Check / Test Name | Reproducing Command |
|---|---|---|---|---|---|---|
| **CLM-SEC-01** | Patient PII (`phoneNumber`, `address`, `medicalHistory`) is encrypted at rest using AES-256-GCM. | **VERIFIED** | Mongoose pre-save hook encrypts with IV and AuthTag; verified against live MongoDB documents. | [`Backend/tests/security.test.js`](file:///d:/Document/Projects/Internship/Arogyamitra/Backend/tests/security.test.js) | MC18 (`docs/evidence/mutation_checks.md#MC18`) | `npm --prefix Backend test` |
| **CLM-SEC-02** | Exact patient lookups use HMAC-SHA256 blind indexing without exposing plaintext in indexes. | **VERIFIED** | Blind index generated from normalized contact numbers; tests assert identical hashes and duplicate matching. | [`Backend/tests/security.test.js`](file:///d:/Document/Projects/Internship/Arogyamitra/Backend/tests/security.test.js) | `test_patient_blind_index_duplicate_matching` | `npm --prefix Backend test` |
| **CLM-SEC-03** | DPDP consent lifecycle supports capture, portability export, and soft deletion with PII anonymization. | **VERIFIED** | Deletion anonymizes fields to `[ANONYMIZED]`, sets `isDeleted: true`, subsequent queries return 404 (anti-enumeration). | [`Backend/tests/security.test.js`](file:///d:/Document/Projects/Internship/Arogyamitra/Backend/tests/security.test.js) | MC19 (`docs/evidence/mutation_checks.md#MC19`) | `npm --prefix Backend test` |
| **CLM-SEC-04** | Direct external calls to internal microservices (:8000, :8001) are forbidden without service tokens or blocked by proxy. | **VERIFIED** | Unauthenticated `/predict` and `/analyze` calls return 401; Nginx proxy configuration blocks `/predict` and `/analyze` external ingress with 403. | [`deploy/nginx.conf:123-129`](file:///d:/Document/Projects/Internship/Arogyamitra/deploy/nginx.conf#L123-L129) | MC1 & MC2 | `curl http://127.0.0.1:8000/predict` |
| **CLM-SEC-05** | Uploaded documents are verified by file magic-bytes, rejecting disguised executables and polyglots. | **VERIFIED** | File inspection validates `%PDF-`, PNG, and JPEG magic bytes in buffer memory prior to storage. | [`Backend/src/utils/upload.js`](file:///d:/Document/Projects/Internship/Arogyamitra/Backend/src/utils/upload.js) | MC29 (`docs/evidence/mutation_checks.md#MC29`) | `npm --prefix Backend test` |
| **CLM-SEC-06** | Admin CSV exports sanitize formula injection characters (`=`, `+`, `-`, `@`) with prepended apostrophes. | **VERIFIED** | Automated test submits formula payloads (`=cmd|' /C calc'!A0`); verifies escaped CSV output (`'=cmd...`). | [`Backend/tests/security.test.js`](file:///d:/Document/Projects/Internship/Arogyamitra/Backend/tests/security.test.js) | `test_csv_export_formula_injection_defense` | `npm --prefix Backend test` |

---

## 3. Concurrency & State Machine Governance Claims

| Claim ID | Claim Description | Status | Verification Proof | Evidence File & Line | Mutation Check / Test Name | Reproducing Command |
|---|---|---|---|---|---|---|
| **CLM-CONC-01** | Decision B enforces that health workers cannot accept red-flag consultations (`RED_FLAG_ACCEPT_BLOCKED` 409). | **VERIFIED** | Triage accept endpoint checks `redFlag` status; rejects with 409 unless valid doctor override note is supplied. | [`Backend/tests/security.test.js`](file:///d:/Document/Projects/Internship/Arogyamitra/Backend/tests/security.test.js) | `test_decision_b_red_flag_accept_blocked_409` | `npm --prefix Backend test` |
| **CLM-CONC-02** | Doctor second opinions are protected against stale overwrites via Optimistic Concurrency Control (`__v`). | **VERIFIED** | Concurrent doctor response submission tests verify second write yields HTTP 409 Conflict. | [`Backend/tests/concurrency.test.js`](file:///d:/Document/Projects/Internship/Arogyamitra/Backend/tests/concurrency.test.js) | MC31 (`docs/evidence/mutation_checks.md#MC31`) | `npm --prefix Backend test` |
| **CLM-CONC-03** | 50 parallel accept calls on pending consultation yield exactly 1 winner and 49 rejected transitions. | **VERIFIED** | Atomic state machine race test executes `Promise.all` across 50 requests; exactly 1 transition succeeds, 49 fail with 409 Conflict. | [`Backend/tests/concurrency.test.js`](file:///d:/Document/Projects/Internship/Arogyamitra/Backend/tests/concurrency.test.js) | `test_atomic_state_machine_parallel_accept_race` | `npm --prefix Backend test` |
| **CLM-CONC-04** | 50 parallel duplicate async job submissions with identical idempotency keys yield exactly 1 job created. | **VERIFIED** | MongoDB atomic unique idempotency index test executes 50 parallel calls; 1 job created, 49 return existing jobId. | [`Backend/tests/concurrency.test.js`](file:///d:/Document/Projects/Internship/Arogyamitra/Backend/tests/concurrency.test.js) | `test_idempotency_key_parallel_submissions` | `npm --prefix Backend test` |

---

## 4. LangGraph, Typography & UI Claims

| Claim ID | Claim Description | Status | Verification Proof | Evidence File & Line | Mutation Check / Test Name | Reproducing Command |
|---|---|---|---|---|---|---|
| **CLM-UI-01** | Streamlit UI operates as a thin-client, using user session JWTs and zero service secrets. | **VERIFIED** | Static code analysis and runtime tests assert no `INTERNAL_SERVICE_SECRET` in `ui/` codebase. | [`ui/tests/test_streamlit.py`](file:///d:/Document/Projects/Internship/Arogyamitra/ui/tests/test_streamlit.py) | `test_api_client_no_service_secret_or_bypass` | `cd ui; uv run pytest tests/test_streamlit.py` |
| **CLM-UI-02** | Clinical PDF generation bundles Noto Sans Devanagari typography under SIL Open Font License. | **VERIFIED** | Font files bundled in `graph/fonts/NotoSansDevanagari-Regular.ttf` with OFL license; verified by test rendering. | [`docs/evidence/pdf_samples/`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/pdf_samples/) | `test_noto_sans_devanagari_pdf_generation` | `pytest graph/tests/test_phase3.py` |
| **CLM-UI-03** | LangGraph pipeline withstands 20-attack prompt injection attacks and falls back cleanly. | **VERIFIED** | Test suite runs 20 jailbreak attacks (DAN mode, XML breakout, instruction ignore); all sanitized or safely rejected. | [`graph/tests/test_phase3.py`](file:///d:/Document/Projects/Internship/Arogyamitra/graph/tests/test_phase3.py) | MC30 (`docs/evidence/mutation_checks.md#MC30`) | `pytest graph/tests/test_phase3.py` |

