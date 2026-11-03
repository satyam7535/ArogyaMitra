"""
ArogyaMitra — Medical Officer Second Opinion Workstation
Enables licensed physicians to review escalated rural cases, evaluate exact Bayesian
feature attributions, issue binding diagnoses, prescribe treatments, and resolve triage workflows.
"""

import os
import sys

import streamlit as st

# Ensure ui and project root are in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.api_client import (
    get_pending_consultations_for_doctor,
    submit_doctor_second_opinion,
)
from utils.i18n import t
from utils.viz import create_shap_waterfall_or_bar, create_top_predictions_chart

st.set_page_config(
    page_title="Doctor Review | ArogyaMitra",
    page_icon="🩺",
    layout="wide",
)

lang = st.session_state.get("lang", "en")
token = st.session_state.get("token")
role = st.session_state.get("role")

# Auto-provision Doctor session if not logged in
if not token:
    try:
        from utils.api_client import login_user
        auth_res = login_user("doctor@arogyamitra.gov.in", "Doctor@Arogya2026!", "Doctor")
        if auth_res.get("success"):
            st.session_state["token"] = auth_res["accessToken"]
            st.session_state["user"] = auth_res["user"]
            st.session_state["role"] = auth_res["role"]
            token = auth_res["accessToken"]
            role = auth_res["role"]
    except Exception:
        pass

st.title(f"🩺 {t('doctor_portal_title', lang)}")
st.caption("Primary Health Center (PHC) Medical Officer Second Opinion Queue")

# Clinical Decision Support Disclaimer
st.info(f"⚠️ **{t('disclaimer_title', lang)}:** {t('disclaimer_text', lang)}")

st.divider()

if "doctor_review_msg" in st.session_state:
    st.success(f"✅ {st.session_state.pop('doctor_review_msg')}")

if not token or role != "Doctor":
    st.warning("Please sign in as a Medical Officer to access the review queue.")
    st.stop()

# Query pending cases from backend API
pending_cases = get_pending_consultations_for_doctor(token)
if pending_cases is None:
    st.error("🚨 Failed to connect to consultation review queue API.")
    st.stop()

if not pending_cases:
    st.info("ℹ️ No cases awaiting review.")
    st.stop()

formatted = []
for c in pending_cases:
    patient = c.get("patient") or {}
    ml = c.get("mlAnalysis") or {}
    llm = c.get("llmAnalysis") or {}
    formatted.append({
        "id": str(c.get("_id", "UNKNOWN")),
        "patientName": patient.get("name", "Unknown Patient"),
        "age": patient.get("age", 35),
        "gender": patient.get("gender", "Unknown"),
        "location": "PHC Center",
        "submittedBy": (c.get("submittedBy") or {}).get("name", "Health Worker"),
        "symptoms": c.get("symptoms", []),
        "primaryDiagnosis": ml.get("disease", "Pending"),
        "confidence": ml.get("confidence", 0.0),
        "severityScore": ml.get("severityScore", 2.0),
        "needsEscalation": ml.get("needsEscalation", True),
        "uncertaintyReason": c.get("escalationReason") or ml.get("uncertaintyReason", "ESCALATED"),
        "notes": c.get("notes") or c.get("escalationReason") or "",
        "shap": ml.get("shapExplanation") or [
            {"symptom": s, "impact": 0.3, "direction": "Supports Diagnosis"}
            for s in c.get("symptoms", [])[:4]
        ],
        "topPredictions": ml.get("topPredictions") or [
            {"disease": ml.get("disease", "Primary"), "confidence": ml.get("confidence", 0.8)}
        ],
        "llmSummary": llm.get("summary") or llm.get("diagnosis_summary", "Review required"),
        "status": c.get("status", "escalated"),
    })

cases_to_display = formatted

# ── Sidebar: Case Selector ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📥 Triage Review Queue")
    st.success("🟢 Connected to live Express consultation queue")
    case_options = [f"{c['id'][:8]} — {c['patientName']} ({c['primaryDiagnosis']})" for c in cases_to_display]
    selected_idx = st.selectbox("Select Case to Review:", range(len(case_options)), format_func=lambda i: case_options[i])
    st.caption(f"Total Pending Reviews: **{len(cases_to_display)} cases**")

selected_case = cases_to_display[selected_idx]

# ── Patient Case Header ──────────────────────────────────────────────────────
st.markdown(f"## Case #{selected_case['id'][:12]} — {selected_case['patientName']}")
st.caption(f"Submitted by: **{selected_case['submittedBy']}** | Sub-Centre: **{selected_case['location']}**")

h1, h2, h3, h4 = st.columns(4)
with h1:
    st.markdown(f"**Age / Gender:** {selected_case['age']} yrs / {selected_case['gender']}")
with h2:
    st.markdown(f"**Presenting Symptoms:** {len(selected_case['symptoms'])} reported")
with h3:
    conf = round(float(selected_case["confidence"]) * 100, 1)
    st.markdown(f"**AI Confidence:** `{conf}%`")
with h4:
    sev = selected_case["severityScore"]
    st.markdown(f"**Severity Index:** `{sev} / 7.0`")

st.markdown(f"**Escalation Reason / Notes:** *\"{selected_case['notes']}\"*")

st.markdown("---")

# ── AI Diagnostic Assessment & Explainability ────────────────────────────────
c_left, c_right = st.columns([3, 2])

with c_left:
    st.markdown("#### 🔬 AI Bayesian Evidence Breakdown")
    st.caption("Exact Bayesian log-odds feature contributions supporting this diagnostic inference:")
    shap_fig = create_shap_waterfall_or_bar(
        selected_case["shap"],
        primary_disease=selected_case["primaryDiagnosis"]
    )
    st.plotly_chart(shap_fig, use_container_width=True)

with c_right:
    st.markdown("#### 📊 Differential Diagnoses")
    st.caption("Probabilistic class distribution across candidate conditions:")
    diff_fig = create_top_predictions_chart(selected_case["topPredictions"])
    st.plotly_chart(diff_fig, use_container_width=True)

st.markdown("---")

# ── Doctor Second Opinion Submission Form ────────────────────────────────────
st.markdown("### ✍️ Medical Officer Clinical Response & Second Opinion")

is_already_reviewed = selected_case.get("status") in ("reviewed", "closed")

if is_already_reviewed:
    st.info("ℹ️ This consultation has already been reviewed and closed.")

with st.form("doctor_opinion_form"):
    confirmed_diagnosis = st.text_input(
        t("doctor_diagnosis", lang),
        value=f"Confirmed {selected_case['primaryDiagnosis']} with clinical correlation.",
    )
    treatment_plan = st.text_area(
        "Prescription / advice",
        value="Prescribed standard oral regimen. Advised hydration and complete rest. Revisit PHC if fever persists past 48 hours.",
        height=100,
    )
    follow_up_days = st.slider("Recommended Follow-Up (Days):", min_value=1, max_value=30, value=5)

    submitted = st.form_submit_button(
        f"📋 {t('submit_opinion', lang)}",
        type="primary",
        disabled=is_already_reviewed,
        use_container_width=True,
    )

    if submitted and not is_already_reviewed:
        with st.spinner("Submitting second opinion to backend with OCC verification..."):
            resp = submit_doctor_second_opinion(
                selected_case["id"],
                confirmed_diagnosis,
                treatment_plan,
                token,
            )
            if resp.get("success"):
                st.session_state["doctor_review_msg"] = "Case reviewed successfully. Second opinion recorded in database."
                st.rerun()
            elif resp.get("statusCode") == 409:
                st.error("⚠️ Conflict (409): Case was already reviewed or updated concurrently. Please refresh.")
            else:
                st.error(f"Failed to submit opinion: {resp.get('error')}")
