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

import ML_Model.app as ml_app
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

# ── 6. Model Architecture & Provenance Verification ───────────────────────────
def test_model_architecture_provenance():
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.naive_bayes import BernoulliNB

    import ML_Model.app as ml_app

    assert isinstance(ml_app.base_model, BernoulliNB), (
        f"Expected base_model to be BernoulliNB, got {type(ml_app.base_model)}"
    )
    assert not isinstance(ml_app.base_model, RandomForestClassifier), (
        "RandomForestClassifier detected in live prediction path! BernoulliNB required."
    )
    assert ml_app.metadata.get("model_version") == "v2.0.0", (
        f"Expected model_version v2.0.0, got {ml_app.metadata.get('model_version')}"
    )
    assert "Bernoulli Naive Bayes" in ml_app.metadata.get("model_family", ""), (
        f"Expected Bernoulli Naive Bayes in model_family, got {ml_app.metadata.get('model_family')}"
    )

# ── 7. Exact Bayesian Log-Odds Additivity Property ────────────────────────────
def test_treeshap_additivity_property():
    """
    Verifies mathematical additivity of the Bayesian log-odds feature attributions:
    phi_0 + sum(x_j * w_j) == model._joint_log_likelihood(x) within tolerance (< 1e-5).
    """
    import ML_Model.app as ml_app
    n_features = len(ml_app.symptom_columns)
    n_classes = len(ml_app.label_encoder.classes_)

    test_cases = [
        ["fever", "cough", "fatigue"],
        ["itching", "skin_rash", "nodal_skin_eruptions"],
        ["chills", "vomiting", "high_fever", "sweating"],
        ["headache", "chest_pain", "breathlessness"],
    ]

    log_theta = ml_app.base_model.feature_log_prob_
    log_one_minus_theta = np.log1p(-np.exp(log_theta))
    w = log_theta - log_one_minus_theta
    phi_0 = ml_app.base_model.class_log_prior_ + np.sum(log_one_minus_theta, axis=1)

    for symptoms in test_cases:
        x = np.zeros(n_features, dtype=np.float64)
        for s in symptoms:
            if s in ml_app.symptom_columns:
                x[ml_app.symptom_columns.index(s)] = 1.0
        x_2d = x.reshape(1, -1)

        raw_jll = ml_app.base_model._joint_log_likelihood(x_2d)[0]
        reconstructed = phi_0 + x @ w.T

        for c_idx in range(n_classes):
            assert np.isclose(reconstructed[c_idx], raw_jll[c_idx], atol=1e-5), (
                f"Bayesian additivity violated for class {c_idx}: "
                f"Reconstructed = {reconstructed[c_idx]}, raw joint log-likelihood = {raw_jll[c_idx]}"
            )

# ── 8. Calibrated Probabilities Bounds & Summation ───────────────────────────
def test_calibrated_probabilities_and_bounds():
    req = PredictRequest(symptoms=["joint_pain", "vomiting", "fatigue", "high_fever"])
    res = run_prediction(req)

    assert 0.0 <= res["confidenceScore"] <= 100.0
    for pred in res["topPredictions"]:
        assert 0.0 <= pred["confidence"] <= 100.0

    # Ensure Top-1 confidence matches top prediction
    assert res["topPredictions"][0]["disease"] == res["primaryDiagnosis"]
    assert res["topPredictions"][0]["confidence"] == res["confidenceScore"]

# ── 9. Symptom-Dropout Robustness (Omission Tolerance) ────────────────────────
def test_symptom_dropout_robustness():
    """
    Tests that a disease (e.g. Malaria) remains in the Top-3 differential diagnosis
    even when frontline workers report only a subset of symptoms (symptom omission).
    """
    full_symptoms = ["chills", "vomiting", "high_fever", "sweating", "headache", "nausea", "muscle_pain"]

    # Full presentation
    req_full = PredictRequest(symptoms=full_symptoms)
    res_full = run_prediction(req_full)
    assert res_full["primaryDiagnosis"] == "Malaria"

    # 1 symptom omitted (dropout)
    req_drop1 = PredictRequest(symptoms=["chills", "high_fever", "sweating", "headache", "muscle_pain"])
    res_drop1 = run_prediction(req_drop1)
    top3_drop1 = [p["disease"] for p in res_drop1["topPredictions"]]
    assert "Malaria" in top3_drop1, f"Expected Malaria in Top-3 after 1 drop, got {top3_drop1}"

    # 2 symptoms omitted (30% dropout)
    req_drop2 = PredictRequest(symptoms=["chills", "high_fever", "sweating", "muscle_pain"])
    res_drop2 = run_prediction(req_drop2)
    top3_drop2 = [p["disease"] for p in res_drop2["topPredictions"]]
    assert "Malaria" in top3_drop2, f"Expected Malaria in Top-3 after 2 drops, got {top3_drop2}"

# ── 10. Suggested Follow-Up Symptoms on Ambiguity ────────────────────────────
def test_suggested_follow_up_symptoms_on_uncertainty():
    """Verifies that follow-up questions are provided to differentiate between close candidates."""
    # Use ambiguous symptom presentation (e.g., fever and headache)
    req = PredictRequest(symptoms=["headache", "chest_pain"])
    res = run_prediction(req)

    assert "suggestedFollowUpSymptoms" in res
    assert isinstance(res["suggestedFollowUpSymptoms"], list)
    if res["needsEscalation"] or (len(res["topPredictions"]) > 1 and (res["topPredictions"][0]["confidence"] - res["topPredictions"][1]["confidence"] < 20.0)):
        assert len(res["suggestedFollowUpSymptoms"]) > 0
        for item in res["suggestedFollowUpSymptoms"]:
            assert "symptom" in item
            assert "relevanceScore" in item
            assert item["relevanceScore"] > 0
            assert item["symptom"] not in res["matchedSymptoms"]

# ── 11. Production TreeSHAP Attribution Verification (MC22 Target) ───────────
def test_production_treeshap_attribution_integrity():
    """Verifies that run_prediction returns exact Bayesian log-odds attributions for matched symptoms."""
    symptoms = ["joint_pain", "vomiting", "fatigue", "high_fever"]
    req = PredictRequest(symptoms=symptoms)
    res = run_prediction(req)

    assert len(res["symptomContributions"]) > 0
    top_c = ml_app.label_encoder.transform([res["primaryDiagnosis"]])[0]
    log_theta = ml_app.base_model.feature_log_prob_
    log_one_minus_theta = np.log1p(-np.exp(log_theta))
    w = log_theta - log_one_minus_theta

    for item in res["symptomContributions"]:
        s_name = item["feature"].replace(" present", "")
        s_idx = ml_app.symptom_columns.index(s_name)
        expected_imp = round(float(w[top_c, s_idx]), 4)
        assert item["impact"] == expected_imp, f"Attribution mismatch for {s_name}: got {item['impact']}, expected {expected_imp}"
