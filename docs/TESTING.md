# ArogyaMitra — Test Strategy & Verification Guide

## 1. Test Architecture & Taxonomy

ArogyaMitra employs an automated testing pyramid ensuring functional correctness, security compliance, mathematical model validity, and high concurrency resilience without external cloud dependencies.

```
                  ┌───────────────────────────────┐
                  │   Streamlit AppTest (E2E)     │  6/6 Tests
                  ├───────────────────────────────┤
                  │ Concurrency & Stress Matrix   │  7/7 Tests
                  ├───────────────────────────────┤
                  │ Inter-Service & Graph Pytest  │ 12/12 Tests
                  ├───────────────────────────────┤
                  │ Backend Security & Org Scoping│ 19/19 Tests
                  ├───────────────────────────────┤
                  │ ML Calibration & Contract API │  9/9 Tests
                  └───────────────────────────────┘
```

---

## 2. Test Execution Commands & Verification Matrix

| Suite | Component | Scope & Coverage | Runner | Passing Tests | Evidence File |
| :--- | :--- | :--- | :--- | :---: | :--- |
| **Suite 1: ML Contract** | `ML_Model` | `/health`, `/predict`, schema validation, calibrated probabilities, TreeSHAP dimensions, edge cases | Pytest | **9 / 9** (100%) | [`phase1_ml_contract.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/phase1_ml_contract.txt) |
| **Suite 2: Security Suite** | `Backend` | Argon2id, lockout, refresh token reuse, AES-256-GCM, NoSQL injection, multi-tenant 404s, rate limits | Vitest | **19 / 19** (100%) | [`phase2_security_matrix.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/phase2_security_matrix.txt) |
| **Suite 3: AI Pipeline** | `graph` | Prompt injection defenses, Pydantic v2 parsing, inter-service JWT auth, PDF generation, fallback | Pytest | **12 / 12** (100%) | [`phase3_llm_pipeline.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/phase3_llm_pipeline.txt) |
| **Suite 4: Concurrency** | `Backend` | Optimistic locking `VersionError`, async job queue, worker concurrency throttle, status polling | Vitest | **7 / 7** (100%) | [`phase4_concurrency_matrix.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/phase4_concurrency_matrix.txt) |
| **Suite 5: Streamlit UI** | `ui` | Headless page mounting (`AppTest`), widgets, charts, state management, exception-free rendering | Pytest | **6 / 6** (100%) | [`phase6_streamlit_evidence.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/phase6_streamlit_evidence.txt) |
| **Total Test Suite** | **All Services** | **End-to-End Enterprise System Validation** | **Multi** | **53 / 53** | **All Passed (100%)** |

---

## 3. Individual Test Runner Instructions

### 3.1 ML Microservice Contract Tests
Verifies the LightGBM calibrated model, SHAP tree explainability, and HTTP API contract:

```powershell
cd ML_Model
$env:PYTHONPATH="."
uv run pytest tests/test_phase1.py -v
```

### 3.2 Backend Security & Authentication Tests
Tests cryptographic integrity, AES-256-GCM PII field-level encryption, multi-tenant organization boundaries, and injection defense:

```powershell
cd Backend
npm test tests/security.test.js
```

### 3.3 Clinical Reasoning Pipeline & LLM Fallback Tests
Tests prompt injection sanitization, Pydantic v2 structured output parsing, bilingual ReportLab PDF rendering, and deterministic fallback logic:

```powershell
cd graph
$env:PYTHONPATH="."
uv run pytest tests/test_phase3.py -v
```

### 3.4 Concurrency & Job Queue Tests
Tests Mongoose optimistic concurrency control (`__v`), asynchronous job queue worker throttling, and status isolation:

```powershell
cd Backend
npm test tests/concurrency.test.js
```

### 3.5 Streamlit Headless Interface Tests
Runs `streamlit.testing.v1.AppTest` across `Home.py`, `1_Worker_Triage.py`, `2_Doctor_Review.py`, and `3_Admin_Dashboard.py`:

```powershell
cd ui
$env:PYTHONPATH="."
uv run pytest tests/test_streamlit.py -v
```

---

## 4. Mocking & Offline Isolation Strategy

To ensure zero flaky tests and rapid execution in restricted or air-gapped CI environments:
- **LLM Isolation**: In `graph/tests/test_phase3.py`, Google Gemini API calls are mocked via Python's `unittest.mock.patch` targeting `httpx.Client.post` and OpenAI client mocks.
- **Database Isolation**: In `Backend/tests/security.test.js` and `concurrency.test.js`, database operations test schema methods, cryptographic transformations, and in-memory Mongoose documents without requiring a live MongoDB server.
- **ML Isolation in Pipeline**: When testing the reasoning graph independently, the internal ML endpoint is mocked with deterministic probability and SHAP fixtures.
