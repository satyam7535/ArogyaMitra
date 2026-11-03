# 🏥 ArogyaMitra — Faculty Evaluator Live Demonstration Runbook

> **Demonstration Context**: This runbook provides a complete, 8-step live browser demonstration procedure designed for academic faculty evaluators and external examiners. It validates the full clinical decision-support lifecycle, fail-closed safety interceptors, role-based workflows, and audit governance.

---

## 🛠️ Demonstration Prerequisites

1. **Verify Services Running**:
   ```powershell
   docker compose ps
   powershell -File scripts/health_check.ps1
   ```
2. **Pristine State Reset**:
   To ensure clean zero-state metrics before commencing the evaluation:
   ```powershell
   powershell -File scripts/reset_demo.ps1
   ```
   *(Or on Linux/macOS: `./scripts/reset_demo.sh`)*

3. **Open Browser**:
   Navigate to **`https://localhost`** (or `http://localhost:8501` for direct Streamlit access).
   Accept the self-signed TLS certificate warning for local evaluation.

---

## 👥 Seed Evaluator Credentials (No Real Passwords Committed)

| Role | Email / Username | Default Password | Initial View |
|---|---|---|---|
| **Frontline Worker (ASHA)** | `worker@arogyamitra.gov.in` | `Worker@Arogya2026!` | `1_Worker_Triage` |
| **Medical Officer (Doctor)** | `doctor@arogyamitra.gov.in` | `Doctor@Arogya2026!` | `2_Doctor_Review` |
| **System Administrator** | `admin@arogyamitra.gov.in` | `Admin@Arogya2026!` | `3_Admin_Dashboard` |

---

## 📋 The 8-Step Verification Procedure

### Step 1: Frontline Health Worker Authentication
1. Open the sidebar navigation in the Streamlit workstation and open **`1_Worker_Triage`**.
2. Expand the **Session Login** expander in the sidebar.
3. Enter credentials:
   - **Email**: `worker@arogyamitra.gov.in`
   - **Password**: `Worker@Arogya2026!`
4. Click **Sign In**.
5. Observe the verified banner: `Active Session: worker@arogyamitra.gov.in (Pune District Rural Health Mission)`.

---

### Step 2: Normal Mild Case Intake & Acceptance (Non-Emergency)
1. In the **Patient Intake** section:
   - **Patient Full Name**: `Ramesh Pawar`
   - **Age**: `34`
   - **Gender**: `Male`
   - **Phone**: `9876543210`
   - **DPDP Consent**: Select `"Yes"`
2. Click the quick-fill preset button: **"Normal Cough Case"** (or select `cough`, `mild_fever`, `headache`).
3. Click **"Run Clinical Triage Analysis"**.
4. Observe the results panel:
   - Machine Learning predicted disease: *Common Cold* / *Bronchial Cough*.
   - Red-Flag Banner: **Green** — *No acute danger signs detected*.
   - Acceptance Panel: Active.
5. Click **"Accept & File Primary Care Advice"**.
6. Observe status update: Consultation marked **"closed"** with local care guidance recorded.

---

### Step 3: Red-Flag Acute Emergency Trigger (Decision B Intercept)
1. Register a second consultation for acute emergency evaluation:
   - **Patient Full Name**: `Sunita Sharma`
   - **Age**: `52`
   - **Gender**: `Female`
   - **Phone**: `9812345678`
   - **DPDP Consent**: Select `"Yes"`
2. Click the quick-fill preset button: **"Chest Pain Emergency"** (or select `chest_pain`, `breathlessness`, `sweating`).
3. Click **"Run Clinical Triage Analysis"**.
4. **Safety Verification**:
   - High-visibility **Red Banner** appears:
     > ⚠️ **RED-FLAG EMERGENCY ALERT: Immediate Doctor Escalation Required**
     > *Identified acute indicators: chest_pain (Chest Pain — Rule out Acute Coronary Syndrome).*
   - The **"Accept & File Primary Care Advice"** button is **completely disabled/blocked**.
   - Attempting to bypass or accept displays the clinical safety rule:
     > *"Emergency: cannot accept without a doctor."*

---

### Step 4: Frontline Escalation to Medical Officer
1. In the active emergency consultation:
   - Locate the **"Mandatory Doctor Escalation"** panel.
   - Enter escalation note: `"Patient experiencing acute radiating chest tightness and diaphoresis for 45 minutes."`
2. Click **"Escalate to Medical Officer"**.
3. Observe confirmation banner:
   > `[SUCCESS] Consultation successfully escalated to Medical Officer Queue.`
4. The consultation status transitions from `analyzed` to `escalated`.

---

### Step 5: Medical Officer Queue & Second-Opinion Review
1. Open a **second browser tab** (or incognito window) to `https://localhost`.
2. Navigate to **`2_Doctor_Review`**.
3. In sidebar login, sign in as Medical Officer:
   - **Email**: `doctor@arogyamitra.gov.in`
   - **Password**: `Doctor@Arogya2026!`
4. In the **"Pending Escalated Triage Queue"**:
   - Locate the escalated case for `Sunita Sharma` (marked with acute red-flag badge).
   - Click **"Review Case"**.
5. Inspect the clinical intake:
   - Review ML disease hypothesis, Bayesian symptom attributions, and frontline worker notes.
6. Enter Clinical Override / Sign-off:
   - **Doctor Clinical Assessment**: `"Suspected Acute Coronary Syndrome. Immediate 108 Ambulance referral dispatched."`
   - **Immediate Prescription / Actions**: `"Aspirin 300mg stat, Sorbitrate 5mg sublingual under direct supervision. High-flow oxygen."`
   - **Action**: Select `"Admit / Urgent Hospital Referral"`.
7. Click **"Submit Clinical Assessment & Sign Off"**.
8. Observe confirmation: Case resolved with Optimistic Concurrency Control (`__v`) check.

---

### Step 6: Frontline Worker Verification of Reviewed Status
1. Switch back to the **first browser tab** (Worker session).
2. On `1_Worker_Triage`, scroll down to **"Recent Consultations"** and click **"Refresh Consultations"**.
3. Locate `Sunita Sharma`:
   - Status has transitioned from `escalated` to **`reviewed`**.
4. Click to expand case details:
   - Worker can read the registered Doctor's exact assessment, emergency prescription, and referral directive.
   - Frontline loop is closed safely under registered medical supervision.

---

### Step 7: System Administrator Audit & Telemetry Inspection
1. Navigate to **`3_Admin_Dashboard`** (or sign in via sidebar):
   - **Email**: `admin@arogyamitra.gov.in`
   - **Password**: `Admin@Arogya2026!`
2. **Verify Real Live Telemetry** (Zero simulated/hardcoded numbers):
   - **Total Consultations**: Exactly reflects live database count (e.g., `2`).
   - **Escalation Rate**: Exactly reflects real ratio (`50.0%`).
   - **Reviewed Count**: Exactly `1`.
   - **Average Turnaround**: Real computed time delta from escalation to doctor response.
3. **Verify Security Audit Trail**:
   - Scroll to **"Immutable Security Audit Logs"**.
   - Verify tamper-evident entries:
     - `USER_LOGIN` for worker, doctor, and admin.
     - `PATIENT_REGISTERED` (with masked ID and zero plaintext PII).
     - `CONSULTATION_ESCALATED` and `DOCTOR_REVIEW_SUBMITTED`.
4. Click **"Export Audit Trail (CSV)"** to confirm RFC 4180 formula injection sanitization.

---

### Step 8: Session Security & Automatic 15-Minute Expiry
1. Observe token telemetry in sidebar: JWT access token expires in **15 minutes**.
2. When the token expires (or when clicking **"Sign Out"**):
   - The session cache is immediately cleared.
   - Any protected API request receives `HTTP 401 Unauthorized` with `TOKEN_EXPIRED`.
   - Streamlit displays: `"Your session has expired. Please sign in again."`
3. Attempts to tamper with tokens or forge signatures fail-closed.

---

## 🧹 Post-Demo Cleanup

After concluding the evaluation session:
```powershell
powershell -File scripts/reset_demo.ps1
```
The database is returned to zero-consultation state, ready for subsequent evaluation rounds.
