"""
Phase 6 Automated Test Suite: Streamlit Multi-Page Application Testing
Uses streamlit.testing.v1.AppTest to execute headless UI tests across all portal pages.
"""

import os
import sys

# Ensure ui and project root are in sys.path
ui_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ui_dir)

from streamlit.testing.v1 import AppTest


def test_home_page_initialization():
    """Verify that the Home landing page mounts cleanly without exceptions."""
    home_file = os.path.join(ui_dir, "Home.py")
    at = AppTest.from_file(home_file, default_timeout=15.0).run()
    assert not at.exception
    assert len(at.title) >= 1
    assert "ArogyaMitra" in at.title[0].value
    # Verify clinical decision support disclaimer warning is present
    assert len(at.warning) >= 1
    assert "Clinical Decision Support Disclaimer" in at.warning[0].value


def test_worker_triage_page_initialization():
    """Verify that the Worker Triage page loads with symptom selector and demographics."""
    triage_file = os.path.join(ui_dir, "pages", "1_Worker_Triage.py")
    at = AppTest.from_file(triage_file, default_timeout=15.0).run()
    assert not at.exception
    assert len(at.title) >= 1
    assert "Worker Triage" in at.title[0].value
    # Verify multiselect is present for symptoms
    assert len(at.multiselect) >= 1


def test_doctor_review_page_initialization(monkeypatch):
    """Verify that the Doctor Review page loads the triage queue and review form."""
    import utils.api_client as ac
    monkeypatch.setattr(ac, "get_pending_consultations_for_doctor", lambda token: [{
        "_id": "660000000000000000000001",
        "patient": {"name": "Test Case", "age": 45, "gender": "Female"},
        "mlAnalysis": {"disease": "Malaria", "confidence": 0.92, "severityScore": 3.0, "needsEscalation": True},
        "symptoms": ["chills", "high_fever"],
        "status": "escalated",
        "notes": "Spiking fever",
    }])
    doctor_file = os.path.join(ui_dir, "pages", "2_Doctor_Review.py")
    at = AppTest.from_file(doctor_file, default_timeout=15.0)
    at.session_state["token"] = "mock_doctor_token"
    at.session_state["role"] = "Doctor"
    at.run()
    assert not at.exception
    assert len(at.title) >= 1
    assert "Medical Officer" in at.title[0].value or "Doctor" in at.title[0].value
    # Verify physician input fields are present
    assert len(at.text_input) >= 1
    assert len(at.text_area) >= 1


def test_admin_dashboard_page_initialization():
    """Verify that the Admin Dashboard loads KPIs, telemetry, and audit trail."""
    admin_file = os.path.join(ui_dir, "pages", "3_Admin_Dashboard.py")
    at = AppTest.from_file(admin_file, default_timeout=15.0).run()
    assert not at.exception
    assert len(at.title) >= 1
    assert "Admin" in at.title[0].value or "Governance" in at.title[0].value
    # Verify metrics tiles are rendered
    assert len(at.metric) >= 4
    # Verify data table is present
    assert len(at.dataframe) >= 1


def test_i18n_localization_integrity():
    """Verify localization module returns valid text in en, hi, mr without missing keys."""
    from utils.i18n import MESSAGES, t
    for lang in ["en", "hi", "mr"]:
        assert len(MESSAGES[lang]) > 20
        assert t("app_title", lang) in ("ArogyaMitra", "आरोग्यमित्र")
        assert len(t("disclaimer_text", lang)) > 30


def test_viz_module_robustness():
    """Verify Plotly figure generation handles edge cases and empty lists gracefully."""
    from utils.viz import (
        create_admin_epidemiology_chart,
        create_shap_waterfall_or_bar,
        create_top_predictions_chart,
    )

    # Empty inputs
    f1 = create_shap_waterfall_or_bar([], "Fungal infection")
    assert f1 is not None

    f2 = create_top_predictions_chart([])
    assert f2 is not None

    f3 = create_admin_epidemiology_chart({})
    assert f3 is not None

    # Normal inputs
    sample_shap = [{"symptom": "itching", "impact": 0.42, "direction": "Supports Diagnosis"}]
    f4 = create_shap_waterfall_or_bar(sample_shap, "Fungal infection")
    assert len(f4.data) >= 1


def test_api_client_thin_client_auth_helpers():
    """Verify that API client thin client methods enforce proper role constraints."""
    from utils.api_client import get_auth_headers, login_user

    # Test invalid role rejection
    res = login_user("fake@test.com", "pass", "SuperAdmin")
    assert res["success"] is False
    assert "Invalid role" in res["error"]

    # Test header generation
    h_none = get_auth_headers(None)
    assert "Authorization" not in h_none
    assert h_none["Content-Type"] == "application/json"

    h_token = get_auth_headers("mock_jwt_token_123")
    assert h_token["Authorization"] == "Bearer mock_jwt_token_123"


def test_api_client_no_service_secret_or_bypass():
    """Verify that api_client.py strictly avoids service secret imports or bypasses."""
    import utils.api_client as ac
    assert not hasattr(ac, "INTERNAL_SERVICE_SECRET"), "Direct service secret bypass must be eliminated from UI"


def test_triage_analysis_with_bayesian_evidence_and_red_flags():
    """Verify run_triage_analysis returns exact Bayesian attributions and red-flag escalation."""
    from utils.api_client import run_triage_analysis

    # 1. Normal case
    res1 = run_triage_analysis(
        ["itching", "skin_rash", "nodal_skin_eruptions"],
        {"name": "Patient A", "age": 28, "gender": "Female"}
    )
    assert "mlResult" in res1
    assert "shapExplanation" in res1["mlResult"]
    assert res1["mlResult"]["disease"] is not None

    # 2. Red-flag cardiac case
    res2 = run_triage_analysis(
        ["chest_pain", "breathlessness", "sweating"],
        {"name": "Patient B", "age": 55, "gender": "Male"}
    )
    assert res2["mlResult"]["redFlag"] is True
    assert res2["mlResult"]["needsEscalation"] is True
    assert res2["mlResult"]["risk"] == "High"


def test_ui_401_expired_session_handling(monkeypatch):
    """Verify that a 401 response results in sessionExpired and not 'AI Prediction Service Unavailable'."""
    import httpx
    from utils.api_client import run_triage_analysis

    class Mock401Response:
        status_code = 401
        text = '{"message": "Access token has expired"}'

        def json(self):
            return {"message": "Access token has expired"}

    monkeypatch.setattr(httpx, "post", lambda *args, **kwargs: Mock401Response())

    res = run_triage_analysis(
        ["itching"],
        {"name": "Expired Test", "age": 40, "gender": "Female"},
        token="expired_token_xyz"
    )
    assert res.get("success") is False
    assert res.get("sessionExpired") is True
    assert res.get("modelUnavailable") is False
    assert "Your session expired" in res.get("error", "")
    assert "AI Prediction Service Unavailable" not in res.get("error", "")



def test_worker_triage_stale_state_reset():
    """Verify item 6: preset buttons and analysis run reset previous accept/escalate messages and results."""
    triage_file = os.path.join(ui_dir, "pages", "1_Worker_Triage.py")
    at = AppTest.from_file(triage_file, default_timeout=15.0)
    at.session_state["accept_msg"] = "Stale accept message"
    at.session_state["escalate_msg"] = "Stale escalate message"
    at.session_state["triage_results"] = {"mlResult": {"disease": "Jaundice", "confidence": 0.95}}
    at.run()
    jaundice_btn = next(b for b in at.button if "Jaundice" in b.label)
    jaundice_btn.click().run()
    assert "accept_msg" not in at.session_state
    assert "escalate_msg" not in at.session_state
    assert "triage_results" not in at.session_state


def test_worker_triage_red_flag_rationale_no_none():
    """Verify item 7: red flag alert renders clinical rationale and never outputs '(None)'."""
    triage_file = os.path.join(ui_dir, "pages", "1_Worker_Triage.py")
    at = AppTest.from_file(triage_file, default_timeout=15.0)
    at.session_state["triage_results"] = {
        "success": True,
        "mlResult": {
            "disease": "Heart Attack",
            "confidence": 0.995,
            "redFlag": True,
            "redFlagDetails": [{"symptom": "chest_pain", "category": None}],
            "needsEscalation": True,
            "matchedSymptoms": ["chest_pain"],
            "severityScore": 6.8,
        },
        "llmResult": {},
    }
    at.run()
    assert not at.exception
    rf_errors = [e.value for e in at.error if "CRITICAL RED-FLAG ALERT" in e.value]
    assert len(rf_errors) == 1
    err_text = rf_errors[0]
    assert "(None)" not in err_text
    assert "Chest Pain" in err_text
    assert "cardiac emergency" in err_text.lower() or "acute coronary" in err_text.lower()


def test_worker_triage_http_409_friendly_message():
    """Verify item 8: HTTP 409 red-flag rejection shows plain English clinical emergency message."""
    triage_file = os.path.join(ui_dir, "pages", "1_Worker_Triage.py")
    at = AppTest.from_file(triage_file, default_timeout=15.0)
    at.session_state["triage_results"] = {
        "success": True,
        "mlResult": {
            "disease": "Fungal infection",
            "confidence": 0.95,
            "redFlag": False,
            "needsEscalation": False,
            "matchedSymptoms": ["itching"],
            "severityScore": 1.2,
        },
    }
    import utils.api_client as ac
    original_submit = ac.submit_consultation
    try:
        ac.submit_consultation = lambda *args, **kwargs: {
            "success": False,
            "statusCode": 409,
            "error": "HTTP 409 Conflict: Cannot accept red-flag consultation without Medical Officer review."
        }
        at.run()
        accept_btn = next(b for b in at.button if "Accept" in b.label or "स्वीकारा" in b.label or "स्वीकार" in b.label)
        accept_btn.click().run()
        error_msgs = [e.value for e in at.error]
        assert any("Emergency: cannot accept without a doctor." in msg for msg in error_msgs)
        assert not any("HTTP 409" in msg for msg in error_msgs)
    finally:
        ac.submit_consultation = original_submit


def test_worker_triage_honest_confidence_label():
    """Verify item 9: confidence >= 0.99 displays 'Very high (uncalibrated estimate)'."""
    triage_file = os.path.join(ui_dir, "pages", "1_Worker_Triage.py")
    at = AppTest.from_file(triage_file, default_timeout=15.0)
    at.session_state["triage_results"] = {
        "success": True,
        "mlResult": {
            "disease": "Malaria",
            "confidence": 0.998,
            "redFlag": False,
            "needsEscalation": False,
            "matchedSymptoms": ["chills", "high_fever"],
            "severityScore": 3.0,
        },
    }
    at.run()
    assert not at.exception
    conf_metrics = [m for m in at.metric if "confidence" in m.label.lower() or "विश्वास" in m.label or "अंदाज" in m.label]
    assert len(conf_metrics) == 1
    assert conf_metrics[0].value == "Very high (uncalibrated estimate)"
