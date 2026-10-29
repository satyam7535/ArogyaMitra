"""
ArogyaMitra — Production ML Prediction Microservice (FastAPI)
Phase 1: Calibrated probabilities (BernoulliNB + CalibratedClassifierCV),
clinical uncertainty scoring, and auto-escalation flags.
"""

import json
import logging
import os
import re
from typing import Any

import joblib
import numpy as np
import yaml
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("arogyamitra-ml")

INTERNAL_SERVICE_SECRET = os.getenv("INTERNAL_SERVICE_SECRET", "")
REQUIRE_INTERNAL_AUTH = os.getenv("REQUIRE_INTERNAL_AUTH", "true").lower() in ("true", "1", "yes")

if REQUIRE_INTERNAL_AUTH and not INTERNAL_SERVICE_SECRET:
    raise RuntimeError("FATAL: INTERNAL_SERVICE_SECRET must be configured when REQUIRE_INTERNAL_AUTH is true.")

def verify_internal_service_token(
    x_internal_service_token: str | None = Header(None),
    authorization: str | None = Header(None),
):
    if not REQUIRE_INTERNAL_AUTH:
        return {"service": "unauthenticated-dev"}

    token = x_internal_service_token if isinstance(x_internal_service_token, str) else None
    if not token and isinstance(authorization, str):
        parts = authorization.split(" ")
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing internal service authentication token.",
        )

    if INTERNAL_SERVICE_SECRET and token == INTERNAL_SERVICE_SECRET:
        return {"service": "internal-shared-secret"}

    if INTERNAL_SERVICE_SECRET:
        import jwt
        try:
            # Check with audience verification
            payload = jwt.decode(
                token,
                INTERNAL_SERVICE_SECRET,
                algorithms=["HS256"],
                audience=["arogyamitra-internal", "arogyamitra-ml"]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Internal service token has expired.",
            )
        except jwt.InvalidAudienceError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid service token: Invalid audience",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Invalid service token: {e!s}",
            )

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Invalid internal service authentication token.",
    )

app = FastAPI(
    title="ArogyaMitra ML Prediction Service",
    description="Disease prediction from patient-reported symptoms with clinical escalation.",
    version="1.1.0"
)

# CORS
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "*")
allowed_origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins else ["http://localhost:5000", "http://127.0.0.1:5000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Schemas ───────────────────────────────────────────────────────────────────
class PredictRequest(BaseModel):
    symptoms: list[str] = Field(..., min_length=1, description="List of patient symptoms")
    patientName: str | None = "Patient"
    patientAge: int | None = None
    patientGender: str | None = None
    workerName: str | None = "Healthcare Worker"
    location: str | None = ""

# ── Artifact Management ───────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Check v2 directory first, then v1, fallback to base model directory
V2_DIR = os.path.join(BASE_DIR, "model", "v2")
V1_DIR = os.path.join(BASE_DIR, "model", "v1")
if os.path.exists(os.path.join(V2_DIR, "disease_model.pkl")):
    MODEL_DIR = V2_DIR
elif os.path.exists(os.path.join(V1_DIR, "disease_model.pkl")):
    MODEL_DIR = V1_DIR
else:
    MODEL_DIR = os.path.join(BASE_DIR, "model")

base_model = None
calibrator = None
shap_explainer = None
label_encoder = None
symptom_columns: list[str] = []
severity_map: dict[str, int] = {}
description_map: dict[str, str] = {}
precaution_map: dict[str, list[str]] = {}
symptom_class_matrix: dict[str, dict[str, float]] = {}
metadata: dict[str, Any] = {}
model_loaded = False
load_error_message = ""

def normalize_symptom_str(s: str) -> str:
    cleaned = s.strip().lower().replace(" ", "_")
    cleaned = re.sub(r"_+", "_", cleaned)
    mappings = {
        "dischromic__patches": "dischromic_patches",
        "spotting__urination": "spotting_urination",
        "foul_smell_ofurine": "foul_smell_of_urine",
        "fluid_overload.1": "fluid_overload",
    }
    return mappings.get(cleaned, cleaned)

def load_red_flags():
    global red_flags_config, red_flags_map
    repo_root = os.path.dirname(BASE_DIR)
    config_path = os.path.join(repo_root, "config", "red_flags.yaml")
    if not os.path.exists(config_path):
        logger.warning(f"Clinical red flags configuration not found at '{config_path}'")
        return
    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise TypeError("config/red_flags.yaml must be a valid YAML mapping")
    if data.get("status") != "DRAFT":
        raise ValueError(f"Expected red_flags status 'DRAFT', got '{data.get('status')}'")
    if data.get("reviewed_by") is not None:
        raise ValueError(f"Expected reviewed_by: null, got '{data.get('reviewed_by')}'")

    rf_items = data.get("vocabulary_red_flags", [])
    rf_map = {}
    for item in rf_items:
        s = item.get("symptom")
        if symptom_columns and s not in symptom_columns:
            raise ValueError(f"Startup validation failure: red-flag symptom '{s}' is not in clinical vocabulary!")
        rf_map[s] = item

    red_flags_config = data
    red_flags_map = rf_map
    logger.info(f"Loaded {len(red_flags_map)} clinical red-flags from '{config_path}' (Status: DRAFT)")

def load_artifacts():
    global base_model, calibrator, shap_explainer, label_encoder, symptom_columns
    global severity_map, description_map, precaution_map, symptom_class_matrix, metadata, model_loaded, load_error_message, MODEL_DIR

    # Re-evaluate MODEL_DIR in case v2 was created
    if os.path.exists(os.path.join(V2_DIR, "disease_model.pkl")):
        MODEL_DIR = V2_DIR
    elif os.path.exists(os.path.join(V1_DIR, "disease_model.pkl")):
        MODEL_DIR = V1_DIR
    else:
        MODEL_DIR = os.getenv("MODEL_DIR", os.path.join(BASE_DIR, "model"))

    required = {
        "disease_model": "disease_model.pkl",
        "label_encoder": "label_encoder.pkl",
        "symptom_columns": "symptom_columns.pkl",
        "severity_map": "severity_map.pkl",
        "description_map": "description_map.pkl",
        "precaution_map": "precaution_map.pkl",
    }

    missing = [f for key, f in required.items() if not os.path.exists(os.path.join(MODEL_DIR, f))]
    if missing:
        load_error_message = f"Missing model artifacts in '{MODEL_DIR}': {', '.join(missing)}."
        logger.warning(load_error_message)
        model_loaded = False
        return

    try:
        base_model = joblib.load(os.path.join(MODEL_DIR, required["disease_model"]))
        label_encoder = joblib.load(os.path.join(MODEL_DIR, required["label_encoder"]))
        symptom_columns = joblib.load(os.path.join(MODEL_DIR, required["symptom_columns"]))
        severity_map = joblib.load(os.path.join(MODEL_DIR, required["severity_map"]))
        description_map = joblib.load(os.path.join(MODEL_DIR, required["description_map"]))
        precaution_map = joblib.load(os.path.join(MODEL_DIR, required["precaution_map"]))

        # Calibrated classifier (Platt / Isotonic)
        cal_path = os.path.join(MODEL_DIR, "calibrator.pkl")
        calibrator = joblib.load(cal_path) if os.path.exists(cal_path) else None

        # TreeSHAP explainer
        shap_path = os.path.join(MODEL_DIR, "shap_explainer.pkl")
        shap_explainer = joblib.load(shap_path) if os.path.exists(shap_path) else None

        # Symptom-disease characteristic frequency matrix
        matrix_path = os.path.join(MODEL_DIR, "symptom_class_matrix.json")
        if os.path.exists(matrix_path):
            with open(matrix_path, "r", encoding="utf-8") as f:
                symptom_class_matrix = json.load(f)
        else:
            symptom_class_matrix = {}

        meta_path = os.path.join(MODEL_DIR, "metadata.json")
        if os.path.exists(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)

        # Load and validate clinical red flags configuration
        load_red_flags()

        model_loaded = True
        logger.info(f"Loaded ML artifacts from '{MODEL_DIR}'. Known symptoms: {len(symptom_columns)}")
    except Exception as e:
        load_error_message = f"Failed to load artifacts from '{MODEL_DIR}': {e!s}"
        logger.error(load_error_message)
        model_loaded = False

# Initial artifact loading
load_artifacts()

# ── Inference Engine ──────────────────────────────────────────────────────────
def run_prediction(req: PredictRequest) -> dict[str, Any]:
    if not model_loaded:
        load_artifacts()
    if not model_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=load_error_message or "Model artifacts are not loaded. Train the model first."
        )

    # 1. Vocabulary validation and feature vector construction
    input_vector = np.zeros(len(symptom_columns), dtype=np.float64)
    matched: list[str] = []
    unmatched: list[str] = []
    symptom_severities: list[dict[str, Any]] = []

    for s in req.symptoms:
        s_norm = normalize_symptom_str(s)
        if s_norm in symptom_columns:
            idx = symptom_columns.index(s_norm)
            input_vector[idx] = 1.0
            matched.append(s_norm)
            symptom_severities.append({
                "symptom": s_norm,
                "severity": int(severity_map.get(s_norm, 1))
            })
        else:
            unmatched.append(s)

    if not matched:
        raise HTTPException(
            status_code=422,
            detail=f"None of the provided symptoms were recognized in the clinical vocabulary. Unmatched: {unmatched}"
        )

    # 2. Probability Prediction (Native Multi-Class Probabilities)
    input_2d = input_vector.reshape(1, -1)
    if calibrator is not None:
        proba = calibrator.predict_proba(input_2d)[0]
    elif base_model is not None and hasattr(base_model, "predict_proba"):
        proba = base_model.predict_proba(input_2d)[0]
    elif base_model is not None and hasattr(base_model, "_Booster") and base_model._Booster is not None:
        proba = base_model._Booster.predict(input_2d)[0]
    else:
        import pandas as pd
        input_df = pd.DataFrame([input_vector], columns=symptom_columns)
        proba = base_model.predict_proba(input_df)[0]

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

    # Margin between top-1 and top-2
    margin = (top_predictions[0]["confidence"] - top_predictions[1]["confidence"]) if len(top_predictions) > 1 else 100.0

    # 3. Clinical Severity Score
    severities = [s["severity"] for s in symptom_severities]
    avg_severity = round(float(np.mean(severities)), 2)
    max_severity = max(severities) if severities else 1

    # 4. Clinical Red-Flag Rule Layer & Auto-Escalation Triggers
    matched_red_flags: list[dict[str, Any]] = [
        red_flags_map[s] for s in matched if s in red_flags_map
    ]
    has_red_flag = len(matched_red_flags) > 0

    escalation_reasons: list[str] = []
    if has_red_flag:
        for rf in matched_red_flags:
            escalation_reasons.append(
                f"🚨 CLINICAL RED FLAG: '{rf['symptom']}' ({rf.get('clinical_rationale', 'Critical condition')}). Immediate physician evaluation required. [DRAFT: Pending Clinical Review]"
            )
    if top_confidence < 70.0:
        escalation_reasons.append(f"Low diagnostic confidence ({top_confidence}% < 70%). Physician review recommended.")
    if margin < 25.0:
        escalation_reasons.append(f"Narrow diagnostic margin ({margin:.1f}% < 25%) between primary and secondary differential diagnoses.")
    if max_severity >= 5 or avg_severity >= 4.5:
        escalation_reasons.append(f"High clinical acuity symptom detected (max severity: {max_severity}/7). Urgent escalation advised.")

    needs_escalation = len(escalation_reasons) > 0
    uncertainty_reason = " | ".join(escalation_reasons) if needs_escalation else None

    # Forced risk level: red-flag forces risk >= High
    if has_red_flag or max_severity >= 6:
        risk_level = "High"
    elif max_severity >= 4 or needs_escalation:
        risk_level = "Moderate"
    else:
        risk_level = "Low" 

    # 5. Exact Additive Feature Attributions (Bayesian Log-Odds / Weight of Evidence)
    symptom_explanations: list[dict[str, Any]] = []
    top_idx = top_indices[0]

    if base_model is not None and hasattr(base_model, "feature_log_prob_"):
        # Bernoulli Naive Bayes exact additive log-odds
        log_theta = base_model.feature_log_prob_
        log_one_minus_theta = np.log1p(-np.exp(log_theta))
        w = log_theta - log_one_minus_theta

        for s_name in matched:
            s_idx = symptom_columns.index(s_name)
            imp = float(w[top_idx, s_idx])
            symptom_explanations.append({
                "feature": f"{s_name} present",
                "impact": round(imp, 4),
                "direction": "Supports Diagnosis" if imp >= 0 else "Against Diagnosis",
                "method": "Exact Bayesian Log-Odds"
            })

        symptom_explanations.sort(key=lambda x: abs(x["impact"]), reverse=True)
    elif base_model is not None and hasattr(base_model, "_Booster") and base_model._Booster is not None:
        try:
            contribs = base_model._Booster.predict(input_2d, pred_contrib=True)
            n_features = len(symptom_columns)
            n_classes = len(label_encoder.classes_) if label_encoder is not None else 41
            contribs_3d = contribs.reshape(input_2d.shape[0], n_classes, n_features + 1)
            class_shap = contribs_3d[0, top_idx, :n_features]

            for s_name in matched:
                s_idx = symptom_columns.index(s_name)
                imp = float(class_shap[s_idx])
                symptom_explanations.append({
                    "feature": f"{s_name} present",
                    "impact": round(imp, 4),
                    "direction": "Supports Diagnosis" if imp >= 0 else "Against Diagnosis",
                    "method": "TreeSHAP"
                })

            symptom_explanations.sort(key=lambda x: abs(x["impact"]), reverse=True)
        except Exception as e:
            logger.warning(f"Feature attribution fallback: {e}")

    # Fallback explanation if model attribution unavailable
    if not symptom_explanations:
        for s_item in symptom_severities:
            symptom_explanations.append({
                "feature": f"{s_item['symptom']} present",
                "impact": round(0.15 * s_item["severity"], 4),
                "direction": "Supports Diagnosis",
                "method": "Clinical Acuity Heuristic"
            })

    # Backward-compatible aliases for SHAP / LIME consumers
    shap_explanations = symptom_explanations
    lime_explanations = symptom_explanations

    # 6. Disease metadata & Precautions
    disease_desc = description_map.get(top_disease, "Clinical disease information not available.")
    disease_precautions = precaution_map.get(
        top_disease,
        ["Consult a qualified medical practitioner for detailed clinical assessment."]
    )

    # 7. Follow-Up Question Suggestions (when margin is narrow or confidence is low or needs escalation)
    suggested_follow_ups: list[dict[str, Any]] = []
    if (margin < 30.0 or top_confidence < 75.0 or needs_escalation) and len(top_predictions) >= 2 and symptom_class_matrix:
        d1 = top_predictions[0]["disease"]
        d2 = top_predictions[1]["disease"]
        d1_symptoms = symptom_class_matrix.get(d1, {})
        d2_symptoms = symptom_class_matrix.get(d2, {})

        candidate_symptoms = set(d1_symptoms.keys()).union(set(d2_symptoms.keys()))
        unreported_candidates = candidate_symptoms - set(matched)

        scored_candidates = []
        for s_cand in unreported_candidates:
            p1 = d1_symptoms.get(s_cand, 0.0)
            p2 = d2_symptoms.get(s_cand, 0.0)
            diff = abs(p1 - p2)
            if diff > 0.0:
                scored_candidates.append({
                    "symptom": s_cand,
                    "relevanceScore": round(diff, 2),
                    "differentiatingBetween": [d1, d2],
                    "reason": f"Differentiates {d1} ({int(p1*100)}%) from {d2} ({int(p2*100)}%)"
                })

        # Sort by relevance descending and take top 5
        scored_candidates.sort(key=lambda x: x["relevanceScore"], reverse=True)
        suggested_follow_ups = scored_candidates[:5]

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
        "symptomContributions": symptom_explanations,
        "explanationMethod": symptom_explanations[0]["method"] if symptom_explanations else "Exact Bayesian Log-Odds",
        "shapExplanation": shap_explanations,
        "limeExplanation": lime_explanations,
        "needsEscalation": needs_escalation,
        "redFlag": has_red_flag,
        "risk": risk_level,
        "redFlagDetails": matched_red_flags,
        "clinicalReviewNotice": red_flags_config.get("notice") if has_red_flag else None,
        "uncertaintyReason": uncertainty_reason,
        "suggestedFollowUpSymptoms": suggested_follow_ups,
        # Echoed metadata
        "patientName": req.patientName,
        "patientAge": req.patientAge,
        "patientGender": req.patientGender,
        "workerName": req.workerName,
        "location": req.location,
        # Model metadata
        "modelUsed": metadata.get("model_family", "Bernoulli Naive Bayes + Exact Bayesian Log-Odds"),
        "modelVersion": metadata.get("model_version", "v2.0.0"),
        "modelAccuracy": metadata.get("in_sample_metrics_on_clean_data", {}).get("accuracy", 1.0) * 100,
    }

# ── API Routes ────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {
        "message": "ArogyaMitra ML Prediction API",
        "status": "running",
        "model_loaded": model_loaded,
        "version": metadata.get("model_version", "v1.0.0")
    }

@app.get("/health")
def health():
    return {
        "status": "healthy" if model_loaded else "degraded",
        "service": "ml",
        "model_loaded": model_loaded,
        "total_symptoms": len(symptom_columns)
    }

@app.get("/ready")
def ready():
    if not model_loaded:
        load_artifacts()
    if not model_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=load_error_message or "Model service is not ready."
        )
    return {
        "status": "ready",
        "model_loaded": True,
        "version": metadata.get("model_version", "v1.0.0"),
        "total_symptoms": len(symptom_columns),
        "total_classes": len(label_encoder.classes_) if label_encoder else 0
    }

@app.get("/model-info")
def model_info():
    if not model_loaded:
        load_artifacts()
    return {
        "modelVersion": metadata.get("model_version", "v1.0.0"),
        "algorithm": metadata.get("model_family", "BernoulliNB + CalibratedClassifierCV"),
        "trainingTimestamp": metadata.get("training_timestamp"),
        "gitCommit": metadata.get("git_commit"),
        "dataset": metadata.get("dataset"),
        "metrics": metadata.get("metrics_on_unique_ground_truth"),
        "totalSymptoms": len(symptom_columns),
        "totalClasses": len(label_encoder.classes_) if label_encoder else 0,
        "classes": list(label_encoder.classes_) if label_encoder else []
    }

@app.get("/symptoms")
def get_symptoms():
    if not model_loaded:
        load_artifacts()
    if not model_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=load_error_message or "Model not loaded"
        )
    return {
        "total": len(symptom_columns),
        "symptoms": [
            {
                "id": s,
                "label": s.replace("_", " ").title(),
                "severity": int(severity_map.get(s, 1))
            }
            for s in symptom_columns
        ]
    }

@app.post("/predict")
def predict(req: PredictRequest, auth: Any = Depends(verify_internal_service_token)):  # noqa: B008
    if not req.symptoms:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one symptom is required."
        )
    return run_prediction(req)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run("app:app", host="127.0.0.1", port=port, reload=False)
