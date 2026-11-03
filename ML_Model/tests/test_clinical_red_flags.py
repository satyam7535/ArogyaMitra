"""
ArogyaMitra — Clinical Red-Flag Rule Layer Tests (Decision A)
"""

import os
import sys

import pytest
import yaml

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
ML_DIR = os.path.dirname(TESTS_DIR)
REPO_ROOT = os.path.dirname(ML_DIR)

for p in [REPO_ROOT, ML_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from ML_Model.app import PredictRequest, load_red_flags, run_prediction


def test_red_flag_forces_escalation_and_high_risk():
    """Verifies that chest_pain triggers redFlag=True, needsEscalation=True, risk='High'."""
    req = PredictRequest(symptoms=["chest_pain", "mild_fever"])
    res = run_prediction(req)

    assert res["redFlag"] is True, "Expected redFlag to be True for chest_pain"
    assert res["needsEscalation"] is True, "Expected needsEscalation to be True for red flag presentation"
    assert res["risk"] == "High", f"Expected risk to be 'High', got {res['risk']}"
    assert len(res["redFlagDetails"]) > 0
    assert any(rf["symptom"] == "chest_pain" for rf in res["redFlagDetails"])
    assert res["clinicalReviewNotice"] is not None
    assert "PENDING CLINICAL REVIEW" in res["clinicalReviewNotice"].upper()
    assert "CLINICAL RED FLAG" in res["uncertaintyReason"]


def test_non_red_flag_routine_presentation():
    """Verifies that low-acuity routine symptoms (itching, skin_rash) do NOT trigger redFlag."""
    req = PredictRequest(symptoms=["itching", "skin_rash", "nodal_skin_eruptions"])
    res = run_prediction(req)

    assert res["redFlag"] is False, "Expected redFlag to be False for low-acuity presentation"
    assert res["risk"] in ["Low", "Moderate"]
    assert len(res["redFlagDetails"]) == 0
    assert res["clinicalReviewNotice"] is None


def test_red_flags_startup_validation_rejects_unmapped_vocabulary(tmp_path, monkeypatch):
    """Verifies startup fail-closed validation when red_flags.yaml references unmapped vocabulary."""
    invalid_config = {
        "status": "DRAFT",
        "reviewed_by": None,
        "vocabulary_red_flags": [
            {
                "symptom": "fictional_unmapped_symptom_not_in_131_columns",
                "acuity_level": "Critical",
                "clinical_rationale": "Invalid test symptom"
            }
        ]
    }
    fake_config_path = tmp_path / "red_flags.yaml"
    with open(fake_config_path, "w", encoding="utf-8") as f:
        yaml.dump(invalid_config, f)

    def fake_join(*args):
        if args[-1] == "red_flags.yaml":
            return str(fake_config_path)
        return os.path.join(*args)

    monkeypatch.setattr(os.path, "join", fake_join)

    with pytest.raises(ValueError, match="is not in clinical vocabulary"):
        load_red_flags()

    # Restore valid configuration
    monkeypatch.undo()
    load_red_flags()


def test_red_flags_startup_validation_rejects_non_draft_status(tmp_path, monkeypatch):
    """Verifies startup fail-closed validation if status is not DRAFT when unreviewed."""
    invalid_config = {
        "status": "PRODUCTION_APPROVED",
        "reviewed_by": None,
        "vocabulary_red_flags": []
    }
    fake_config_path = tmp_path / "red_flags.yaml"
    with open(fake_config_path, "w", encoding="utf-8") as f:
        yaml.dump(invalid_config, f)

    def fake_join(*args):
        if args[-1] == "red_flags.yaml":
            return str(fake_config_path)
        return os.path.join(*args)

    monkeypatch.setattr(os.path, "join", fake_join)

    with pytest.raises(ValueError, match="Expected red_flags status 'DRAFT'"):
        load_red_flags()

    # Restore valid configuration
    monkeypatch.undo()
    load_red_flags()
