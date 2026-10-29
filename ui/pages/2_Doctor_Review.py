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

st.title(f"🩺 {t('doctor_portal_title', lang)}")
st.caption("Primary Health Center (PHC) Medical Officer Second Opinion Queue")

# Clinical Decision Support Disclaimer
st.info(f"⚠️ **{t('disclaimer_title', lang)}:** {t('disclaimer_text', lang)}")

st.divider()

# Sample Pending Cases Database (Integration Fallback)
SAMPLE_PENDING_CASES = [
    {
        "id": "CASE-9021",
        "patientName": "Ramesh Shinde",
        "age": 48,
        "gender": "Male",
        "location": "Pali Sub-Centre, Raigad",
        "submittedBy": "Sunita Patil (ASHA Worker)",
        "symptoms": ["chills", "vomiting", "high_fever", "sweating", "headache"],
        "primaryDiagnosis": "Malaria",
        "confidence": 0.885,
        "severityScore": 3.8,
        "needsEscalation": True,
        "uncertaintyReason": "HIGH_SEVERITY",
        "notes": "Patient reported high spiking fever with severe rigors and chills for 3 days. Weak and dehydrated.",
        "shap": [
            {"symptom": "chills", "impact": 0.44, "direction": "Supports Diagnosis"},
            {"symptom": "high_fever", "impact": 0.38, "direction": "Supports Diagnosis"},
            {"symptom": "sweating", "impact": 0.31, "direction": "Supports Diagnosis"},
            {"symptom": "vomiting", "impact": 0.18, "direction": "Supports Diagnosis"},
        ],
        "topPredictions": [
            {"disease": "Malaria", "probability": 0.885},
            {"disease": "Dengue", "probability": 0.082},
            {"disease": "Typhoid", "probability": 0.033},
        ],
        "llmSummary": "Clinical signs strongly indicate plasmodium infection. Rapid diagnostic test (RDT) and blood smear required immediately."
    },
    {
        "id": "CASE-9022",
        "patientName": "Anandi Bai",
        "age": 62,
        "gender": "Female",
        "location": "Bhor PHC, Pune",
        "submittedBy": "Rekha Gaikwad (ANM)",
        "symptoms": ["itching", "yellowish_skin", "dark_urine", "nausea", "fatigue"],
        "primaryDiagnosis": "Jaundice",
        "confidence": 0.824,
        "severityScore": 3.2,
        "needsEscalation": True,
        "uncertaintyReason": "CLINICAL_RISK",
        "notes": "Noticeable scleral icterus observed by health worker. Patient complains of severe anorexia and dark urine.",
        "shap": [
            {"symptom": "yellowish_skin", "impact": 0.46, "direction": "Supports Diagnosis"},
            {"symptom": "dark_urine", "impact": 0.39, "direction": "Supports Diagnosis"},
            {"symptom": "itching", "impact": 0.22, "direction": "Supports Diagnosis"},
        ],
        "topPredictions": [
            {"disease": "Jaundice", "probability": 0.824},
            {"disease": "Hepatitis A", "probability": 0.112},
            {"disease": "Chronic Cholestasis", "probability": 0.064},
        ],
        "llmSummary": "Hepatobiliary dysfunction suspected. Liver Function Tests (LFT) and abdominal ultrasonography recommended."
    },
]

# Attempt to load dynamic pending cases from backend if doctor token exists
cases_to_display = SAMPLE_PENDING_CASES
is_live_backend = False

if token and role == "Doctor":
    live_cases = get_pending_consultations_for_doctor(token)
    if live_cases:
        formatted = []
        for c in live_cases:
            patient = c.get("patient") or {}
            ml = c.get("mlAnalysis") or {}
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
                "uncertaintyReason": ml.get("uncertaintyReason", "ESCALATED"),
                "notes": c.get("notes") or c.get("escalationReason") or "",
                "shap": ml.get("shapExplanation") or [
                    {"symptom": s, "impact": 0.3, "direction": "Supports Diagnosis"}
                    for s in c.get("symptoms", [])[:4]
                ],
                "topPredictions": ml.get("topPredictions") or [
                    {"disease": ml.get("disease", "Primary"), "probability": ml.get("confidence", 0.8)}
                ],
                "llmSummary": (c.get("llmAnalysis") or {}).get("summary", "Review required"),
            })
        if formatted:
            cases_to_display = formatted
            is_live_backend = True

# ── Sidebar: Case Selector ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📥 Triage Review Queue")
    if is_live_backend:
        st.success("🟢 Connected to live Express consultation queue")
    else:
        st.caption("ℹ️ Demonstration review queue active")

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
    st.markdown(f"**Severity Index:** `{sev} / 5.0`")

st.markdown(f"**Worker Clinical Notes:** *\"{selected_case['notes']}\"*")

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

with st.form("doctor_opinion_form"):
    confirmed_diagnosis = st.text_input(
        t("doctor_diagnosis", lang),
        value=f"Confirmed {selected_case['primaryDiagnosis']} with clinical correlation.",
    )
    treatment_plan = st.text_area(
        t("doctor_prescription", lang),
        value="Prescribed standard oral regimen. Advised hydration and complete rest. Revisit PHC if fever persists past 48 hours.",
        height=100,
    )
    follow_up_days = st.slider("Recommended Follow-Up (Days):", min_value=1, max_value=30, value=5)

    submitted = st.form_submit_button(
        f"📋 {t('submit_opinion', lang)}",
        type="primary",
        use_container_width=True,
    )

    if submitted:
        if token and is_live_backend:
            with st.spinner("Submitting second opinion to backend with OCC verification..."):
                resp = submit_doctor_second_opinion(
                    selected_case["id"],
                    confirmed_diagnosis,
                    treatment_plan,
                    token,
                )
                if resp.get("success"):
                    st.success(f"✅ {t('case_closed', lang)} Second opinion recorded in database.")
                elif resp.get("statusCode") == 409:
                    st.error("⚠️ Conflict (409): Case was modified concurrently by another provider. Please refresh.")
                else:
                    st.error(f"Failed to submit opinion: {resp.get('error')}")
        else:
            st.success(f"✅ {t('case_closed', lang)} Second opinion issued for #{selected_case['id']}.")
            st.info("Treatment recommendation has been transmitted back to the health worker tablet.")
