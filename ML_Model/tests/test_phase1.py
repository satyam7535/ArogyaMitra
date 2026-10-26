"""
ArogyaMitra — Phase 1 Test Suite
Validates data leakage prevention, probability calibration bounds,
TreeSHAP explainability contract, clinical uncertainty triggers, and vocabulary validation.
"""

import os
import sys

import numpy as np
import pytest
from fastapi import HTTPException

# Ensure root is on path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ML_Model.app import (
    PredictRequest,
    get_symptoms,
    health,
    load_artifacts,
    model_info,
    ready,
    run_prediction,
)
from ML_Model.training.prepare_data import load_and_clean_data, normalize_symptom_name


@pytest.fixture(scope="session", autouse=True)
def ensure_artifacts():
    load_artifacts()

# ── 1. Data Leakage Prevention ────────────────────────────────────────────────
def test_no_data_leakage_in_clean_data():
    csv_path = os.path.join(BASE_DIR, "ML_Model", "dataset", "Training.csv")
    if not os.path.exists(csv_path):
        pytest.skip("Dataset file not available locally")

    data = load_and_clean_data(csv_path, deduplicate=True)
    X = data["X"]
    # Verify that all 304 unique rows are strictly unique
    unique_rows = np.unique(X, axis=0)
    assert len(unique_rows) == len(X), "Cleaned dataset contains duplicate rows!"
    assert len(X) == 304, f"Expected 304 unique rows, got {len(X)}"
    assert data["stats"]["duplicate_rows_dropped"] == 4616

def test_symptom_name_normalization():
    assert normalize_symptom_name("foul_smell_ofurine") == "foul_smell_of_urine"
    assert normalize_symptom_name("spotting__urination") == "spotting_urination"
    assert normalize_symptom_name("dischromic__patches") == "dischromic_patches"
    assert normalize_symptom_name("fluid_overload.1") == "fluid_overload"

# ── 2. Full Prediction Contract ───────────────────────────────────────────────
def test_prediction_contract_complete():
    req = PredictRequest(
        symptoms=["itching", "skin_rash", "nodal_skin_eruptions"],
        patientName="Aarav Sharma",
        patientAge=34,
        patientGender="Male",
        workerName="Sunita Devi",
        location="Gaya Sub-center"
    )
    res = run_prediction(req)

    # Core diagnosis fields
    assert isinstance(res["primaryDiagnosis"], str) and len(res["primaryDiagnosis"]) > 0
    assert isinstance(res["confidenceScore"], (float, int))
    assert 0.0 <= res["confidenceScore"] <= 100.0
    assert isinstance(res["severityScore"], (float, int))
    assert 1.0 <= res["severityScore"] <= 7.0

    # Differential predictions
    assert isinstance(res["topPredictions"], list)
    assert len(res["topPredictions"]) == 3
    for p in res["topPredictions"]:
        assert "disease" in p and "confidence" in p
        assert 0.0 <= p["confidence"] <= 100.0

    # Precautions & description
    assert isinstance(res["precautions"], list) and len(res["precautions"]) > 0
    assert isinstance(res["description"], str) and len(res["description"]) > 0

    # TreeSHAP & LIME explanations
    assert isinstance(res["shapExplanation"], list) and len(res["shapExplanation"]) > 0
    for exp in res["shapExplanation"]:
        assert "feature" in exp
        assert "impact" in exp
        assert exp["direction"] in ["Supports Diagnosis", "Against Diagnosis"]
    assert "limeExplanation" in res
    assert len(res["limeExplanation"]) == len(res["shapExplanation"])

    # Uncertainty & escalation
    assert isinstance(res["needsEscalation"], bool)
    if res["needsEscalation"]:
        assert isinstance(res["uncertaintyReason"], str) and len(res["uncertaintyReason"]) > 0

    # Metadata echo
    assert res["patientName"] == "Aarav Sharma"
    assert res["patientAge"] == 34
    assert res["workerName"] == "Sunita Devi"
    assert "modelVersion" in res
    assert "modelUsed" in res

# ── 3. High Acuity Escalation Trigger ─────────────────────────────────────────
def test_high_acuity_triggers_escalation():
    # chest_pain has severity 7 (highest clinical weight)
    req = PredictRequest(symptoms=["chest_pain", "breathlessness", "sweating"])
    res = run_prediction(req)

    assert res["needsEscalation"] is True
    assert "acuity" in res["uncertaintyReason"].lower() or "severity" in res["uncertaintyReason"].lower() or "review" in res["uncertaintyReason"].lower()

# ── 4. Vocabulary Validation ──────────────────────────────────────────────────
def test_unrecognized_symptoms_handling():
    req = PredictRequest(symptoms=["itching", "completely_fake_symptom_abc123"])
    res = run_prediction(req)

    assert "itching" in res["matchedSymptoms"]
    assert "completely_fake_symptom_abc123" in res["unmatchedSymptoms"]

def test_all_unrecognized_symptoms_raises_422():
    req = PredictRequest(symptoms=["completely_fake_symptom_abc123", "another_unknown_xyz"])
    with pytest.raises(HTTPException) as exc_info:
        run_prediction(req)
    assert exc_info.value.status_code == 422
    assert "None of the provided symptoms were recognized" in exc_info.value.detail

# ── 5. Endpoints Verification ─────────────────────────────────────────────────
def test_health_and_ready_endpoints():
    h = health()
    assert h["status"] in ["healthy", "degraded"]
    assert h["service"] == "ml"

    r = ready()
    assert r["status"] == "ready"
    assert r["total_symptoms"] > 100

def test_model_info_endpoint():
    info = model_info()
    assert "modelVersion" in info
    assert "algorithm" in info
    assert info["totalSymptoms"] > 100
    assert info["totalClasses"] == 41

def test_symptoms_endpoint():
    symp = get_symptoms()
    assert symp["total"] > 100
    assert len(symp["symptoms"]) == symp["total"]
    first = symp["symptoms"][0]
    assert "id" in first and "label" in first and "severity" in first
