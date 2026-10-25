# 🏥 ArogyaMitra — AI-Assisted Primary Healthcare Decision Support System

> **⚠️ Clinical Decision Support Disclaimer**: ArogyaMitra is an AI-assisted clinical decision-support system designed to assist frontline healthcare workers in rural and primary healthcare centers (PHCs). It is **not** a replacement for licensed medical doctors or definitive clinical diagnoses. All predictions, severity flags, and clinical recommendations require human review and medical validation.

---

## 📌 Architecture & System Flow

```mermaid
flowchart TD
    subgraph Client ["Client Layer"]
        User(["Frontline Healthcare Worker / Doctor / Admin"])
        UI["React 19 + Tailwind Dashboard :5173"]
    end

    subgraph Core ["Application & Data Layer"]
        API["Express 5 Backend :5000\n(Auth, Roles, Consultations, RBAC)"]
        DB[("MongoDB :27017\n(Patients, Users, Consultations)")]
    end

    subgraph AI ["AI & Clinical Pipeline"]
        GraphSvc["LangGraph Orchestration :8001\n(Workflow State, Multilingual PDF)"]
        MLSvc["FastAPI ML Microservice :8000\n(Symptom Classifier, SHAP/LIME, Severity)"]
        GeminiAPI["Google Gemini LLM\n(OpenAI-Compatible Endpoint)"]
    end

    User --> UI
    UI -->|REST / JWT| API
    API -->|Mongoose| DB
    API -->|Internal Service Call| GraphSvc
    GraphSvc -->|Feature Vector & Predict| MLSvc
    GraphSvc -->|Structured Prompt| GeminiAPI
    GraphSvc -->|Render PDF| UI
```

---

## ⚡ Setup in 5 Commands

Run the entire ArogyaMitra stack with Docker Compose:

```bash
# 1. Clone & enter repository
git clone https://github.com/Ayush-div/Arogyamitra.git && cd Arogyamitra

# 2. Set up environment variables
cp .env.example .env

# 3. Train baseline ML model artifacts (requires Python 3.11+)
python ML_Model/scripts/train_baseline.py

# 4. Build and start all services (mongo, backend, ml, graph, frontend)
docker compose up -d

# 5. Verify service health
curl http://localhost:5000/health && curl http://localhost:8000/health && curl http://localhost:8001/health
```

---

## 🛠️ Local Development (Manual Setup)

### Prerequisites
- **Node.js**: v20+ (v22 recommended)
- **Python**: v3.11+
- **MongoDB**: v6.0+ (running on `localhost:27017`)

---

### Step 1: Backend Setup
```bash
cd Backend
cp .env.example .env
npm install
npm run dev
# Listens on http://localhost:5000
# Healthcheck: http://localhost:5000/health
```

---

### Step 2: ML Prediction Microservice Setup
```bash
cd ML_Model
# Verify dataset files exist in ML_Model/dataset/ (see ML_Model/scripts/download_dataset.md)
python scripts/train_baseline.py
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
# Listens on http://localhost:8000
# Healthcheck: http://localhost:8000/health
```

---

### Step 3: LangGraph AI Pipeline Setup
```bash
cd graph
cp .env.example .env
# Configure your Google Gemini API key:
# LLM_API_KEY=your_gemini_api_key
pip install -r requirements.txt
python server.py
# Listens on http://localhost:8001
# Healthcheck: http://localhost:8001/health
```

---

### Step 4: Frontend Web App Setup
```bash
cd Frontend
npm install
npm run dev
# Listens on http://localhost:5173
```

---

## 🤖 LLM Provider Configuration

ArogyaMitra exclusively uses **Google Gemini** through its free-tier OpenAI-compatible endpoint:
- **Base URL**: `https://generativelanguage.googleapis.com/v1beta/openai/`
- **Default Model**: `gemini-1.5-flash`
- **Environment Variables**:
  - `LLM_API_KEY`: Your Gemini API key.
  - `LLM_BASE_URL`: OpenAI-compatible Gemini URL.
  - `LLM_MODEL`: Target Gemini model (`gemini-1.5-flash` or `gemini-2.0-flash`).

*Patient data privacy*: In accordance with privacy and data minimization principles, personally identifiable information (patient names, phone numbers, addresses) is never transmitted to external LLM providers.

---

## 📊 Prediction Contract (`POST /predict`)

The ML microservice exposes `POST /predict` adhering to this strict contract:

```json
{
  "primaryDiagnosis": "Fungal infection",
  "confidenceScore": 92.5,
  "severityScore": 2.67,
  "topPredictions": [
    { "disease": "Fungal infection", "confidence": 92.5 },
    { "disease": "Allergy", "confidence": 4.2 },
    { "disease": "GERD", "confidence": 1.1 }
  ],
  "matchedSymptoms": ["itching", "skin_rash"],
  "unmatchedSymptoms": [],
  "symptomSeverities": [
    { "symptom": "itching", "severity": 1 },
    { "symptom": "skin_rash", "severity": 3 }
  ],
  "precautions": ["bath twice", "use dettol or neem in bathing water"],
  "description": "Fungal infection is a common skin condition...",
  "limeExplanation": [
    { "feature": "skin_rash present", "impact": 0.45, "direction": "Supports Diagnosis" }
  ],
  "patientName": "Sunita Patil",
  "patientAge": 38,
  "patientGender": "Female",
  "workerName": "Asha Worker Anita",
  "location": "Wardha PHC"
}
```

---

## 📁 Repository Structure

```
ArogyaMitra/
├── Backend/                 # Express 5 + Mongoose 9 REST API
│   ├── src/                 # Controllers, models, routes, middlewares
│   ├── Dockerfile
│   └── package.json
├── Frontend/                # React 19 + Vite + Tailwind CSS
│   ├── src/                 # Pages, components, locales (en, hi, mr)
│   ├── Dockerfile
│   └── package.json
├── ML_Model/                # FastAPI Machine Learning Service
│   ├── app.py               # Prediction API endpoint
│   ├── dataset/             # Kaggle symptom-disease datasets
│   ├── model/               # Serialized model artifacts (.pkl, .json)
│   ├── scripts/             # Training and setup scripts
│   ├── Dockerfile
│   └── requirements.txt
├── graph/                   # LangGraph AI Pipeline & PDF Generator
│   ├── nodes/               # Graph execution nodes (XAI, LLM, PDF)
│   ├── utils/               # PDF generator with ReportLab
│   ├── server.py            # FastAPI server
│   ├── Dockerfile
│   └── requirements.txt
├── docs/                    # Architecture, Decisions, and Progress
│   ├── DECISIONS.md         # Architecture Decision Records (ADRs)
│   ├── PROGRESS.md          # Phased engineering task logs
│   └── evidence/            # Empirical benchmarks and test logs
├── docker-compose.yml       # Production baseline orchestration stack
└── .editorconfig            # Code style and formatting standards
```
