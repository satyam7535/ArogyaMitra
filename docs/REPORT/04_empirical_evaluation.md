# Chapter 4: Empirical Evaluation & Results

## 4.1 Machine Learning Benchmark & Validation

All experiments were conducted on the deduplicated dataset ($n=304$ unique clinical profiles across 41 disease classes) using **Repeated Stratified K-Fold Cross-Validation (5 folds × 3 repeats = 15 total splits)**. Data augmentation (symptom-dropout) was applied strictly within training partitions to prevent data leakage.

### 4.1.1 Cross-Model Comparative Benchmark
Six candidate model families were benchmarked under varying levels of missing symptom noise (0%, 30%, and 50% missing symptoms):

| Model Family | Clean Accuracy (0% Drop) | Robust Accuracy (30% Drop) | Extreme Robustness (50% Drop) | Mean F1-Score |
| :--- | :---: | :---: | :---: | :---: |
| **LightGBM (Tuned + Aug)** | **99.67%** | **95.39%** | **83.22%** | **0.9512** |
| XGBoost (Augmented) | 99.34% | 94.74% | 81.91% | 0.9458 |
| CatBoost (Augmented) | 99.01% | 93.42% | 80.26% | 0.9389 |
| Random Forest (Augmented) | 98.68% | 91.78% | 77.96% | 0.9241 |
| Multilayer Perceptron (MLP) | 96.05% | 88.16% | 72.37% | 0.8876 |
| Gaussian Naïve Bayes | 89.47% | 78.29% | 63.82% | 0.8015 |

*Complete raw data and split distributions are archived in [`model_benchmark.md`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/model_benchmark.md) and [`model_benchmark.csv`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/model_benchmark.csv).*

### 4.1.2 Probability Calibration Metrics
Hyperparameter optimization using Optuna yielded a cross-validated Log Loss of **0.0505**. Applying post-hoc Sigmoid/Platt calibration significantly improved probabilistic alignment:

| Metric | Uncalibrated LightGBM | Calibrated LightGBM (Platt Sigmoid) | Improvement |
| :--- | :---: | :---: | :---: |
| **Expected Calibration Error (ECE)** | 0.0892 | **0.0384** | **-56.9%** |
| **Brier Score** | 0.0247 | **0.0121** | **-51.0%** |
| **Multi-class Log Loss** | 0.0914 | **0.0505** | **-44.7%** |

*The calibration curve is plotted in [`calibration_reliability.png`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/calibration_reliability.png).*

---

## 4.2 System Performance & Concurrency Load Testing

To evaluate real-world responsiveness under clinic peak hours, an automated load test was executed across four concurrency tiers ($c \in \{1, 5, 10, 20\}$) issuing 400 total requests against the asynchronous job queue.

| Concurrency Tier ($c$) | Total Requests | Completed | Failed | Error Rate | Mean Latency (ms) | P95 Latency (ms) | Max Latency (ms) | Throughput (req/s) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **c = 1** | 100 | 100 | 0 | **0.00%** | 92.4 ms | 114.2 ms | 148.0 ms | **10.74 req/s** |
| **c = 5** | 100 | 100 | 0 | **0.00%** | 375.3 ms | 421.0 ms | 489.0 ms | **13.17 req/s** |
| **c = 10** | 100 | 100 | 0 | **0.00%** | 758.3 ms | 812.0 ms | 902.0 ms | **13.06 req/s** |
| **c = 20** | 100 | 100 | 0 | **0.00%** | 1,514.8 ms | 1,640.0 ms | 1,780.0 ms | **13.08 req/s** |
| **Total / Aggregate** | **400** | **400** | **0** | **0.00%** | **685.2 ms** | **1,640.0 ms** | **1,780.0 ms** | **12.51 req/s** |

### Key Concurrency Findings:
1. **Zero Request Dropping**: Error rate was **0.00%** across all 400 requests.
2. **Graceful Queueing**: When concurrency exceeded worker capacity ($c=10, 20$ with `maxConcurrency: 5`), throughput remained stable at ~13.1 req/s while latency scaled linearly without server degradation or memory spikes.
3. *Complete load test logs are preserved in [`load_test.md`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/load_test.md).*

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

Across all subsystems, ArogyaMitra achieved a **100% test pass rate** (53 passing tests, 0 failures, 0 skipped):

```
================================== TEST MATRIX SUMMARY ==================================
  Suite 1: ML Microservice Contract (Pytest) ................  9 /  9 PASSED [100%]
  Suite 2: Backend Security & Multi-Tenancy (Vitest) ....... 19 / 19 PASSED [100%]
  Suite 3: LangGraph Reasoning & LLM Fallback (Pytest) ...... 12 / 12 PASSED [100%]
  Suite 4: Concurrency & Optimistic Locking (Vitest) ........  7 /  7 PASSED [100%]
  Suite 5: Streamlit Headless Interface (Pytest AppTest) ...  6 /  6 PASSED [100%]
-----------------------------------------------------------------------------------------
  TOTAL VERIFIED SYSTEM TESTS .............................. 53 / 53 PASSED [100%]
=========================================================================================
```
