"""
ArogyaMitra — AI-Assisted Primary Healthcare Decision Support System
Main Portal Hub & Welcome Interface
"""

import os
import sys

import streamlit as st

# Ensure ui and project root are in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.api_client import check_services_health, login_user
from utils.i18n import t

st.set_page_config(
    page_title="ArogyaMitra | Healthcare Decision Support",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize Session State
if "lang" not in st.session_state:
    st.session_state["lang"] = "en"
if "token" not in st.session_state:
    st.session_state["token"] = None
if "user" not in st.session_state:
    st.session_state["user"] = None
if "role" not in st.session_state:
    st.session_state["role"] = None

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
    if st.session_state.get("token"):
        user_info = st.session_state.get("user") or {}
        st.success(f"👤 Logged in as: **{user_info.get('name', 'User')}** ({st.session_state.get('role')})")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state["token"] = None
            st.session_state["user"] = None
            st.session_state["role"] = None
            st.rerun()
    else:
        st.info("🔐 Session: Not logged in (Public view)")

    st.caption("ArogyaMitra v2.0.0 | DPDP Act (2023) Compliant")

# Hero Banner
lang = st.session_state["lang"]
st.title(f"🏥 {t('app_title', lang)}")
st.subheader(t("app_tagline", lang))

# Clinical Decision Support Disclaimer (Mandatory Regulatory Alert)
st.warning(f"⚠️ **{t('disclaimer_title', lang)}:** {t('disclaimer_text', lang)}")

st.divider()

# Authentication Portal Section
with st.expander("🔑 Healthcare Provider Authentication & Sign-In", expanded=not st.session_state.get("token")):
    if st.session_state.get("token"):
        user = st.session_state.get("user") or {}
        st.success(f"✅ Active session: **{user.get('name', 'User')}** | Role: `{st.session_state.get('role')}` | Email: `{user.get('email', '')}`")
        if st.button("Sign Out of Session", key="sign_out_btn"):
            st.session_state["token"] = None
            st.session_state["user"] = None
            st.session_state["role"] = None
            st.rerun()
    else:
        st.markdown("Sign in with your verified institutional health center credentials to access clinical workflows:")
        auth_col1, auth_col2, auth_col3 = st.columns([1, 1, 1])
        with auth_col1:
            role_choice = st.selectbox("Role", ["Worker", "Doctor", "Admin"])
        with auth_col2:
            default_email = (
                "worker@arogyamitra.gov.in" if role_choice == "Worker"
                else ("doctor@arogyamitra.gov.in" if role_choice == "Doctor"
                else "admin@arogyamitra.gov.in")
            )
            email_input = st.text_input("Institutional Email", value=default_email)
        with auth_col3:
            default_pwd = (
                "Worker@Arogya2026!" if role_choice == "Worker"
                else ("Doctor@Arogya2026!" if role_choice == "Doctor"
                else "Admin@Arogya2026!")
            )
            password_input = st.text_input("Password", type="password", value=default_pwd)

        if st.button("🔓 Sign In to ArogyaMitra", type="primary", use_container_width=True):
            with st.spinner("Authenticating with Express security layer..."):
                auth_res = login_user(email_input, password_input, role_choice)
                if auth_res.get("success"):
                    st.session_state["token"] = auth_res["accessToken"]
                    st.session_state["user"] = auth_res["user"]
                    st.session_state["role"] = auth_res["role"]
                    st.success(f"Authentication successful! Logged in as {auth_res['role']}.")
                    st.rerun()
                else:
                    st.error(f"Sign-in failed: {auth_res.get('error', 'Invalid credentials')}")

st.divider()

# Quick Navigation Portals
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 👩‍⚕️ Community Health Worker")
    st.markdown(
        "Triage patients at village sub-centers or home visits. "
        "Select presenting symptoms from 131 clinical categories, run AI predictions, "
        "inspect Bayesian evidence weights, and escalate high-risk cases to physicians."
    )
    if st.button("🚀 Launch Worker Triage", type="primary", use_container_width=True):
        st.switch_page("pages/1_Worker_Triage.py")

with col2:
    st.markdown("### 🩺 Medical Officer Review")
    st.markdown(
        "Remote physician review workstation. Review escalated cases, "
        "evaluate differential diagnoses alongside exact Bayesian log-odds feature attributions, "
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
    st.markdown("#### 🔬 Bernoulli Naive Bayes")
    st.markdown("Robust probabilistic classifier (v2.0.0) achieving 98.9% top-1 accuracy under 30% missing symptoms.")

with c2:
    st.markdown("#### 🔍 Exact Bayesian XAI")
    st.markdown("Exact log-odds feature contributions explaining symptom evidence weight with proven additivity.")

with c3:
    st.markdown("#### 🔒 Zero-Trust Security")
    st.markdown("Argon2id hashing, AES-256-GCM patient encryption with key rotation, and DPDP Act 2023 compliance.")

with c4:
    st.markdown("#### 🌐 Multilingual Edge")
    st.markdown("Full vernacular clinical report generation and UI localization in English, Hindi, and Marathi.")
