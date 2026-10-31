# Chapter 4: Empirical Evaluation & Results

## 4.1 Machine Learning Benchmark & Validation

All experiments were conducted on the deduplicated dataset ($n=304$ unique clinical profiles across 41 disease classes) using **Repeated Stratified K-Fold Cross-Validation (5 folds × 3 repeats = 15 total splits)**. Data augmentation (symptom-dropout) was applied strictly within training partitions to prevent data leakage.

> **Data Provenance & Calibration Status**: *The dataset is synthetically generated with 304 unique rows across 41 disease classes (after dropping 4,616 duplicates), and the deployed model is uncalibrated.*

### 4.1.1 Cross-Model Comparative Benchmark & Evidence Traceability
Candidate model families were benchmarked across 15 outer splits under varying levels of missing symptom noise (0%, 30%, and 50% missing symptoms):

- **Historical Draft Figures (Untraceable)**: An earlier Phase 7 project draft listed candidate metrics for LightGBM (Clean 99.67%, 30% Dropout 95.39%, 50% Dropout 83.22%, Mean F1 0.9512, ECE 0.0384, Brier 0.0121). These draft numbers **cannot be traced to lines in any empirical evidence file** in `docs/evidence/`.
- **Empirical Tuned Tree Benchmark (Traceable)**: The actual empirical nested CV benchmark recorded in [`docs/evidence/tuned_tree_benchmark.md`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/tuned_tree_benchmark.md) (5 folds × 3 repeats = 15 splits, with inner 3-fold CV for hyperparameter tuning) produced the following traceable metrics:

| Model | Evaluation Protocol | Symptom Dropout | Top-1 Accuracy | Top-3 Accuracy | Log-Loss | ECE | Evidence File |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **LightGBM (Tuned Inner-CV)** | Repeated Stratified 5x3 CV | **0% (Clean)** | 0.9890 ± 0.0119 | 0.9945 ± 0.0080 | 0.0656 ± 0.0720 | 0.0098 ± 0.0079 | [`tuned_tree_benchmark.md:12`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/tuned_tree_benchmark.md) |
| **LightGBM (Tuned Inner-CV)** | Repeated Stratified 5x3 CV | **30% (Robust)** | 0.8640 ± 0.0399 | 0.9440 ± 0.0341 | 0.7140 ± 0.2789 | 0.0975 ± 0.0370 | [`tuned_tree_benchmark.md:13`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/tuned_tree_benchmark.md) |
| **LightGBM (Tuned Inner-CV)** | Repeated Stratified 5x3 CV | **50% (Extreme)** | 0.6830 ± 0.0783 | 0.8256 ± 0.0652 | 1.7157 ± 0.5034 | 0.2019 ± 0.0508 | [`tuned_tree_benchmark.md:14`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/tuned_tree_benchmark.md) |
| **XGBoost (Tuned Inner-CV)** | Repeated Stratified 5x3 CV | **0% (Clean)** | 0.9836 ± 0.0139 | 0.9934 ± 0.0104 | 0.1433 ± 0.0367 | 0.0826 ± 0.0129 | [`tuned_tree_benchmark.md:15`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/tuned_tree_benchmark.md) |
| **XGBoost (Tuned Inner-CV)** | Repeated Stratified 5x3 CV | **30% (Robust)** | 0.8683 ± 0.0413 | 0.9715 ± 0.0201 | 0.6463 ± 0.1217 | 0.1983 ± 0.0346 | [`tuned_tree_benchmark.md:16`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/tuned_tree_benchmark.md) |
| **XGBoost (Tuned Inner-CV)** | Repeated Stratified 5x3 CV | **50% (Extreme)** | 0.7203 ± 0.0773 | 0.8969 ± 0.0549 | 1.2161 ± 0.2235 | 0.2118 ± 0.0474 | [`tuned_tree_benchmark.md:17`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/tuned_tree_benchmark.md) |

- **Deployed Production Model (Bernoulli Naive Bayes v2.0.0)**: As recorded in [`docs/evidence/model_benchmark.md`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/model_benchmark.md) and [`docs/MODEL_CARD.md`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/MODEL_CARD.md), Bernoulli Naive Bayes decisively outperformed tree ensembles under symptom omission on this sparse, synthetic dataset:
  - **0% Missing Symptoms**: Top-1 Accuracy `1.000 ± 0.000` (`100.0%`), Top-3 `1.000 ± 0.000`, Macro F1 `1.000`, Log-Loss `0.006 ± 0.004`, ECE `0.005` ([`model_benchmark.md:14`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/model_benchmark.md))
  - **30% Missing Symptoms**: Top-1 Accuracy `0.989 ± 0.014` (`98.9%`), Top-3 `1.000 ± 0.000`, Macro F1 `0.985`, Log-Loss `0.053 ± 0.024`, ECE `0.032` ([`model_benchmark.md:31`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/model_benchmark.md))
  - **50% Missing Symptoms**: Top-1 Accuracy `0.919 ± 0.023` (`91.9%`), Top-3 `0.991 ± 0.012`, Macro F1 `0.896`, Log-Loss `0.279 ± 0.050`, ECE `0.072` ([`model_benchmark.md:48`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/model_benchmark.md))

### 4.1.2 Probability Calibration Findings
Empirical calibration evaluations documented in [`docs/MODEL_CARD.md`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/MODEL_CARD.md) revealed that post-hoc Sigmoid/Platt Scaling (`CalibratedClassifierCV(method='sigmoid')`) substantially worsened out-of-fold log loss from 0.0061 to 0.1643 for Bernoulli Naive Bayes. Consequently, post-hoc calibration was rejected and the production service runs uncalibrated Bayesian posterior estimates.

---

## 4.2 System Performance & Concurrency Load Testing

To evaluate real-world responsiveness and stability under clinic load, an automated multi-tier concurrency benchmark was executed against the stack running the test-mode compose configuration (`docker-compose.test.yml`, `NODE_ENV=test`, `ALLOW_LOAD_TEST=true`, `LLM_ENABLED=false`).

The benchmark exercised all four critical production endpoints (`doctor_respond`, `health`, `submit_triage`, `worker_list`) across three concurrency levels (1, 10, and 50 concurrent simulated users), issuing **200 requests per endpoint per level (800 requests per concurrency tier, 2,400 total benchmark requests)** through the Nginx reverse proxy ingress at `https://localhost`.

### 4.2.1 Overall Concurrency Performance Table (200 Req / Endpoint, 2,400 Total)
*Source: [`docs/evidence/load_test_testmode_results.txt:13-17`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/load_test_testmode_results.txt) and [`load_test_testmode_results.json`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/load_test_testmode_results.json)*

| Concurrency Tier | Total Requests | Duration (s) | Throughput (req/s) | p50 Latency | p90 Latency | p95 Latency | p99 Latency | 400 Errors | 401 Errors | 429 Errors | 5xx Errors | Status Distribution |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **C = 1** | 800 | 78.79 s | 10.2 req/s | 79.3 ms | 148.9 ms | 190.6 ms | 317.4 ms | 0 | 0 | 0 | 0 | {200: 800} |
| **C = 10** | 800 | 57.74 s | 13.9 req/s | 500.7 ms | 1,530.1 ms | 1,952.3 ms | 2,548.2 ms | 0 | 0 | 0 | 0 | {200: 800} |
| **C = 50** | 800 | 54.31 s | 14.7 req/s | 2,428.4 ms | 5,057.2 ms | 5,862.8 ms | 8,087.4 ms | 0 | 0 | 0 | 0 | {200: 800} |
| **Total / Aggregate** | **2,400** | **190.84 s** | **12.6 req/s** | — | — | — | — | **0** | **0** | **0** | **0** | **{200: 2,400} (100%)** |

### 4.2.2 Per-Endpoint Latency Breakdown across Concurrency Levels
*Source: [`docs/evidence/load_test_testmode_results.txt:20-38`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/load_test_testmode_results.txt)*

- **Concurrency C = 1 (200 requests per endpoint)**:
  - `doctor_respond`: p50 = 73.0 ms | p90 = 116.8 ms | p95 = 128.6 ms | p99 = 244.2 ms (status={200: 200})
  - `health`: p50 = 61.5 ms | p90 = 88.5 ms | p95 = 93.9 ms | p99 = 131.7 ms (status={200: 200})
  - `submit_triage`: p50 = 135.4 ms | p90 = 256.3 ms | p95 = 299.2 ms | p99 = 392.4 ms (status={200: 200})
  - `worker_list`: p50 = 76.2 ms | p90 = 117.9 ms | p95 = 130.3 ms | p99 = 152.0 ms (status={200: 200})

- **Concurrency C = 10 (200 requests per endpoint)**:
  - `doctor_respond`: p50 = 474.3 ms | p90 = 765.0 ms | p95 = 856.6 ms | p99 = 1,286.7 ms (status={200: 200})
  - `health`: p50 = 354.3 ms | p90 = 637.7 ms | p95 = 717.2 ms | p99 = 1,135.1 ms (status={200: 200})
  - `submit_triage`: p50 = 1,349.2 ms | p90 = 2,274.1 ms | p95 = 2,443.5 ms | p99 = 2,863.4 ms (status={200: 200})
  - `worker_list`: p50 = 417.7 ms | p90 = 701.2 ms | p95 = 779.4 ms | p99 = 1,255.3 ms (status={200: 200})

- **Concurrency C = 50 (200 requests per endpoint)**:
  - `doctor_respond`: p50 = 2,183.6 ms | p90 = 4,462.1 ms | p95 = 5,269.6 ms | p99 = 6,676.6 ms (status={200: 200})
  - `health`: p50 = 2,412.6 ms | p90 = 4,734.2 ms | p95 = 5,576.5 ms | p99 = 8,168.2 ms (status={200: 200})
  - `submit_triage`: p50 = 3,050.5 ms | p90 = 6,242.4 ms | p95 = 6,729.9 ms | p99 = 9,930.8 ms (status={200: 200})
  - `worker_list`: p50 = 2,295.1 ms | p90 = 4,834.6 ms | p95 = 5,468.1 ms | p99 = 7,047.0 ms (status={200: 200})

### 4.2.3 End-to-End Triage Latency Profiling
*Source: [`docs/evidence/load_test_testmode_results.txt:41-47`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/load_test_testmode_results.txt)*
Empirical component profiling of the single-request triage pipeline (`POST /consultation/:id/analyze`) demonstrates that inference compute is not the bottleneck:
1. **ML Bayesian Inference (FastAPI :8000 in-container)**: 1.8 ms (1.4%)
2. **Devanagari PDF Synthesis (ReportLab, CPU)**: 63.0 ms (50.4%)
3. **Network Ingress, Express Middleware, DB Overhead**: 60.2 ms (48.2%)
- **Total Triage Pipeline Latency (LLM Offline / Deterministic Fallback)**: **125.0 ms (100.0%)**

---

## 4.3 Security & Cryptographic Verification

The backend security suite was tested across 19 automated test cases covering authentication hardening, cryptographic isolation, and injection defense:

| Security Vector | Test Scope | Result | Status |
| :--- | :--- | :---: | :---: |
| **Argon2id Hashing** | Memory-hard hashing, bcrypt auto-upgrade, timing attack resistance | 3 / 3 | **PASS** |
| **Account Lockout** | 5 consecutive failed attempts lock account for 15 minutes | 2 / 2 | **PASS** |
| **Refresh Token Family** | Rotating token issuance, reuse detection revoking family | 3 / 3 | **PASS** |
| **AES-256-GCM Crypto** | Authenticated encryption, random IV per record, auth tag verification | 3 / 3 | **PASS** |
| **Tamper Resistance** | Corrupt ciphertext / modified tag throws fatal decryption error | 2 / 2 | **PASS** |
| **NoSQL Injection** | Recursive stripping of `$` and `.` operators on nested JSON | 2 / 2 | **PASS** |
| **Multi-Tenant Isolation** | Foreign tenant queries return HTTP 404 (anti-enumeration) | 2 / 2 | **PASS** |
| **Admin Route Protection** | Public registration blocked with HTTP 403 `REGISTRATION_DISABLED` | 2 / 2 | **PASS** |
| **Total Security Suite** | [`phase2_security_matrix.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/phase2_security_matrix.txt) | **19 / 19** | **PASS (100%)** |

---

## 4.4 Automated Test Suite Summary

Across all subsystems and integration boundaries, ArogyaMitra achieved a **100% test pass rate** backed by concrete evidence logs:

- **Golden Set Evaluation**: **20 / 20 PASSED** ([`docs/evidence/p0_golden_set_live_output.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/p0_golden_set_live_output.txt))
  - Validates 20 clinically realistic symptom profiles against the 41-class disease boundary, verifies bilingual PDF byte emission, and proves fail-closed HTTP 503 behavior on upstream ML container outage.
- **Full Prototype Integration & Unit Suite**: **321 / 321 PASSED (100%)**
  - **ML Microservice Contract & Safety**: 55 / 55 PASSED ([`docs/evidence/verify_ml.txt:14`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/verify_ml.txt))
  - **Backend API, Auth & Security Matrix**: 231 / 231 PASSED ([`docs/evidence/verify_backend.txt:8`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/verify_backend.txt))
  - **LangGraph Reasoning, Injection & Fallbacks**: 26 / 26 PASSED ([`docs/evidence/verify_graph.txt:15`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/verify_graph.txt))
  - **Streamlit Headless Interface (AppTest)**: 9 / 9 PASSED ([`docs/evidence/verify_ui.txt:16`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/verify_ui.txt))
- **Playwright Browser End-to-End Suite**: **11 / 11 Scenarios PASSED** ([`docs/evidence/playwright_report.txt:64`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/playwright_report.txt))
  - Covers end-to-end triage, cardiac red-flag block, doctor second opinion workstation, admin dashboard & CSV export, multilingual PDF download, DPDP patient consent withdrawal, upstream ML outage fail-closed 503, role navigation, and server-side consultation list pagination.
