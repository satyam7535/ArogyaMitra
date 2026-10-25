"""
ArogyaMitra — AI-Assisted Primary Healthcare Decision Support System
Main Portal Hub & Welcome Interface
"""

import streamlit as st
import os
import sys

# Ensure ui and project root are in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.i18n import t
from utils.api_client import check_services_health

st.set_page_config(
    page_title="ArogyaMitra | Healthcare Decision Support",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize Session State
if "lang" not in st.session_state:
    st.session_state["lang"] = "en"

# Sidebar: Language & System Health
with st.sidebar:
    st.image("https://img.icons8.com/color/96/caduceus.png", width=64)
    st.markdown("### **ArogyaMitra**")
    st.caption("AI-Assisted Rural Healthcare CDSS")
    st.divider()

    selected_lang = st.selectbox(
        "🌐 " + t("language_select", st.session_state["lang"]),
        options=["English", "हिंदी (Hindi)", "मराठी (Marathi)"],
        index=0 if st.session_state["lang"] == "en" else (1 if st.session_state["lang"] == "hi" else 2),
    )
    lang_code = "en" if "English" in selected_lang else ("hi" if "Hindi" in selected_lang else "mr")
    st.session_state["lang"] = lang_code

    st.divider()
    st.markdown(f"#### 📡 {t('service_status', lang_code)}")
    health = check_services_health()

    ml_color = "🟢" if health["ml"] else "🟡"
    graph_color = "🟢" if health["graph"] else "🟡"
    backend_color = "🟢" if health["backend"] else "🟡"

    st.markdown(f"- **ML Engine:** {ml_color} {'Operational' if health['ml'] else 'In-Process Fallback'}")
    st.markdown(f"- **AI Pipeline:** {graph_color} {'Operational' if health['graph'] else 'In-Process Fallback'}")
    st.markdown(f"- **Backend API:** {backend_color} {'Operational' if health['backend'] else 'Standalone Mode'}")

    st.divider()
    st.caption("ArogyaMitra v1.0.0 | DPDP Act (2023) Compliant")

# Hero Banner
lang = st.session_state["lang"]
st.title(f"🏥 {t('app_title', lang)}")
st.subheader(t("app_tagline", lang))

# Clinical Decision Support Disclaimer (Mandatory Regulatory Alert)
st.warning(f"⚠️ **{t('disclaimer_title', lang)}:** {t('disclaimer_text', lang)}")

st.divider()

# Quick Navigation Portals
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 👩‍⚕️ Community Health Worker")
    st.markdown(
        "Triage patients at village sub-centers or home visits. "
        "Select presenting symptoms from 131 clinical categories, run calibrated AI predictions, "
        "inspect TreeSHAP feature attributions, and escalate high-risk cases to physicians."
    )
    if st.button("🚀 Launch Worker Triage", type="primary", use_container_width=True):
        st.switch_page("pages/1_Worker_Triage.py")

with col2:
    st.markdown("### 🩺 Medical Officer Review")
    st.markdown(
        "Remote physician review workstation. Review escalated cases, "
        "evaluate calibrated differential diagnoses alongside TreeSHAP feature attributions, "
        "issue binding clinical second opinions, and prescribe treatments."
    )
    if st.button("📋 Open Doctor Workstation", use_container_width=True):
        st.switch_page("pages/2_Doctor_Review.py")

with col3:
    st.markdown("### 📊 Health Center Admin")
    st.markdown(
        "Governance and real-time observability dashboard. "
        "Monitor epidemiological disease prevalence, track doctor turnaround times, "
        "view asynchronous analysis job queue health, and inspect immutable security audit logs."
    )
    if st.button("⚙️ Open Admin Dashboard", use_container_width=True):
        st.switch_page("pages/3_Admin_Dashboard.py")

st.divider()

# Technical Highlights Section
st.markdown("### 🛡️ Core Clinical & Architectural Pillars")

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown("#### 🔬 Calibrated ML")
    st.markdown("LightGBM ensemble calibrated via sigmoid regression on 304 deduplicated clinical ground-truth rows.")

with c2:
    st.markdown("#### 🔍 TreeSHAP XAI")
    st.markdown("True marginal feature contributions explaining exactly why a diagnosis was recommended.")

with c3:
    st.markdown("#### 🔒 Zero-Trust Security")
    st.markdown("Argon2id hashing, AES-256-GCM patient encryption, and DPDP Act 2023 compliance.")

with c4:
    st.markdown("#### 🌐 Multilingual Edge")
    st.markdown("Full vernacular clinical report generation and UI localization in English, Hindi, and Marathi.")
