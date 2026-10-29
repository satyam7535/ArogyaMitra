# ArogyaMitra — Privacy Architecture & DPDP Act (2023) Compliance

**Document Version:** 1.0.0  
**Regulatory Frameworks:**
- Digital Personal Data Protection Act, 2023 (DPDP Act, India)
- National Digital Health Mission (NDHM / Ayushman Bharat Digital Mission) Health Data Management Policy
- HIPAA Security and Privacy Rule Principles (Security by Design)

---

## 1. Executive Summary

ArogyaMitra processes sensitive personal data, including health data, biometric identifiers, and contact details for patients in primary healthcare settings. This document establishes how ArogyaMitra implements privacy-by-design, fulfilling the statutory duties of a **Data Fiduciary** and **Data Processor** under the DPDP Act 2023.

---

## 2. Key Roles and Responsibilities

| DPDP Act Role | Entity in ArogyaMitra | Obligations |
|:--------------|:---------------------|:------------|
| **Data Principal** | The Patient | Natural person whose health data and symptoms are processed. Possesses statutory rights of consent, correction, and erasure. |
| **Data Fiduciary** | Primary Health Centre (PHC) / Sub-Centre / Hospital | The healthcare institution determining the purpose and means of data processing. |
| **Data Processor** | ArogyaMitra Platform Infrastructure | Operates the software, ML inference engine, and database under the direct instructions of the Data Fiduciary. |
| **Consent Manager** | Health Worker Interface (Streamlit) | Collects, manages, and records verifiable, informed consent before any clinical triage record is created. |

---

## 3. Core Principles & Implementation

### 3.1 Lawful Basis & Notice (Section 5 & 6)
- **Notice in Vernacular Languages:** Prior to symptom entry, patients are presented with a clear, concise notice in their preferred regional language (English, Hindi, or Marathi).
- **Informed Consent:** Consent is collected explicitly for the sole purpose of triage decision support and physician review.
- **Withdrawal of Consent:** Patients may request withdrawal of consent at any stage, triggering cessation of processing.

### 3.2 Purpose Limitation (Section 7)
- Personal data collected by ArogyaMitra is used **exclusively** for clinical triage, risk evaluation, and physician second opinion workflows.
- Patient health data is **strictly segregated from ML training pipelines**. The diagnostic model runs offline with frozen, versioned weights; patient data is never forwarded to external third parties or commercial advertising brokers.

### 3.3 Data Minimization (Section 8)
- The system collects only the minimal dataset required for diagnostic assessment:
  - Age, Gender, Presenting Symptoms, and Clinical Notes.
  - Identification numbers are pseudonymized with internal MongoDB ObjectIds.
  - Contact details (Phone, Address) are encrypted immediately upon ingest.

### 3.4 Storage Limitation & Retention Policy
- Triage consultation records are retained in compliance with state medical record regulations (typically 3 to 5 years).
- Closed consultations past the mandatory retention threshold are automatically anonymized or purged via scheduled database lifecycle jobs.

---

## 4. Rights of the Data Principal

| Right | DPDP Section | ArogyaMitra Technical Mechanism |
|:------|:------------:|:--------------------------------|
| **Right to Access** | Sec. 11 | Patients may request a complete printed or digital summary of their consultation, diagnosis, and physician second opinions via multilingual PDF export, or via admin-approved data export (`POST /api/v1/patient/:id/approve-export`). |
| **Right to Correction** | Sec. 12 | Health workers and physicians can correct clerical errors or append clinical observations directly through versioned consultation updates. |
| **Right to Erasure** | Sec. 12 | Patients may request record erasure; requires administrative verification and sign-off via `POST /api/v1/patient/:id/approve-delete`, which anonymizes PII while preserving epidemiology metrics. |
| **Right to Withdraw Consent** | Sec. 6(4) | Patients can withdraw consent at any time via `POST /api/v1/patient/:id/withdraw-consent`, recording timestamp, language, version, and reason, immediately halting all automated processing. |
| **Right to Grievance Redressal** | Sec. 13 | Each deployment designates a Data Protection Officer (DPO). Contact channels and grievance tracking IDs are recorded in the immutable audit log. |

---

## 5. Technical and Organizational Security Measures (TOMs)

1. **Cryptographic Protection at Rest & Key Lifecycle:**
   - Patient phone numbers, physical residential addresses, and emergency contact details are encrypted using authenticated **AES-256-GCM** with 96-bit initialization vectors and 128-bit authentication tags.
   - Ciphertext strings are stored with versioned Key IDs (`keyId:iv:authTag:enc`), enabling seamless, zero-downtime key rotation (`rotateFieldEncryption`) across cryptographic generations without service interruption.
   - Decryption keys are managed via environment variables (`serverConfig.ENCRYPTION_KEY`) and are inaccessible to frontend clients or database administrators.
2. **Cryptographic Protection in Transit:**
   - TLS 1.3 encryption with HTTP Strict Transport Security (HSTS) enforced across all API endpoints.
   - Downgrade attacks and plaintext transmission are blocked at the edge reverse proxy.
3. **Multi-Tenant Data Isolation:**
   - Strict organization-scoping middleware ensures healthcare centers cannot access, view, or enumerate patient records belonging to other health centers.
   - Cross-tenant requests return `HTTP 404 Not Found` (never 403) to prevent resource presence enumeration.
4. **Tamper-Evident Audit Logging:**
   - All accesses, modifications, escalations, and export actions are logged to an append-only `AuditLog` collection capturing user ID, IP address, timestamp, action, and resource identifiers.

---

## 6. Personal Data Breach Protocol (Section 8(6))

In the event of a verified or suspected security breach compromising patient personal data:
1. **Containment & Incident Response:** The security team activates incident containment procedures, revokes active session tokens, and rotates affected cryptographic keys within 1 hour.
2. **Statutory Notification:** Under Section 8(6) of the DPDP Act 2023, formal notification will be submitted to the **Data Protection Board of India (DPBI)** within 72 hours of becoming aware of the breach.
3. **Data Principal Notification:** Affected patients and healthcare centers will be informed with actionable guidance on mitigating potential consequences.
