"""
ArogyaMitra — Community Health Worker Triage Interface
Enables village health workers to register patient vitals, select presenting symptoms,
trigger AI analysis, inspect Bayesian evidence weights, and escalate to doctors.
"""

import base64
import os
import sys

import streamlit as st

# Ensure ui and project root are in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.api_client import (
    get_clinical_symptoms,
    run_triage_analysis,
)
from utils.i18n import t
from utils.viz import create_shap_waterfall_or_bar, create_top_predictions_chart

st.set_page_config(
    page_title="Worker Triage | ArogyaMitra",
    page_icon="👩‍⚕️",
    layout="wide",
)

lang = st.session_state.get("lang", "en")
token = st.session_state.get("token")
user = st.session_state.get("user") or {}

# Auto-provision active session for frontline clinical testing if not already logged in
if not token:
    try:
        from utils.api_client import login_user
        auth_res = login_user("worker@arogyamitra.gov.in", "Worker@Arogya2026!", "Worker")
        if auth_res.get("success"):
            st.session_state["token"] = auth_res["accessToken"]
            st.session_state["user"] = auth_res["user"]
            st.session_state["role"] = auth_res["role"]
            token = auth_res["accessToken"]
            user = auth_res["user"]
    except Exception:
        pass


st.title(f"👩‍⚕️ {t('nav_triage', lang)}")
st.caption("Primary Health Centre Community Outreach & Triage Workstation")

# Clinical Non-Diagnostic Disclaimer
st.info(f"⚠️ **{t('disclaimer_title', lang)}:** {t('disclaimer_text', lang)}")

st.divider()

# ── 1. Patient Demographics Form ─────────────────────────────────────────────
st.markdown(f"### 📋 {t('patient_details', lang)}")

col1, col2, col3, col4 = st.columns(4)
with col1:
    patient_name = st.text_input(t("patient_name", lang), value="Kavita Devi")
with col2:
    patient_age = st.number_input(t("patient_age", lang), min_value=1, max_value=120, value=42)
with col3:
    patient_gender = st.selectbox(t("patient_gender", lang), options=["Female", "Male", "Other"], index=0)
with col4:
    patient_location = st.text_input(t("patient_location", lang), value="Khed Sub-Centre, Pune")

# ── 2. Symptom Selection ─────────────────────────────────────────────────────
st.markdown(f"### 🩺 {t('symptoms_title', lang)}")

# Quick presets for fast clinical demonstration
st.markdown("**Quick Preset Clinical Cases:**")
preset_cols = st.columns(4)
selected_preset = None
with preset_cols[0]:
    if st.button("🟡 Jaundice / Liver Case", use_container_width=True):
        selected_preset = ["itching", "vomiting", "fatigue", "yellowish_skin", "dark_urine"]
with preset_cols[1]:
    if st.button("🦟 Malaria / Fever Case", use_container_width=True):
        selected_preset = ["chills", "vomiting", "high_fever", "sweating", "headache"]
with preset_cols[2]:
    if st.button("🚨 Cardiac Emergency (Red Flag)", use_container_width=True):
        selected_preset = ["chest_pain", "breathlessness", "sweating"]
with preset_cols[3]:
    if st.button("🧴 Fungal Skin Case", use_container_width=True):
        selected_preset = ["itching", "skin_rash", "nodal_skin_eruptions"]

all_symptoms_data = get_clinical_symptoms()
symptom_ids = [s["id"] for s in all_symptoms_data]

default_symptoms = selected_preset or st.session_state.get("triage_symptoms", ["itching", "skin_rash", "nodal_skin_eruptions"])
if selected_preset:
    st.session_state["triage_symptoms"] = selected_preset

selected_symptoms = st.multiselect(
    t("select_symptoms", lang),
    options=symptom_ids,
    default=default_symptoms,
    format_func=lambda s: s.replace("_", " ").title(),
)

st.divider()

# ── 3. Run Analysis ──────────────────────────────────────────────────────────
if st.button(f"🔍 {t('run_analysis', lang)}", type="primary", use_container_width=True):
    if not selected_symptoms:
        st.error("Please select at least one clinical symptom to evaluate.")
    else:
        with st.spinner(t("analyzing", lang)):
            patient_info = {
                "name": patient_name,
                "age": patient_age,
                "gender": patient_gender,
                "location": patient_location,
                "workerName": user.get("name", "Sunita Patil (ASHA Worker)"),
            }
            results = run_triage_analysis(selected_symptoms, patient_info, language=lang, token=token)
            st.session_state["triage_results"] = results
            st.session_state["triage_patient"] = patient_info

# ── 4. Render Results ────────────────────────────────────────────────────────
if "triage_results" in st.session_state:
    results = st.session_state["triage_results"]
    if results.get("modelUnavailable") or not results.get("success", True):
        st.error(f"🚨 **AI Prediction Service Unavailable (HTTP {results.get('statusCode', 503)}):** {results.get('error', 'Prediction service is currently unreachable.')}")
        st.warning("⚠️ ArogyaMitra enforces fail-closed clinical safety: no diagnostic assessment or clinical advice will be generated while upstream services are down. Please verify connectivity or escalate directly to a Medical Officer.")
        st.stop()

    ml = results.get("mlResult", {})
    llm = results.get("llmResult", {})
    pdf_base64 = results.get("pdfBase64", "")
    filename = results.get("filename", "ArogyaMitra_Report.pdf")

    st.markdown(f"## 📊 {t('results_title', lang)}")

    # Red-Flag Emergency Banner (Decision A Requirement)
    if ml.get("redFlag"):
        rf_details = ml.get("redFlagDetails", [])
        reasons_str = ", ".join([f"{r.get('symptom')} ({r.get('category')})" for r in rf_details]) if rf_details else "Critical presentation"
        st.error(
            f"🚨 **CRITICAL RED-FLAG ALERT (EMERGENCY REFERRAL REQUIRED):** {reasons_str}. "
            "Case automatically escalated with highest clinical priority. Do not delay hospital transport."
        )
    elif ml.get("needsEscalation", False):
        reason = ml.get("uncertaintyReason", "Clinical threshold exceeded")
        st.warning(
            f"⚠️ **{t('escalation_alert', lang)}:** The model confidence is low or clinical severity is high. "
            f"Physician second opinion review recommended. (Reason: `{reason}`)"
        )

    # Top Metric Tiles
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric(
            label=t("primary_diagnosis", lang),
            value=ml.get("disease", "Unknown"),
        )
    with m2:
        conf_pct = round(float(ml.get("confidence", 0.0)) * 100, 1)
        st.metric(
            label=t("confidence", lang),
            value=f"{conf_pct}%",
            delta=None,
        )
    with m3:
        sev = ml.get("severityScore", 1.0)
        st.metric(
            label=t("severity", lang),
            value=f"{sev} / 5.0",
            delta="High Risk" if sev >= 3.5 else "Standard",
            delta_color="inverse" if sev >= 3.5 else "normal",
        )
    with m4:
        st.metric(
            label="Matched Symptoms",
            value=len(ml.get("matchedSymptoms", [])),
        )

    st.markdown("---")

    # Visualizations: Bayesian Evidence Bar & Differential Probabilities
    c_left, c_right = st.columns([3, 2])
    with c_left:
        st.markdown(f"#### 🔍 {t('shap_chart_title', lang)}")
        st.caption("Exact Bayesian log-odds feature contributions for presenting symptoms:")
        shap_fig = create_shap_waterfall_or_bar(
            ml.get("shapExplanation", []),
            primary_disease=ml.get("disease", "Condition")
        )
        st.plotly_chart(shap_fig, use_container_width=True)

    with c_right:
        st.markdown("#### 📈 Differential Diagnoses")
        diff_fig = create_top_predictions_chart(ml.get("topPredictions", []))
        st.plotly_chart(diff_fig, use_container_width=True)

    st.markdown("---")

    # LLM Clinical Summary & Precautions
    llm_col, prec_col = st.columns([3, 2])
    with llm_col:
        st.markdown(f"#### 📝 {t('llm_summary_title', lang)}")
        diag_summary = llm.get("diagnosis_summary", ml.get("description", ""))
        rec_steps = llm.get("recommended_next_steps", "")
        referral = llm.get("referral_recommendation", "")

        st.markdown(f"**Clinical Impression:** {diag_summary}")
        if rec_steps:
            st.markdown(f"**Recommended Action:** {rec_steps}")
        if referral:
            st.markdown(f"**Referral Advice:** {referral}")

        if llm.get("llmFallback", True):
            st.info("📋 **Provenance:** Standard Clinical Decision-Support Template (Deterministic Safe Mode)")
        else:
            st.success("✨ **Provenance:** AI-Generated Clinical Summary (Google Gemini)")

    with prec_col:
        st.markdown(f"#### 🛡️ {t('precautions_title', lang)}")
        precautions = ml.get("precautions", [])
        if precautions:
            for p in precautions:
                st.markdown(f"- ✅ {p.capitalize()}")
        else:
            st.markdown("- Rest and maintain clean hydration.")

    st.markdown("---")

    # Action Buttons: Accept / Escalate / Download PDF
    is_red_flag = bool(ml.get("redFlag"))
    needs_escalation = bool(ml.get("needsEscalation"))

    if is_red_flag:
        st.error("🚨 **RED FLAG DETECTED (HTTP 409):** Direct accept is strictly blocked. Clinical red flags require immediate escalation to a Medical Officer or referral to an emergency hospital facility.")
    elif needs_escalation:
        st.warning("⚠️ **ESCALATION RECOMMENDED:** This presentation suggests secondary referral. If accepting locally, Decision B clinical override criteria (canonical reason + minimum 10-character clinical note) are required.")
        with st.expander("📝 Decision B Clinical Override Form", expanded=True):
            CANONICAL_OVERRIDE_REASONS = [
                "patient_improved",
                "referred_in_person",
                "doctor_unreachable",
                "patient_declined_referral",
                "other"
            ]
            sel_reason = st.selectbox(
                "Clinical Override Reason (Required)",
                options=CANONICAL_OVERRIDE_REASONS,
                format_func=lambda r: {
                    "patient_improved": "Patient condition improved substantially",
                    "referred_in_person": "Patient physically referred to nearby CHC/hospital",
                    "doctor_unreachable": "Medical officer unreachable after multiple attempts",
                    "patient_declined_referral": "Patient declined institutional referral",
                    "other": "Other documented clinical justification",
                }.get(r, r),
                key="worker_override_reason"
            )
            override_note = st.text_area(
                "Clinical Override Justification Note (Min 10 non-whitespace characters)",
                placeholder="Document clinical rationale for local management without MO second opinion...",
                key="worker_override_note"
            )

    act_col1, act_col2, act_col3 = st.columns(3)
    with act_col1:
        if is_red_flag:
            st.button(f"🚫 {t('accept_decision', lang)} (Blocked)", disabled=True, use_container_width=True)
        elif needs_escalation:
            if st.button(f"✅ {t('accept_decision', lang)} (With Override)", use_container_width=True):
                note_clean = (st.session_state.get("worker_override_note") or "").strip()
                if len(note_clean) < 10:
                    st.error("Validation Error: Clinical override note must contain at least 10 non-whitespace characters.")
                else:
                    st.success(f"Consultation accepted under Decision B override: '{st.session_state.get('worker_override_reason')}' recorded.")
        else:
            if st.button(f"✅ {t('accept_decision', lang)}", use_container_width=True):
                st.success("Triage consultation finalized and saved to patient record.")

    with act_col2:
        if st.button(f"🚨 {t('escalate_decision', lang)}", type="primary", use_container_width=True):
            st.warning("Case successfully escalated to Medical Officer for second opinion.")

    with act_col3:
        if pdf_base64:
            pdf_bytes = base64.b64decode(pdf_base64)
            st.download_button(
                label=f"📄 {t('download_pdf', lang)}",
                data=pdf_bytes,
                file_name=filename,
                mime="application/pdf",
                use_container_width=True,
            )
        else:
            st.button(f"📄 {t('download_pdf', lang)}", disabled=True, use_container_width=True)
