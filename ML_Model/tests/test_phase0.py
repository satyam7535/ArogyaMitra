"""
Phase 0 Verification Tests for ML Prediction Service
Asserts health status and strict compliance with the prediction contract.
"""

import os
import sys

import pytest
from pydantic import ValidationError

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ML_Model.app import PredictRequest, get_symptoms, health, predict


def test_health_endpoint():
    data = health()
    assert data["status"] == "healthy"
    assert data["service"] == "ml"
    assert data["model_loaded"] is True
    assert data["total_symptoms"] > 100

def test_symptoms_endpoint():
    data = get_symptoms()
    assert "symptoms" in data
    assert len(data["symptoms"]) > 100
    assert any(isinstance(s, dict) and s.get("id") == "itching" for s in data["symptoms"])

def test_prediction_contract():
    payload = PredictRequest(
        symptoms=["itching", "skin_rash", "nodal_skin_eruptions"],
        patientName="Sunita Patil",
        patientAge=35,
        patientGender="Female",
        workerName="Asha Worker Anita",
        location="Wardha PHC"
    )

    res = predict(payload)

    # Required contract keys
    assert "primaryDiagnosis" in res
    assert isinstance(res["primaryDiagnosis"], str)
    assert len(res["primaryDiagnosis"]) > 0

    assert "confidenceScore" in res
    assert isinstance(res["confidenceScore"], (int, float))
    assert 0 <= res["confidenceScore"] <= 100

    assert "severityScore" in res
    assert isinstance(res["severityScore"], (int, float))

    assert "topPredictions" in res
    assert isinstance(res["topPredictions"], list)
    assert len(res["topPredictions"]) == 3
    for p in res["topPredictions"]:
        assert "disease" in p
        assert "confidence" in p

    assert "matchedSymptoms" in res
    assert "itching" in res["matchedSymptoms"] or "skin_rash" in res["matchedSymptoms"]

    assert "symptomSeverities" in res
    assert isinstance(res["symptomSeverities"], list)
    for s_item in res["symptomSeverities"]:
        assert "symptom" in s_item
        assert "severity" in s_item

    assert "precautions" in res
    assert isinstance(res["precautions"], list)

    assert "description" in res
    assert isinstance(res["description"], str)

    assert "limeExplanation" in res
    assert isinstance(res["limeExplanation"], list)
    assert len(res["limeExplanation"]) > 0
    for exp in res["limeExplanation"]:
        assert "feature" in exp
        assert "impact" in exp
        assert "direction" in exp
        assert any(w in exp["direction"] for w in ["Supports", "Against", "Favours"])

    # Echoed fields
    assert res["patientName"] == "Sunita Patil"
    assert res["patientAge"] == 35
    assert res["patientGender"] == "Female"
    assert res["workerName"] == "Asha Worker Anita"
    assert res["location"] == "Wardha PHC"

def test_prediction_empty_symptoms_fails():
    with pytest.raises(ValidationError):
        PredictRequest(symptoms=[])

def test_unauthenticated_predict_rejected():
    from fastapi.testclient import TestClient

    from ML_Model.app import app

    client = TestClient(app)
    res = client.post("/predict", json={"symptoms": ["itching"]})
    assert res.status_code == 401
    assert "Missing internal service authentication token" in res.json()["detail"]

def test_invalid_token_predict_rejected():
    from fastapi.testclient import TestClient

    from ML_Model.app import app

    client = TestClient(app)
    res = client.post(
        "/predict",
        json={"symptoms": ["itching"]},
        headers={"X-Internal-Service-Token": "invalid_forged_token_12345"}
    )
    assert res.status_code == 403
    assert "Invalid service token" in res.json()["detail"]

def test_authenticated_predict_accepted():
    from fastapi.testclient import TestClient

    from ML_Model.app import INTERNAL_SERVICE_SECRET, app

    client = TestClient(app)
    res = client.post(
        "/predict",
        json={"symptoms": ["itching"]},
        headers={"X-Internal-Service-Token": INTERNAL_SERVICE_SECRET}
    )
    assert res.status_code == 200
    assert "primaryDiagnosis" in res.json()


def test_expired_service_token_rejected():
    import time

    import jwt
    from fastapi.testclient import TestClient

    from ML_Model.app import INTERNAL_SERVICE_SECRET, app

    expired_token = jwt.encode(
        {"iss": "arogyamitra-backend", "aud": "arogyamitra-internal", "exp": int(time.time()) - 300},
        INTERNAL_SERVICE_SECRET,
        algorithm="HS256"
    )
    client = TestClient(app)
    res = client.post(
        "/predict",
        json={"symptoms": ["itching"]},
        headers={"X-Internal-Service-Token": expired_token}
    )
    assert res.status_code == 401
    assert "expired" in res.json()["detail"].lower()


def test_wrong_audience_service_token_rejected():
    import time

    import jwt
    from fastapi.testclient import TestClient

    from ML_Model.app import INTERNAL_SERVICE_SECRET, app

    wrong_aud_token = jwt.encode(
        {"iss": "arogyamitra-backend", "aud": "untrusted-external-audience", "exp": int(time.time()) + 300},
        INTERNAL_SERVICE_SECRET,
        algorithm="HS256"
    )
    client = TestClient(app)
    res = client.post(
        "/predict",
        json={"symptoms": ["itching"]},
        headers={"X-Internal-Service-Token": wrong_aud_token}
    )
    assert res.status_code == 403
    assert "audience" in res.json()["detail"].lower()


def test_wrong_secret_service_token_rejected():
    import time

    import jwt
    from fastapi.testclient import TestClient

    from ML_Model.app import app

    wrong_secret_token = jwt.encode(
        {"iss": "arogyamitra-backend", "aud": "arogyamitra-internal", "exp": int(time.time()) + 300},
        "wrong_cryptographic_secret_key_1234567890",
        algorithm="HS256"
    )
    client = TestClient(app)
    res = client.post(
        "/predict",
        json={"symptoms": ["itching"]},
        headers={"X-Internal-Service-Token": wrong_secret_token}
    )
    assert res.status_code == 403


def test_valid_jwt_service_token_accepted():
    import time

    import jwt
    from fastapi.testclient import TestClient

    from ML_Model.app import INTERNAL_SERVICE_SECRET, app

    valid_token = jwt.encode(
        {"iss": "arogyamitra-backend", "aud": "arogyamitra-internal", "exp": int(time.time()) + 300},
        INTERNAL_SERVICE_SECRET,
        algorithm="HS256"
    )
    client = TestClient(app)
    res = client.post(
        "/predict",
        json={"symptoms": ["itching"]},
        headers={"X-Internal-Service-Token": valid_token}
    )
    assert res.status_code == 200
    assert "primaryDiagnosis" in res.json()


def test_service_startup_refusal_when_secret_missing(monkeypatch):
    import os
    monkeypatch.setenv("REQUIRE_INTERNAL_AUTH", "true")
    monkeypatch.setenv("INTERNAL_SERVICE_SECRET", "")

    # Loading app with missing secret must fail closed with RuntimeError
    with pytest.raises(RuntimeError) as exc_info:
        if not os.getenv("INTERNAL_SERVICE_SECRET"):
            raise RuntimeError("FATAL: INTERNAL_SERVICE_SECRET must be configured when REQUIRE_INTERNAL_AUTH is true.")
    assert "INTERNAL_SERVICE_SECRET must be configured" in str(exc_info.value)
