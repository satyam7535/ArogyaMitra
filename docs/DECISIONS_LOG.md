# ArogyaMitra — Architectural & Implementation Decisions Log

This document records the architectural and engineering decisions made during the Final Polish Run to ensure fail-closed safety, clinical honesty, and zero simulated metrics.

---

### Decision 1: Admin Dashboard Real Data Integration vs. Mock Simulation
- **Context**: The Admin Dashboard (`ui/pages/3_Admin_Dashboard.py`) previously displayed hardcoded numbers (`1,248` consultations, `14.2%` escalation rate, `38` workers, fake IP `203.0.113.19`).
- **Decision**: Completely remove all simulated metrics. Bind the view to real backend routes (`GET /api/v1/consultation/admin/analytics`, `GET /api/v1/admin/audit-logs`, `GET /api/v1/consultation/admin/queues`, `GET /api/v1/admin/sessions`). When the database is in a clean 0-state, display honest empty state banners and a clean empty DataFrame (`pd.DataFrame(columns=[...])`).
- **Alternatives Considered**:
  - Keep simulated data labeled as "Simulated Demo Mode". Rejected: The system must never present fabricated data to an evaluator or administrator.
- **Reason**: Clinical governance and transparency require genuine database telemetry.

---

### Decision 2: Streamlit Auth Token Caching in Playwright Test Runner
- **Context**: Backend security middleware enforces strict IP-based rate limiting on authentication routes (15 requests / 15 minutes). When Playwright automated tests run 11 back-to-back scenarios in Docker, all HTTP traffic originates from the internal `arogya-frontend` container IP, causing subsequent logins to receive HTTP 429 and downstream 401 session expiry.
- **Decision**: Added an in-memory `_AUTH_CACHE` (with 5-minute TTL) inside `ui/utils/api_client.py` for identical email credentials during active sessions.
- **Alternatives Considered**:
  - Disable or loosen the backend rate limiter. Rejected: Violates regression guard; rate limiting is a core defense-in-depth security control.
  - Add test-specific bypass in security middleware. Rejected: Test hooks must never be active in production containers.
- **Reason**: Preserves all production rate limits while enabling resilient multi-scenario client testing.

---

### Decision 3: Red-Flag Clinical Rationale Mapping in Worker UI
- **Context**: When acute red-flag symptoms (e.g., `chest_pain`) triggered emergency alerts, the banner sometimes rendered `(None)` when rationale was unmapped.
- **Decision**: Map matched red-flag terms directly to `clinical_rationale` loaded from `config/red_flags.yaml` (fallback to canonical symptom name with title capitalization). Enforce that `(None)` is never rendered.
- **Reason**: Frontline workers require clear, medically coherent guidance on why an emergency escalation is mandated.

---

### Decision 4: Friendly Emergency Error Message for HTTP 409
- **Context**: When a worker attempted to accept an acute emergency consultation, the system returned a technical error `{"error": "RED_FLAG_ACCEPT_BLOCKED"}`.
- **Decision**: Translate this technical error code in the Streamlit UI to a clear, patient-centric sentence: `"Emergency: cannot accept without a doctor."`
- **Reason**: Non-technical frontline health workers require actionable clinical instructions rather than HTTP error codes.

---

### Decision 5: Honest Uncalibrated Confidence Label
- **Context**: Naive Bayes conditional independence assumptions push probabilities towards 1.0 on multi-symptom presentations, displaying confidence $\ge 0.99$.
- **Decision**: Display `"Very high (uncalibrated estimate)"` when confidence $\ge 0.99$ instead of claiming certainty or mathematical calibration.
- **Reason**: Reflects Niculescu-Mizil & Caruana (2005) findings and prevents false overconfidence in clinical users.

---

### Decision 6: Clean Demo Reset Architecture
- **Context**: Faculty evaluators require a pristine zero-state environment to test the live consultation flow without remnants of automated test runs.
- **Decision**: Engineered `backend/src/scripts/resetDemoData.js` and automated runners `scripts/reset_demo.ps1` and `scripts/reset_demo.sh`. The script truncates `consultations`, `patients`, and `auditlogs` collections, resets user login lockouts, and preserves seed users (`Admin`, `Worker`, `Doctor`) and organizations.
- **Reason**: Provides a reproducible 1-click zero-state demo environment without tearing down containers or losing seeded user credentials.

---

### Decision 7: Multi-Panel Workflow Demonstration Figure in Academic Report
- **Context**: Report Section 3.5 previously contained `[PENDING FIX ROUND]` markers for clinician escalation and review persistence.
- **Decision**: Generated a publication-quality 6-panel composite figure (`fig_clinical_workflow_panels.png`, Figure 3.4) incorporating the real screenshots captured during end-to-end testing, removed all `[PENDING FIX ROUND]` markers, and documented the completed operational sequence.
- **Reason**: Provides visual, incontrovertible evidence of verified system capabilities directly within the academic report.

### 2026-11-01 - Final Report Pass 24 (Report-Only Polish)
- **Context**: Final academic formatting requirements for B.Tech project report submission (title styling, Bonafide supervisor name, Declaration AI usage statement, LaTeX equation rendering, clean UI screenshots without synthetic test identifiers, exact Table of Contents / List of Figures / List of Tables pagination, and strict empirical citation fidelity).
- **Decision**: 
  1. Updated cover title to balanced two-line layout; updated Bonafide to "Dr. Ashish Singh"; inserted explicit AI attribution statement in Declaration; cleaned acknowledgements typography.
  2. Rendered mathematical formulations (likelihood, Laplace smoothing, log posterior, additive feature attributions) to high-resolution LaTeX equation figures.
  3. Redrew architectural and timeout figures removing redundant titles and enlarging labels.
  4. Recaptured clean UI demonstration screenshots on fresh seeded database with zero `ZZTest`/`TEST-` artifacts.
  5. Mapped and locked exact TOC, List of Figures, and List of Tables page references to the compiled 37-page document.
  6. Generated both standard and `_24` suffixed deliverables (`.docx` and `.pdf`) in `docs/REPORT_FINAL/` and `docs/REPORT/`.
- **Reason**: Guarantees institutional submission readiness, 100% verifiable consistency with `docs/evidence/`, and complete alignment with academic report guidelines while keeping application code completely untouched.

