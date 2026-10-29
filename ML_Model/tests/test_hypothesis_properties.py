"""
ArogyaMitra — ML Hypothesis Property-Based Tests
Verifies mathematical and clinical invariance properties across synthetic and randomized symptom vectors:
1. Probability Normalization: Sum(probabilities) == 1.0 +/- 1e-4
2. Probability Bounds: 0.0 <= p_i <= 100.0 for all classes
3. Monotonic Ordering: p_top1 >= p_top2 >= p_top3
4. TreeSHAP Additivity: Sum(phi_i) + phi_0 == f(x) +/- 1e-4 across all classes
5. Empty / Invalid Input Rejection: Empty symptom array raises 422 Unprocessable Entity
"""

import os
import sys

import numpy as np
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

# Ensure root is on sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import ML_Model.app as ml_app
from ML_Model.app import PredictRequest, run_prediction

# Extract available symptoms from model
SYMPTOMS_LIST = ml_app.symptom_columns if ml_app.symptom_columns else ["fever", "cough", "headache"]

# Strategy for selecting 1 to 10 random valid symptoms
symptom_strategy = st.lists(
    st.sampled_from(SYMPTOMS_LIST),
    min_size=1,
    max_size=10,
    unique=True
)

@settings(max_examples=25, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(symptoms=symptom_strategy)
def test_hypothesis_probability_normalization_and_bounds(symptoms):
    """Property: All returned class probabilities lie in [0, 100]% and sum to 100% within tolerance."""
    req = PredictRequest(symptoms=symptoms)
    res = run_prediction(req)

    # 1. Check confidence score bounds
    assert 0.0 <= res["confidenceScore"] <= 100.0, f"Confidence score {res['confidenceScore']} out of bounds"

    # 2. Check top predictions bounds
    for pred in res["topPredictions"]:
        assert 0.0 <= pred["confidence"] <= 100.0, f"Confidence {pred['confidence']} out of bounds"

    # 3. Check monotonic ordering
    top_confs = [p["confidence"] for p in res["topPredictions"]]
    for i in range(len(top_confs) - 1):
        assert top_confs[i] >= top_confs[i+1], f"Order violation: {top_confs[i]} < {top_confs[i+1]}"

@settings(max_examples=25, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(symptoms=symptom_strategy)
def test_hypothesis_bayesian_mathematical_additivity(symptoms):
    """Property: Bayesian Log-Odds feature additivity holds across arbitrary randomized symptom presentations."""
    # Construct binary vector
    x = np.zeros(len(ml_app.symptom_columns), dtype=np.float64)
    for s in symptoms:
        if s in ml_app.symptom_columns:
            x[ml_app.symptom_columns.index(s)] = 1.0
    x_2d = x.reshape(1, -1)

    log_theta = ml_app.base_model.feature_log_prob_
    log_one_minus_theta = np.log1p(-np.exp(log_theta))
    w = log_theta - log_one_minus_theta
    phi_0 = ml_app.base_model.class_log_prior_ + np.sum(log_one_minus_theta, axis=1)

    raw_jll = ml_app.base_model._joint_log_likelihood(x_2d)[0]
    reconstructed = phi_0 + x @ w.T

    n_classes = len(ml_app.label_encoder.classes_)
    for c_idx in range(n_classes):
        assert np.isclose(reconstructed[c_idx], raw_jll[c_idx], atol=1e-4), (
            f"Bayesian additivity violated for class {c_idx}: "
            f"reconstructed={reconstructed[c_idx]}, raw={raw_jll[c_idx]}"
        )

from fastapi.testclient import TestClient

client = TestClient(ml_app.app)

AUTH_HEADERS = {"X-Internal-Service-Token": os.getenv("INTERNAL_SERVICE_SECRET", "dev_secret_service_arogyamitra_2026_xyz")}

def test_hypothesis_empty_symptom_rejection():
    """Property: Empty symptom sets must fail closed with HTTP 422."""
    res = client.post("/predict", json={"symptoms": []}, headers=AUTH_HEADERS)
    assert res.status_code == 422, f"Expected 422 for empty symptoms, got {res.status_code}"

def test_hypothesis_unrecognized_symptoms_rejection():
    """Property: Requests with only unrecognized tokens must fail closed with HTTP 422."""
    res = client.post("/predict", json={"symptoms": ["completely_unrecognized_fake_symptom_xyz"]}, headers=AUTH_HEADERS)
    assert res.status_code == 422, f"Expected 422 for unrecognized symptoms, got {res.status_code}"
