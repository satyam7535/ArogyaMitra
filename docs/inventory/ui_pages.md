# ArogyaMitra — Streamlit UI Pages Inventory Map (`docs/inventory/ui_pages.md`)

This machine-readable map documents every Streamlit page in `ui/`, the endpoints it communicates with, and flags direct connections to internal microservices or secret possession.

---

## UI Page Catalog

| Page File | Primary Role | Backend Endpoints Called | Direct ML / Graph / DB Calls | Holds Service Secret? | Stubs & Mock Data Identified |
| :--- | :--- | :--- | :--- | :---: | :--- |
| [`ui/Home.py`](file:///d:/Document/Projects/Internship/Arogyamitra/ui/Home.py) | Welcome Hub, Health Telemetry, Vernacular Language Switcher | `GET /api/v1/consultation/queue/metrics` (via `check_services_health`) | **YES**<br>- `GET http://localhost:8000/health`<br>- `GET http://localhost:8001/health` | **YES** (imports from `api_client.py`) | No real login screen or authentication guard; open navigation to all role pages. |
| [`ui/pages/1_Worker_Triage.py`](file:///d:/Document/Projects/Internship/Arogyamitra/ui/pages/1_Worker_Triage.py) | Frontline ASHA Worker Triage Workstation | **NONE** (Bypasses backend entirely!) | **YES**<br>- `GET http://localhost:8000/symptoms`<br>- `POST http://localhost:8001/analyze/json`<br>- In-process fallback: imports `app.run_prediction` & `graph.llm.call_llm` directly | **YES** (Uses `INTERNAL_SERVICE_SECRET` to mint JWTs for Graph) | - "Accept Decision" & "Escalate" buttons only show `st.success`/`st.warning` banner without persisting to MongoDB.<br>- No consultation created in backend. |
| [`ui/pages/2_Doctor_Review.py`](file:///d:/Document/Projects/Internship/Arogyamitra/ui/pages/2_Doctor_Review.py) | Medical Officer Second Opinion Queue | **NONE** (Zero API calls) | **NONE** | No | - Uses hardcoded `PENDING_CASES` list (lines 35–64).<br>- All decision actions ("Confirm", "Override", "Order Lab") only trigger `st.success` without backend updates. |
| [`ui/pages/3_Admin_Dashboard.py`](file:///d:/Document/Projects/Internship/Arogyamitra/ui/pages/3_Admin_Dashboard.py) | PHC Network Governance & Monitoring | **NONE** (Zero API calls) | **NONE** | No | - KPIs ("1,248 consultations", "14.2% escalation") are hardcoded strings.<br>- Disease prevalence pie chart uses hardcoded dictionary.<br>- Audit trail uses hardcoded fake events dataframe (`sample_audit_events`). |
| [`ui/utils/api_client.py`](file:///d:/Document/Projects/Internship/Arogyamitra/ui/utils/api_client.py) | Shared API Adapter & Client Helper | `GET /api/v1/consultation/queue/metrics` | **YES** (Direct `httpx` to `:8000` and `:8001`) | **YES** (`INTERNAL_SERVICE_SECRET` read from env) | In-process fallback imports ML and Graph source code directly when HTTP services fail. |

---

## Architectural Violations Flagged (Against Requirement A1 & C1)

1. **Direct Service Calls & Secret Leakage**: The UI client directly accesses internal ports `:8000` (ML) and `:8001` (Graph), and holds `INTERNAL_SERVICE_SECRET` to self-mint inter-service JWT tokens. Requirement A1 states: *"UI is a thin client: calls only the backend; contains no internal service secret; works with ML/graph ports unreachable to it."*
2. **Backend Gateway Bypass**: `1_Worker_Triage.py` never calls `POST /api/v1/consultation/:id/analyze`. Patients and consultations triaged in the UI are never saved to the MongoDB database.
3. **Missing Authentication & Role Guards**: There is no login form, session cookie management, or role restriction. Any user accessing `localhost:8501` can view and click through Worker, Doctor, and Admin screens.
4. **Hardcoded Workstation Stubs**: Doctor Review and Admin Dashboard are purely visual mockups with static data and no state persistence.
