# ArogyaMitra — Operations & Deployment Runbook

## 1. Environment Variable Specifications

Every microservice in ArogyaMitra is governed by strictly validated environment configurations. Missing or malformed variables will fail fast at process startup.

### 1.1 Backend Service (`Backend/.env`)
Template file: [`Backend/.env.example`](file:///d:/Document/Projects/Internship/Arogyamitra/Backend/.env.example)

| Variable | Required | Default / Format | Description |
| :--- | :---: | :--- | :--- |
| `PORT` | No | `5000` | Port for Express HTTP server. |
| `NODE_ENV` | Yes | `development` / `production` / `test` | Runtime environment mode. |
| `MONGO_URI` | Yes | `mongodb://localhost:27017/arogyamitra` | MongoDB connection URI. |
| `JWT_SECRET` | Yes | Min 32 characters | Cryptographic secret for signing user access JWTs. |
| `JWT_EXPIRY` | No | `15m` | Lifetime of short-lived access tokens. |
| `REFRESH_TOKEN_SECRET` | Yes | Min 32 characters | Secret for rotating refresh tokens. |
| `REFRESH_TOKEN_EXPIRY` | No | `7d` | Inactivity expiry for refresh token families. |
| `ENCRYPTION_KEY` | Yes | 64-char hex (32 bytes) | AES-256-GCM symmetric key for patient PII. |
| `INTERNAL_SERVICE_SECRET` | Yes | Min 32 characters | Shared HMAC-SHA256 secret for inter-service JWT. |
| `AI_SERVICE_URL` | No | `http://localhost:8001` | LangGraph orchestration endpoint. |
| `CORS_ORIGIN` | No | `http://localhost:8501` | Allowed origin for frontend clients. |

### 1.2 ML Diagnostic Service (`ML_Model/.env`)
Template file: [`ML_Model/.env.example`](file:///d:/Document/Projects/Internship/Arogyamitra/ML_Model/.env.example)

| Variable | Required | Default / Format | Description |
| :--- | :---: | :--- | :--- |
| `PORT` | No | `8000` | FastAPI server port. |
| `MODEL_PATH` | No | `ML_Model/model/v1/lightgbm_calibrated.joblib` | Serialized calibrated model artifact. |
| `SHAP_EXPLAINER_PATH` | No | `ML_Model/model/v1/shap_explainer.joblib` | Serialized TreeSHAP explainer artifact. |
| `SYMPTOMS_LIST_PATH` | No | `ML_Model/model/v1/symptoms.json` | 131 canonical symptom schema definitions. |
| `INTERNAL_SERVICE_SECRET` | Yes | Min 32 characters | Shared secret for token verification. |

### 1.3 LangGraph Clinical Reasoning Service (`graph/.env`)
Template file: [`graph/.env.example`](file:///d:/Document/Projects/Internship/Arogyamitra/graph/.env.example)

| Variable | Required | Default / Format | Description |
| :--- | :---: | :--- | :--- |
| `PORT` | No | `8001` | FastAPI server port. |
| `LLM_API_KEY` | Yes | Google AI Studio Key | API Key for Gemini 1.5 Flash. |
| `LLM_BASE_URL` | No | `https://generativelanguage.googleapis.com/v1beta/openai/` | OpenAI-compatible endpoint. |
| `LLM_MODEL` | No | `gemini-1.5-flash` | Target LLM model family. |
| `ML_SERVICE_URL` | No | `http://localhost:8000` | Internal ML inference endpoint. |
| `INTERNAL_SERVICE_SECRET` | Yes | Min 32 characters | Shared secret for inter-service token. |

### 1.4 Streamlit Presentation UI (`ui/.env` / Config)
| Variable | Required | Default | Description |
| :--- | :---: | :--- | :--- |
| `BACKEND_URL` | No | `http://localhost:5000` | Backend API Gateway. |
| `ML_SERVICE_URL` | No | `http://localhost:8000` | Fallback ML endpoint. |
| `GRAPH_SERVICE_URL` | No | `http://localhost:8001` | Fallback Graph endpoint. |

---

## 2. One-Command Setup & Local Startup

### 2.1 Demo Seeding (Prerequisite)
Populate the database with a demonstration organization, staff accounts, encrypted patient records, and initial clinical cases:

```powershell
cd Backend
node src/scripts/seedDemo.js
```
*Creates:*
- **Admin**: `admin@arogyamitra.gov.in` / `Admin@Pass12345!`
- **Worker (ASHA)**: `asha.shinde@arogyamitra.gov.in` / `Worker@Pass12345!`
- **Doctor (MO)**: `dr.patil@arogyamitra.gov.in` / `Doctor@Pass12345!`
- **Patients**: Ramchandra Jadhav, Sunita More, Baby Ananya (with AES-256 encrypted PII).

### 2.2 Local Process Startup

In 4 separate terminal tabs (or a background supervisor):

```powershell
# 1. Start ML Diagnostic Service
cd ML_Model
uv run uvicorn app:app --host 0.0.0.0 --port 8000

# 2. Start LangGraph Reasoning Service
cd graph
uv run uvicorn server:app --host 0.0.0.0 --port 8001

# 3. Start Backend Express API Gateway
cd Backend
node src/index.js

# 4. Start Multilingual Streamlit Clinical Workstation
cd ui
uv run streamlit run Home.py --server.port 8501
```

### 2.3 Containerized Startup (Docker Compose)
When running on an environment with Docker daemon support and adequate virtualization disk space:

```bash
docker compose up --build -d
docker compose ps
```

---

## 3. Health Checks & Observability Endpoints

All services implement standard liveness and readiness probes compatible with Kubernetes and Docker healthchecks:

| Service | Endpoint | Success Response | Function |
| :--- | :--- | :--- | :--- |
| **Backend** | `GET /health` | `{"status":"UP","timestamp":"..."}` | Liveness check |
| **Backend** | `GET /ready` | `{"status":"READY","database":"connected"}` | Readiness check |
| **Backend** | `GET /queue/metrics` | `{"queueSize":0,"activeWorkers":0,"completed":14}` | Queue monitoring |
| **ML Model** | `GET /health` | `{"status":"healthy","service":"ml-service"}` | Liveness check |
| **ML Model** | `GET /ready` | `{"status":"ready","model_loaded":true}` | Readiness check |
| **ML Model** | `GET /model-info` | `{"model_type":"LightGBM","version":"1.0.0"}` | Model metadata |
| **LangGraph** | `GET /health` | `{"status":"ok","service":"graph-service"}` | Liveness check |
| **Streamlit**| `GET /_stcore/health` | `HTTP 200 OK` | UI server liveness |

---

## 4. Disaster Recovery & Backup Runbooks

### 4.1 Database Backup (Encrypted Mongo Dump)
To create an encrypted snapshot of tenant records:

```powershell
# 1. Create BSON dump
mongodump --uri="mongodb://localhost:27017/arogyamitra" --out="D:\backups\dump_$(Get-Date -Format 'yyyyMMdd_HHmmss')"

# 2. Encrypt dump archive using OpenSSL AES-256-CBC
tar -czf - -C "D:\backups" "dump_*" | openssl enc -aes-256-cbc -salt -pbkdf2 -out "D:\backups\arogyamitra_backup.tar.gz.enc"
```

### 4.2 Database Restoration
```powershell
# Decrypt archive and restore
openssl enc -d -aes-256-cbc -pbkdf2 -in "D:\backups\arogyamitra_backup.tar.gz.enc" | tar -xzf - -C "D:\backups\restore"
mongorestore --uri="mongodb://localhost:27017/arogyamitra" --drop "D:\backups\restore\dump\arogyamitra"
```

### 4.3 Key Rotation Procedure (`ENCRYPTION_KEY`)
1. Generate new 256-bit hexadecimal key: `openssl rand -hex 32`.
2. Configure `OLD_ENCRYPTION_KEY` in environment.
3. Execute re-encryption script across `Patient` collection to decrypt ciphertext using old IV/Tag and re-encrypt using new key.
4. Promote new key to primary `ENCRYPTION_KEY` and restart backend services.
