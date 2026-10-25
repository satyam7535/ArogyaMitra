"""
ArogyaMitra — Medical Officer Second Opinion Workstation
Enables licensed physicians to review escalated rural cases, evaluate TreeSHAP feature
attributions, issue binding diagnoses, prescribe treatments, and resolve triage workflows.
"""

import streamlit as st
import os
import sys

# Ensure ui and project root are in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.i18n import t
from utils.viz import create_shap_waterfall_or_bar, create_top_predictions_chart

st.set_page_config(
    page_title="Doctor Review | ArogyaMitra",
    page_icon="🩺",
    layout="wide",
)

lang = st.session_state.get("lang", "en")

st.title(f"🩺 {t('doctor_portal_title', lang)}")
st.caption("Primary Health Center (PHC) Medical Officer Second Opinion Queue")

# Clinical Decision Support Disclaimer
st.info(f"⚠️ **{t('disclaimer_title', lang)}:** {t('disclaimer_text', lang)}")

st.divider()

# Sample Pending Cases Database (Mock / Integration Queue)
PENDING_CASES = [
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

# ── Sidebar: Case Selector ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📥 Triage Review Queue")
    case_options = [f"{c['id']} — {c['patientName']} ({c['primaryDiagnosis']})" for c in PENDING_CASES]
    selected_idx = st.selectbox("Select Case to Review:", range(len(case_options)), format_func=lambda i: case_options[i])
    st.caption(f"Total Pending Reviews: **{len(PENDING_CASES)} cases**")

selected_case = PENDING_CASES[selected_idx]

# ── Patient Case Header ──────────────────────────────────────────────────────
st.markdown(f"### 📋 {selected_case['id']} — {selected_case['patientName']}")

h1, h2, h3, h4 = st.columns(4)
with h1:
    st.markdown(f"**Age / Gender:** {selected_case['age']} / {selected_case['gender']}")
with h2:
    st.markdown(f"**Origin:** {selected_case['location']}")
with h3:
    st.markdown(f"**Submitted By:** {selected_case['submittedBy']}")
with h4:
    st.error(f"🚨 Escalation: `{selected_case['uncertaintyReason']}`")

st.markdown(f"**Health Worker Notes:** *\"{selected_case['notes']}\"*")
st.markdown(f"**Reported Symptoms:** " + ", ".join(f"`{s.replace('_', ' ').title()}`" for s in selected_case['symptoms']))

st.divider()

# ── AI Diagnostic Evaluation & TreeSHAP ──────────────────────────────────────
c1, c2 = st.columns([3, 2])

with c1:
    st.markdown("#### 🔬 AI Model Clinical Suggestion")
    st.markdown(f"- **Predicted Condition:** **{selected_case['primaryDiagnosis']}**")
    st.markdown(f"- **Calibrated Confidence:** **{round(selected_case['confidence']*100, 1)}%**")
    st.markdown(f"- **Severity Index:** **{selected_case['severityScore']} / 5.0**")
    st.markdown(f"- **AI Clinical Impression:** {selected_case['llmSummary']}")

    shap_fig = create_shap_waterfall_or_bar(selected_case['shap'], selected_case['primaryDiagnosis'])
    st.plotly_chart(shap_fig, use_container_width=True)

with c2:
    st.markdown("#### 📈 Differential Probability Distribution")
    diff_fig = create_top_predictions_chart(selected_case['topPredictions'])
    st.plotly_chart(diff_fig, use_container_width=True)

st.divider()

# ── Physician Review & Second Opinion Form ────────────────────────────────────
st.markdown("### ✍️ Physician Clinical Verdict & Prescription Order")

doc_col1, doc_col2 = st.columns(2)
with doc_col1:
    doctor_diag = st.text_input(
        t("doctor_diagnosis", lang),
        value=selected_case['primaryDiagnosis'],
        help="Confirm or modify the primary diagnosis based on clinical review."
    )
    urgency = st.selectbox(
        "Triage Urgency Level",
        options=["Routine Outpatient", "Urgent PHC Follow-up (within 24h)", "Immediate Hospital Transfer"],
        index=1 if selected_case['severityScore'] >= 3.5 else 0
    )

with doc_col2:
    prescription = st.text_area(
        t("prescription_notes", lang),
        value=(
            "1. Tab Paracetamol 650mg TDS x 3 days\n"
            "2. Tab Chloroquine / ACT combination as per NVBDCP guidelines\n"
            "3. Complete Blood Count (CBC) + Peripheral Smear for Malarial Parasite\n"
            "4. Ensure strict oral fluid intake (minimum 2.5L/day)"
        ),
        height=130
    )

st.markdown("---")

# Decision Action Buttons
btn_col1, btn_col2, btn_col3 = st.columns(3)
with btn_col1:
    if st.button("✅ Confirm AI Diagnosis & Issue Prescription", type="primary", use_container_width=True):
        st.success(f"Case {selected_case['id']} reviewed. Second opinion officially issued and logged to audit trail.")

with btn_col2:
    if st.button("🔄 Override Diagnosis with Clinical Notes", use_container_width=True):
        st.warning(f"AI diagnosis overridden by physician: '{doctor_diag}'. Prescription transmitted to health worker.")

with btn_col3:
    if st.button("🧪 Order Urgent Laboratory Investigation", use_container_width=True):
        st.info("Laboratory orders dispatched to nearest Community Health Center (CHC).")
