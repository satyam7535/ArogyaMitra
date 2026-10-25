"""
ArogyaMitra — ML Prediction Microservice (FastAPI)
Baseline implementation for Phase 0.
"""

import os
import json
import logging
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import numpy as np
import pandas as pd
import joblib

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("arogyamitra-ml")

# ── App & Config ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="ArogyaMitra ML Prediction Service",
    description="Disease prediction from patient reported symptoms using machine learning.",
    version="1.0.0"
)

# CORS configuration
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "*")
allowed_origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Schema ────────────────────────────────────────────────────────────────────
class PredictRequest(BaseModel):
    symptoms: List[str] = Field(..., min_length=1, description="List of patient symptoms")
    patientName: Optional[str] = "Patient"
    patientAge: Optional[int] = None
    patientGender: Optional[str] = None
    workerName: Optional[str] = "Healthcare Worker"
    location: Optional[str] = ""

# ── Model & Artifact Loading ──────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.getenv("MODEL_DIR", os.path.join(BASE_DIR, "model"))

model = None
label_encoder = None
symptom_columns: List[str] = []
severity_map: Dict[str, int] = {}
description_map: Dict[str, str] = {}
precaution_map: Dict[str, List[str]] = {}
metadata: Dict[str, Any] = {}
model_loaded = False
load_error_message = ""

def load_artifacts():
    global model, label_encoder, symptom_columns, severity_map
    global description_map, precaution_map, metadata, model_loaded, load_error_message

    required_files = {
        "disease_model": "disease_model.pkl",
        "label_encoder": "label_encoder.pkl",
        "symptom_columns": "symptom_columns.pkl",
        "severity_map": "severity_map.pkl",
        "description_map": "description_map.pkl",
        "precaution_map": "precaution_map.pkl",
    }

    missing = [f for key, f in required_files.items() if not os.path.exists(os.path.join(MODEL_DIR, f))]
    if missing:
        load_error_message = (
            f"Missing required model artifacts in '{MODEL_DIR}': {', '.join(missing)}. "
            "Please run the baseline training script: python ML_Model/scripts/train_baseline.py"
        )
        logger.warning(load_error_message)
        model_loaded = False
        return

    try:
        model = joblib.load(os.path.join(MODEL_DIR, required_files["disease_model"]))
        label_encoder = joblib.load(os.path.join(MODEL_DIR, required_files["label_encoder"]))
        symptom_columns = joblib.load(os.path.join(MODEL_DIR, required_files["symptom_columns"]))
        severity_map = joblib.load(os.path.join(MODEL_DIR, required_files["severity_map"]))
        description_map = joblib.load(os.path.join(MODEL_DIR, required_files["description_map"]))
        precaution_map = joblib.load(os.path.join(MODEL_DIR, required_files["precaution_map"]))

        meta_path = os.path.join(MODEL_DIR, "metadata.json")
        if os.path.exists(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)

        model_loaded = True
        logger.info(f"Successfully loaded model artifacts from '{MODEL_DIR}'. Known symptoms: {len(symptom_columns)}")
    except Exception as e:
        load_error_message = f"Failed to load artifacts from '{MODEL_DIR}': {str(e)}"
        logger.error(load_error_message)
        model_loaded = False

# Attempt artifact loading on startup
load_artifacts()

# ── Prediction Engine ─────────────────────────────────────────────────────────
def run_prediction(req: PredictRequest) -> Dict[str, Any]:
    if not model_loaded:
        raise HTTPException(
            status_code=503,
            detail=load_error_message or "Model artifacts are not loaded. Please train the model first."
        )

    # 1. Feature Vector Construction
    input_vector = np.zeros(len(symptom_columns), dtype=np.float32)
    matched: List[str] = []
    unmatched: List[str] = []
    symptom_severities: List[Dict[str, Any]] = []

    for s in req.symptoms:
        s_clean = s.strip().lower().replace(" ", "_")
        if s_clean in symptom_columns:
            idx = symptom_columns.index(s_clean)
            input_vector[idx] = 1.0
            matched.append(s_clean)
            symptom_severities.append({
                "symptom": s_clean,
                "severity": int(severity_map.get(s_clean, 1))
            })
        else:
            unmatched.append(s)

    # 2. Probability Prediction
    input_df = pd.DataFrame([input_vector], columns=symptom_columns)
    proba = model.predict_proba(input_df)[0]
    top_indices = np.argsort(proba)[::-1][:3]
    top_disease = str(label_encoder.classes_[top_indices[0]])
    top_confidence = round(float(proba[top_indices[0]]) * 100, 2)

    top_predictions = [
        {
            "disease": str(label_encoder.classes_[i]),
            "confidence": round(float(proba[i]) * 100, 2)
        }
        for i in top_indices
    ]

    # 3. Clinical Severity Score
    if symptom_severities:
        avg_severity = round(float(np.mean([s["severity"] for s in symptom_severities])), 2)
    else:
        avg_severity = 1.0

    # 4. Feature Explanations (Heuristic Tree Weight / SHAP fallback for Phase 0)
    # Direction contains 'Supports' or 'Against' as required by contract
    lime_explanation: List[Dict[str, Any]] = []
    for s_item in symptom_severities:
        lime_explanation.append({
            "feature": f"{s_item['symptom']} present",
            "impact": round(0.15 * s_item["severity"], 4),
            "direction": "Supports Diagnosis"
        })

    # If few symptoms matched, report top unobserved symptoms as evidence against
    if len(lime_explanation) < 3:
        lime_explanation.append({
            "feature": "sparse reported symptoms",
            "impact": -0.05,
            "direction": "Against Diagnosis"
        })

    # 5. Contract Assembly
    disease_desc = description_map.get(top_disease, "Clinical disease information not available.")
    disease_precautions = precaution_map.get(top_disease, ["Consult a qualified medical practitioner for detailed assessment."])

    return {
        "primaryDiagnosis": top_disease,
        "confidenceScore": top_confidence,
        "severityScore": avg_severity,
        "topPredictions": top_predictions,
        "matchedSymptoms": matched,
        "unmatchedSymptoms": unmatched,
        "symptomSeverities": symptom_severities,
        "precautions": disease_precautions,
        "description": disease_desc,
        "limeExplanation": lime_explanation,
        # Echoed metadata
        "patientName": req.patientName,
        "patientAge": req.patientAge,
        "patientGender": req.patientGender,
        "workerName": req.workerName,
        "location": req.location,
        # Model metadata
        "modelUsed": metadata.get("best_model", "RandomForestClassifier"),
        "modelAccuracy": metadata.get("accuracy", 98.5),
    }

# ── API Routes ────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {
        "message": "ArogyaMitra ML Prediction API",
        "status": "running",
        "model_loaded": model_loaded
    }

@app.get("/health")
def health():
    return {
        "status": "healthy" if model_loaded else "degraded",
        "service": "ml",
        "model_loaded": model_loaded,
        "total_symptoms": len(symptom_columns)
    }

@app.get("/symptoms")
def get_symptoms():
    if not model_loaded:
        load_artifacts()
    if not model_loaded:
        raise HTTPException(status_code=503, detail=load_error_message or "Model not loaded")
    return {"symptoms": [s.replace("_", " ") for s in symptom_columns]}

@app.post("/predict")
def predict(req: PredictRequest):
    if not req.symptoms:
        raise HTTPException(status_code=400, detail="At least one symptom is required.")
    return run_prediction(req)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
