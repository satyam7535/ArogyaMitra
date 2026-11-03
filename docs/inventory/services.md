# ArogyaMitra — Microservices Topology & Service Inventory (`docs/inventory/services.md`)

This machine-readable map documents every service in ArogyaMitra, its network port, bind interface, authentication enforcement status with empirical evidence, and required configuration environment variables.

---

## Service Catalog

| Service Name | Component Path | Network Port | Bind Address | Auth Required? | Empirical Proof / Evidence | Required Environment Variables | Security & Isolation Evaluation |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- | :--- |
| **ML Diagnostic Service** | `ML_Model/app.py` | `8000` | `0.0.0.0` | **NO** | `curl.exe -s -X POST http://localhost:8000/predict -d '{"symptoms":["itching"]}'` returned `200 OK` with full diagnosis. Zero auth required. | `PORT`<br>`ALLOWED_ORIGINS` | **UNPROTECTED**: Binds to `0.0.0.0` without authentication. Anyone on local network can directly execute predictions. Violates Requirement A2 & F2. |
| **LangGraph Reasoning Pipeline** | `graph/server.py` | `8001` | `0.0.0.0` | **YES** | `curl.exe -s -i -X POST http://localhost:8001/analyze/json -d '{"symptoms":["itching"]}'` returned `401 Unauthorized: Missing internal service authentication token.` | `PORT`<br>`ML_API_URL`<br>`INTERNAL_SERVICE_SECRET`<br>`LLM_API_KEY`<br>`LLM_BASE_URL`<br>`LLM_MODEL`<br>`ALLOWED_ORIGINS` | Protected via HMAC-SHA256 JWT, but binds to `0.0.0.0` instead of `127.0.0.1`. |
| **Express Backend Gateway** | `Backend/src/index.js` | `5000` | `0.0.0.0` (Node default) | **YES** (Role-based JWT) | `curl.exe -s -i -X POST http://localhost:5000/api/v1/consultation/123/analysis/ml` returned `401 Unauthorized: No authentication token provided.` | `PORT`<br>`DB_URL`<br>`JWT_SECRET`<br>`JWT_EXPIRY`<br>`REFRESH_TOKEN_SECRET`<br>`REFRESH_TOKEN_EXPIRY`<br>`ENCRYPTION_KEY`<br>`INTERNAL_SERVICE_SECRET`<br>`FRONTEND_URL`<br>`NODE_ENV` | Startup validates secrets with Zod (fails closed if secret missing or `<32` chars). Direct client analysis mutation endpoints return 403. |
| **Streamlit Clinical UI** | `ui/Home.py` | `8501` | `0.0.0.0` | **NO** | Headless browser walkthrough accessed `/Home`, `/Worker_Triage`, `/Doctor_Review`, and `/Admin_Dashboard` with zero login or session tokens. | `BACKEND_URL`<br>`ML_API_URL`<br>`GRAPH_API_URL`<br>`INTERNAL_SERVICE_SECRET` | **OPEN / UNGUARDED**: No login screen, no session cookie verification. Holds internal secret and connects directly to ML/Graph. |

---

## Service-to-Service Topology Gaps

```mermaid
flowchart LR
    Browser([Browser / Client])
    UI[Streamlit UI :8501]
    API[Express Backend :5000]
    Graph[LangGraph :8001]
    ML[FastAPI ML :8000]

    Browser -.->|No Auth Required!| UI
    UI -.->|Direct Call with Secret!| Graph
    UI -.->|Direct Call (No Auth)!| ML
    API -->|HMAC JWT| Graph
    Graph -->|HTTP Call (No Auth)| ML

    style UI fill:#ffebee,stroke:#c62828
    style ML fill:#fff3e0,stroke:#ef6c00
```

1. **Intended Architecture**: Client $\rightarrow$ Streamlit $\rightarrow$ Backend $\rightarrow$ Graph $\rightarrow$ ML.
2. **Current Reality**: Streamlit UI bypasses Backend completely, directly querying Graph (:8001) using a leaked internal secret and ML (:8000) directly for symptoms.
