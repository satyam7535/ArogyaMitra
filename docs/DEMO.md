# ArogyaMitra — 5-Minute Live Demonstration Script

This script provides an examiner-ready walkthrough demonstrating the complete human-in-the-loop clinical decision support workflow.

---

## 0. Demonstration Setup & Pre-Flight Checklist (1 Minute Before)

1. **Verify Services Running**:
   - Backend API: `http://localhost:5000/health` → `{"status":"UP"}`
   - ML Diagnostic Service: `http://localhost:8000/health` → `{"status":"healthy"}`
   - LangGraph Service: `http://localhost:8001/health` → `{"status":"ok"}`
   - Streamlit Workstation: `http://localhost:8501`

2. **Demo Credentials (TEST ONLY, GENERATED FOR EVALUATION)**:
   > [!IMPORTANT]
   > The credentials below are mock test accounts seeded strictly for local evaluation. They are not real user credentials and must never be used in production.
   - **ASHA Worker**: `worker@arogyamitra.gov.in` / `Arogya@2026Secure!`
   - **Medical Officer (Doctor)**: `doctor@arogyamitra.gov.in` / `Arogya@2026Secure!`
   - **Administrator**: `admin@arogyamitra.gov.in` / `Arogya@2026Secure!`

---

## Step 1: Landing Hub & Multilingual Switcher (Minute 0:00 - 0:45)

**Narrative**: *"Welcome to ArogyaMitra. The landing page provides instant microservice health telemetry, regulatory clinical disclaimers, and one-click vernacular language switching for rural health workers."*

1. Open `http://localhost:8501`.
2. Point out the **Live System Telemetry** pill cards showing connected services (`API Gateway`, `ML Diagnostics`, `Clinical Graph`).
3. In the sidebar, change language from **English** to **हिंदी (Hindi)** and **मराठी (Marathi)**.
   - *Observe*: All UI elements, descriptions, and labels translate dynamically.
4. Highlight the persistent statutory disclaimer: *"Clinical Decision Support System for primary healthcare triaging only. Final diagnostic authority rests with licensed Medical Officers."*

---

## Step 2: ASHA Worker Clinical Triage (Minute 0:45 - 2:15)

**Narrative**: *"Now let's walk through an ASHA worker triaging a patient presenting with acute jaundice and fatigue in a rural village."*

1. Navigate to **"1 Worker Triage"** in the sidebar.
2. Under **Patient Demographics**:
   - Name: `Ramchandra Jadhav`
   - Age: `48`, Gender: `Male`, Blood Pressure: `125/82`
3. Click the preset button: **"Case 1: Acute Jaundice (Jaundice / High Bilirubin)"**.
   - *Observe*: The 131-symptom searchable multiselect auto-populates with `itching`, `vomiting`, `fatigue`, `yellowish_skin`, `dark_urine`, `abdominal_pain`.
4. Click **"Run Diagnostic Analysis"**.
5. **Explain the Diagnostic Output**:
   - **Primary Prediction**: **Jaundice** with **Model Confidence Estimate** (e.g., 94.2%). Explain to examiners: *"This is a Bayesian posterior probability estimate from the BernoulliNB model; it is an estimate, not a clinically calibrated probability."**
   - **Bayesian Evidence Attributions**: Hover over the horizontal bar chart. Explain: *"Bayesian Evidence proves mathematically why the model predicted Jaundice—yellowish skin and dark urine contributed +0.48 and +0.32 log-odds to the prediction."*
   - **Differential Diagnoses**: Point out the secondary probabilities (`Hepatitis A`, `Chronic Cholestasis`).
   - **Clinical Safety Banner**: If an acute condition is present or confidence is low, highlight the **Needs Escalation** banner advising immediate hospital transfer.
6. Click **"Download Official Medical PDF Report"**.
   - *Open the downloaded PDF*: Show the bilingual formatting, patient vitals, Bayesian Evidence summary, and blank physician sign-off section.

---

## Step 3: Medical Officer (Doctor) Review (Minute 2:15 - 3:45)

**Narrative**: *"The consultation is now in the doctor's review queue. Let's see how the Medical Officer reviews the case."*

1. Navigate to **"2 Doctor Review"** in the sidebar.
2. Select consultation case: `Ramchandra Jadhav — Case #1 (Triage: Jaundice)`.
3. **Review Clinical Evidence**:
   - The doctor inspects the reported symptoms, vitals, and the AI differential.
   - The doctor reviews the **SHAP Attribution Breakdown** to confirm clinical validity.
4. **Physician Verdict & Prescription**:
   - Select Confirmed Diagnosis: `Jaundice (Confirmed)`.
   - Enter Physician Prescription:
     - *"Tab. Silymarin 140mg TID x 14 days"*
     - *"LFT and Ultrasound Abdomen review within 48 hours"*
     - *"Strict bed rest, low-fat diet, plenty of oral fluids"*
   - Select Referral Action: `District Civil Hospital (Routine OPD)`.
5. Click **"Submit Physician Verdict & Sign Consultation"**.
   - *Observe*: Case status transitions from `Pending Review` to `Signed Off`.

---

## Step 4: Admin Governance & Security Audit Trail (Minute 3:45 - 5:00)

**Narrative**: *"Finally, let's inspect the administrative governance and security telemetry."*

1. Navigate to **"3 Admin Dashboard"** in the sidebar.
2. **Operational KPIs**:
   - Total Consultations: `14`
   - Pending Reviews: `2`
   - High-Risk Escalations: `3`
   - System Health: `99.9%`
3. **Epidemiological Prevalence**:
   - Point out the interactive Plotly Donut Chart showing regional disease distribution (Jaundice, Malaria, Dengue, Type-2 Diabetes).
4. **Job Queue & Concurrency Telemetry**:
   - Point out the queue worker limits (`maxConcurrency: 5`), showing zero dropped connections during high load.
5. **Security & Cryptographic Audit Log**:
   - Highlight:
     - `Argon2id` password hashing status.
     - `AES-256-GCM` field-level PII encryption active.
     - Real-time immutable audit trail recording user logins, consultation updates, and access timestamps.

**Conclusion**: *"ArogyaMitra delivers an end-to-end, privacy-compliant, mathematically rigorous, and explainable primary healthcare triage system designed specifically for the operational realities of rural India."*
