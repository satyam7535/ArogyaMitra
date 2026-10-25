# ArogyaMitra — Master Evidence & Empirical Verification Index

This index catalogs every empirical artifact, benchmark log, test output, and cryptographic verification generated throughout the project. In accordance with the system's strict evidence rules, **all metrics and figures originate from reproducible runs**.

---

## Master Artifact Catalog

| # | Evidence Artifact | Component | Date Generated | Generation Command | Empirical Outcome / Result |
| :-: | :--- | :--- | :---: | :--- | :--- |
| **1** | [`phase0_ml_contract.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/phase0_ml_contract.txt) | ML Service (Baseline) | 2026-10-26 | `pytest tests/test_contract.py` | 1/1 passed. Verified baseline `/predict` schema contract. |
| **2** | [`model_benchmark.md`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/model_benchmark.md)<br>[`model_benchmark.csv`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/model_benchmark.csv) | Machine Learning | 2026-10-26 | `python scripts/benchmark.py` | Benchmarked 6 model families across 15 splits (5x3 Repeated Stratified K-Fold) with 0%, 30%, 50% missing symptoms. LightGBM (Tuned + Aug) ranked #1 (99.67% clean, 83.22% under 50% missing). |
| **3** | [`classification_report.md`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/classification_report.md) | Machine Learning | 2026-10-26 | `python scripts/train_lightgbm.py` | Per-class precision, recall, and F1 across all 42 diseases. Macro F1: 0.9967, Weighted F1: 0.9967. |
| **4** | [`calibration_reliability.png`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/calibration_reliability.png) | Machine Learning | 2026-10-26 | `python scripts/train_lightgbm.py` | Empirical reliability diagram confirming calibration alignment. Log Loss: 0.0505, ECE: 0.0384, Brier Score: 0.0121. |
| **5** | [`phase1_ml_contract.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/phase1_ml_contract.txt) | ML Microservice | 2026-10-26 | `pytest tests/test_phase1.py -v` | **9 / 9 passed (100%)**. Validated `/health`, `/ready`, `/model-info`, `/symptoms`, `/predict`, calibrated probabilities, TreeSHAP attributions, and clinical uncertainty escalation triggers. |
| **6** | [`phase2_security_matrix.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/phase2_security_matrix.txt) | Backend Security | 2026-10-26 | `npm test tests/security.test.js` | **19 / 19 passed (100%)**. Validated Argon2id hashing, legacy bcrypt migration, 5-attempt lockout, rotating refresh tokens with reuse detection, AES-256-GCM PII encryption, anti-enumeration 404s, and NoSQL injection sanitizer. |
| **7** | [`phase3_llm_pipeline.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/phase3_llm_pipeline.txt) | LangGraph Pipeline | 2026-10-26 | `pytest tests/test_phase3.py -v` | **12 / 12 passed (100%)**. Validated prompt injection neutralization, Pydantic v2 parsing, inter-service HMAC JWT authentication, ReportLab bilingual PDF generation, and deterministic clinical fallback. |
| **8** | [`load_test.md`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/load_test.md)<br>[`run_load_test.py`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/run_load_test.py) | Backend Concurrency | 2026-10-26 | `python docs/evidence/run_load_test.py` | 400 real requests across 4 concurrency tiers ($c=1, 5, 10, 20$). Peak throughput: 13.17 req/s, **0.00% error rate**. |
| **9** | [`phase4_concurrency_matrix.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/phase4_concurrency_matrix.txt) | Backend Concurrency | 2026-10-26 | `npm test tests/concurrency.test.js` | **7 / 7 passed (100%)** (26/26 backend total). Validated Mongoose optimistic locking `VersionError`, job queue async orchestration, status isolation, and concurrency throttling. |
| **10** | [`mitm_demo.md`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/mitm_demo.md) | Network Security | 2026-10-26 | Network Packet Capture Analysis | Empirical packet analysis contrasting cleartext HTTP exposure with TLS 1.3 encryption, HSTS downgrade resistance, and AES-256-GCM authenticated tamper-resistance. |
| **11** | [`security_audit.md`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/security_audit.md) | System Dependencies | 2026-10-26 | `npm audit fix` & pip inspection | Dependency vulnerability audit and mitigation report across Node.js and Python ecosystems. |
| **12** | [`phase6_streamlit_evidence.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/phase6_streamlit_evidence.txt) | Streamlit UI | 2026-10-26 | `pytest tests/test_streamlit.py -v` | **6 / 6 passed (100%)**. Headless UI verification using `streamlit.testing.v1.AppTest` across `Home.py`, `1_Worker_Triage.py`, `2_Doctor_Review.py`, and `3_Admin_Dashboard.py`. |

---

## Cumulative Verification Summary

$$\text{Total Verified Automated Tests} = 9 \text{ (ML)} + 19 \text{ (Security)} + 12 \text{ (Graph)} + 7 \text{ (Concurrency)} + 6 \text{ (Streamlit)} = \mathbf{53 \text{ Passed / 53 Total (100\%)}}$$

$$\text{Total Load Test Requests} = 400 \quad | \quad \text{Failed Requests} = 0 \quad (\mathbf{0.00\% \text{ Error Rate}})$$
