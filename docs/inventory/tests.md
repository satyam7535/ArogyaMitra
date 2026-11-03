# ArogyaMitra — Test Suite Inventory & Mock Assessment (`docs/inventory/tests.md`)

This machine-readable map documents every test file across the repository, what it covers, what it mocks, and whether mocks hide real system behavior.

---

## Test Suite Catalog

| Test File | Component | Tests Run | Passed | What It Covers | What It Mocks | Do Mocks Hide Real Behavior? (Harsh Audit) |
| :--- | :--- | :---: | :---: | :--- | :--- | :--- |
| [`ML_Model/tests/test_phase0.py`](file:///d:/Document/Projects/Internship/Arogyamitra/ML_Model/tests/test_phase0.py) | ML Service (Baseline) | 4 | 3 (1 fail) | Health, symptoms, prediction contract, empty symptom rejection. | None | **NO**: Real in-process call. `test_symptoms_endpoint` fails because the endpoint was upgraded to return objects (`{id, label, severity}`) while this legacy test expects strings. |
| [`ML_Model/tests/test_phase1.py`](file:///d:/Document/Projects/Internship/Arogyamitra/ML_Model/tests/test_phase1.py) | ML Service (Production) | 9 | 9 | Data deduplication (304 unique rows), typo normalization, prediction contract, TreeSHAP, high acuity escalation, vocabulary filtering. | None | **NO**: Tests execute against real LightGBM + TreeSHAP serialized artifacts (`ML_Model/model/v1/`). |
| [`graph/tests/test_phase3.py`](file:///d:/Document/Projects/Internship/Arogyamitra/graph/tests/test_phase3.py) | LangGraph AI Pipeline | 12 | 12 | Prompt injection defense, Pydantic schema parsing, deterministic multilingual fallback, service JWT verification, ReportLab PDF generation. | - Mocks OpenAI/Gemini client completions.<br>- Mocks ML microservice HTTP responses in e2e test. | **PARTIAL**: Mocks the LLM (as required to avoid API costs), but PDF test only verifies the `%PDF-` file header, completely missing Devanagari font rendering failures. |
| [`ui/tests/test_streamlit.py`](file:///d:/Document/Projects/Internship/Arogyamitra/ui/tests/test_streamlit.py) | Streamlit UI (Headless) | 6 | 6 | Headless rendering of Home, Worker Triage, Doctor Review, Admin Dashboard; i18n dictionary completeness; Plotly chart builders. | None (Uses in-process fallback in `api_client.py`) | **YES**: Mocks/stubs hide the fact that Doctor Review and Admin Dashboard use static hardcoded python lists/dataframes, and that Worker Triage bypasses the Express backend. |
| [`Backend/tests/security.test.js`](file:///d:/Document/Projects/Internship/Arogyamitra/Backend/tests/security.test.js) | Backend Security | 19 | 19 | AES-256-GCM encryption, Argon2id hashing, lockout logic, refresh token families, anti-enumeration 404 rule. | Mocks Mongoose models (`findById: vi.fn()`) and Express `req/res/next` objects. | **YES**: The test for `enforceOrgScope` passes against a mock model, hiding the fact that `enforceOrgScope` is **not mounted on any route** in `Backend/src/routes/*.js`. |
| [`Backend/tests/concurrency.test.js`](file:///d:/Document/Projects/Internship/Arogyamitra/Backend/tests/concurrency.test.js) | Backend Concurrency | 7 | 7 | Job queue lifecycle, status scoping, OCC schema configuration, 50-job enqueue throughput. | Defines in-test mock function `simulateConcurrentWrite`. | **YES (VACUOUS TEST)**: Lines 97–108 test OCC by creating a local dummy JavaScript function that throws an error, asserting that its own dummy function throws. Zero database concurrency or race conditions are tested. |

---

## Vacuous & Over-Mocked Tests Identified

1. **`tests/concurrency.test.js:97-108`**: OCC conflict detection test creates a synthetic JavaScript function `simulateConcurrentWrite` in test memory and checks if it throws `VersionError`. It never tests Mongoose or MongoDB.
2. **`tests/security.test.js:170-196`**: Tests `enforceOrgScope` middleware against a fabricated `{ findById: vi.fn() }` object. The test passes 100%, but the middleware was never attached to any actual Express route.
3. **`ui/tests/test_streamlit.py:45-56`**: Passes because `Doctor_Review.py` and `Admin_Dashboard.py` render static Python dictionaries. It proves the page mounts without crashing, but verifies zero live backend connectivity.
