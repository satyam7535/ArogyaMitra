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


def test_doctor_review_page_initialization():
    """Verify that the Doctor Review page loads the triage queue and review form."""
    doctor_file = os.path.join(ui_dir, "pages", "2_Doctor_Review.py")
    at = AppTest.from_file(doctor_file, default_timeout=15.0).run()
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
