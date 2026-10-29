# ArogyaMitra — Threat Model & Security Architecture (STRIDE)

**Project:** ArogyaMitra (AI-Assisted Primary Healthcare Decision Support System)  
**Methodology:** Microsoft STRIDE Threat Modeling Framework  
**Scope:** Client Interfaces (Streamlit/React), API Gateway / Reverse Proxy, Application Backend (Node/Express), Microservices (ML & LangGraph), and Persistence Layer (MongoDB, Encrypted Storage).

---

## 1. System Overview & Trust Boundaries

ArogyaMitra is deployed in primary healthcare centers (PHCs) and community outreach environments across rural India. Healthcare workers collect patient symptoms and vital signs in low-connectivity settings, while medical officers review cases remotely.

```
+-----------------------------------------------------------------------------------------+
| TRUST BOUNDARY 1: UNTRUSTED / EXTERNAL ENVIRONMENT                                      |
|                                                                                         |
|  [ Rural Health Worker (Mobile/Tablet) ]       [ Medical Officer (Desktop/Laptop) ]     |
|          |                                              |                               |
|          +----------------------+-----------------------+                               |
|                                 | TLS 1.3 / HTTPS (HSTS enforced)                       |
+---------------------------------|-------------------------------------------------------+
                                  v
+-----------------------------------------------------------------------------------------+
| TRUST BOUNDARY 2: DEMILITARIZED ZONE (DMZ) / EDGE REVERSE PROXY                         |
|                                                                                         |
|  [ Nginx / Caddy Edge Gateway ]                                                         |
|  - TLS 1.3 Termination & HSTS Preload                                                   |
|  - Global Rate Limiting & Request Sanitization                                          |
|  - WAF / Security Headers (CSP, X-Frame-Options, HPP)                                   |
|          |                                                                              |
+----------|------------------------------------------------------------------------------+
           | Internal Network (Port 5000)
           v
+-----------------------------------------------------------------------------------------+
| TRUST BOUNDARY 3: APPLICATION SERVICES LAYER                                            |
|                                                                                         |
|  [ Express 5 Secure Backend ]                                                           |
|  - Role-Based Access Control (RBAC) & Tenant Scoping (404 Anti-Enumeration Rule)         |
|  - Argon2id Password Hashing & Refresh Token Family Rotation                            |
|  - Asynchronous Job Queue (concurrency throttling)                                     |
|  - Server-Side AI Pipeline Orchestrator                                                 |
|          |                                              |                               |
|          | Internal Service JWT                         | Mongoose (AES-256-GCM)        |
|          v                                              v                               |
|  +--------------------------------+           +---------------------------------------+ |
|  | TRUST BOUNDARY 4: INTERNAL     |           | TRUST BOUNDARY 5: DATA LAYER          | |
|  | MICROSERVICES NETWORK          |           |                                       | |
|  | [ FastAPI ML Service :8000 ]   |           | [ MongoDB Multi-Tenant Cluster ]      | |
|  | - Bernoulli Naive Bayes v2.0.0 |           | - Encrypted Patient PII (AES-256-GCM) | |
|  | - Exact Bayesian Attributions  |           | - AuditLog Collection (Append-Only)   | |
|  | - Clinical Red Flags Filter    |           | - Versioned Consultations (OCC)       | |
|  | [ LangGraph Service :8001 ]    |           |                                       | |
|  | - Safe Gemini LLM Pipeline     |           | [ Cloudinary Object Store ]           | |
|  | - Prompt Injection Guardrail   |           | - Signed Report Attachments           | |
|  | - Deterministic Fallback Node  |           +---------------------------------------+ |
|  | - ReportLab Multilingual PDF   |                                                     |
|  +--------------------------------+                                                     |
+-----------------------------------------------------------------------------------------+
```

---

## 2. Asset Classification

| Asset ID | Asset Description | Confidentiality | Integrity | Availability | Storage / Transit State |
|:--------:|:------------------|:---------------:|:---------:|:------------:|:------------------------|
| **A-1** | Patient PII (Name, Phone, Address, Age, Gender) | HIGH | HIGH | MEDIUM | Encrypted at rest (AES-256-GCM), TLS 1.3 in transit |
| **A-2** | Patient Clinical Symptoms & Consultation History | HIGH | CRITICAL | HIGH | MongoDB with tenant scoping, TLS 1.3 in transit |
| **A-3** | ML Model Weights, Scalers, & Encoders | MEDIUM | CRITICAL | HIGH | Ephemeral container volume, SHA-256 validated |
| **A-4** | Gemini API Keys & Internal Service Secrets | CRITICAL | CRITICAL | HIGH | Environment variables (`.env`), never committed to VCS |
| **A-5** | User Authentication Credentials (Passwords, JWTs) | CRITICAL | CRITICAL | HIGH | Argon2id hashes, rotating token families, httpOnly cookies |
| **A-6** | System Audit Logs | HIGH | CRITICAL | HIGH | Immutable append-only collection, tamper-evident timestamps |

---

## 3. STRIDE Threat Analysis Matrix

### 3.1 Spoofing Identity (S)

| Threat ID | Threat Scenario | Impact | Likelihood | Mitigation Implemented | Verification Mechanism |
|:---------:|:----------------|:------:|:----------:|:-----------------------|:-----------------------|
| **S-01** | Attacker impersonates health worker using intercepted access token | CRITICAL | LOW | Access tokens expire in 15 minutes. Refresh tokens rotate on every exchange. Refresh token reuse triggers immediate family-wide revocation. | `tests/security.test.js` (Token Family Revocation test) |
| **S-02** | Attacker calls internal ML/Graph microservices directly from outside | HIGH | MEDIUM | Microservices run in private Docker network and require signed `X-Internal-Service-Token` (HMAC-SHA256 / JWT). | `graph/tests/test_phase3.py` (`test_verify_service_token_*`) |
| **S-03** | Attacker brute-forces worker or doctor account passwords | HIGH | MEDIUM | Argon2id password hashing + 5-attempt account lockout for 15 minutes (`HTTP 423 Locked`). | `tests/security.test.js` (Brute-force lockout test) |
| **S-04** | Unauthorized self-registration of Admin accounts | CRITICAL | HIGH | Public `/admin/register` endpoint permanently disabled (`HTTP 403 REGISTRATION_DISABLED`). Admin provisioning restricted to CLI seed script. | `tests/security.test.js` (Disabled public register test) |

---

### 3.2 Tampering with Data (T)

| Threat ID | Threat Scenario | Impact | Likelihood | Mitigation Implemented | Verification Mechanism |
|:---------:|:----------------|:------:|:----------:|:-----------------------|:-----------------------|
| **T-01** | Man-in-the-Middle modifies symptoms or diagnosis in transit | CRITICAL | MEDIUM | Strict TLS 1.3 + HSTS (`max-age=63072000`). Reverse proxy blocks plaintext downgrades. Field-level AES-256-GCM authenticated encryption. | `docs/evidence/mitm_demo.md` |
| **T-02** | Rogue client submits fake ML diagnosis to bypass doctor review | CRITICAL | HIGH | Client direct write routes (`/:id/analysis/*`) permanently blocked with `HTTP 403`. All AI analyses are orchestrated exclusively server-side. | `tests/security.test.js` + `consultation.controller.js` |
| **T-03** | Concurrent writers overwrite each other's decisions (Lost Update) | HIGH | MEDIUM | Optimistic Concurrency Control (`optimisticConcurrency: true`) on Mongoose schemas rejects stale `__v` versions with `VersionError`. | `tests/concurrency.test.js` (OCC collision test) |
| **T-04** | Prompt injection in symptoms alters LLM diagnosis summary | HIGH | MEDIUM | Input sanitization removes instruction tags. Input wrapped in `<clinical_data>`. Prompt strictly forbids overriding ML primary diagnosis. | `graph/tests/test_phase3.py` (`test_prompt_injection_*`) |

---

### 3.3 Repudiation (R)

| Threat ID | Threat Scenario | Impact | Likelihood | Mitigation Implemented | Verification Mechanism |
|:---------:|:----------------|:------:|:----------:|:-----------------------|:-----------------------|
| **R-01** | Doctor denies providing a misdiagnosed second opinion | CRITICAL | LOW | Every consultation update logs immutable audit records with `doctorId`, `timestamp`, `ipAddress`, and `consultationId`. | `Backend/src/models/audit/auditLogSchema.js` |
| **R-02** | Worker denies escalating a high-risk patient case | HIGH | LOW | `logAuditEvent` triggers on every triage transition (`CONSULTATION_SUBMITTED`, `CONSULTATION_ANALYZED`, `SECOND_OPINION_SUBMITTED`). | `Backend/src/middlewares/audit.middleware.js` |

---

### 3.4 Information Disclosure (I)

| Threat ID | Threat Scenario | Impact | Likelihood | Mitigation Implemented | Verification Mechanism |
|:---------:|:----------------|:------:|:----------:|:-----------------------|:-----------------------|
| **I-01** | Database breach exposes patient phone numbers and addresses | CRITICAL | MEDIUM | AES-256-GCM authenticated field encryption applied to `patient.phone` and `patient.address` before persistence. Raw DB dump yields only ciphertext. | `tests/security.test.js` (AES-256-GCM test) |
| **I-02** | Cross-tenant patient record enumeration via ID guessing | HIGH | MEDIUM | Multi-tenant organization scoping returns `HTTP 404 Not Found` (never 403) on cross-tenant queries, preventing attacker from verifying ID existence. | `tests/security.test.js` (Anti-enumeration 404 test) |
| **I-03** | Server error leaks stack traces and database schema | MEDIUM | HIGH | Production error handlers strip stack traces, mask error internals, and disable `X-Powered-By` header. | `tests/security.test.js` (Security headers test) |

---

### 3.5 Denial of Service (D)

| Threat ID | Threat Scenario | Impact | Likelihood | Mitigation Implemented | Verification Mechanism |
|:---------:|:----------------|:------:|:----------:|:-----------------------|:-----------------------|
| **D-01** | Flooding auth endpoints exhausts server compute | HIGH | HIGH | `express-rate-limit` enforces 15 requests per 15-minute window per IP on `/auth/*` and 150 req/min globally. | `tests/security.test.js` + `security.middleware.js` |
| **D-02** | Flooding heavy AI analysis pipeline freezes Node.js event loop | HIGH | MEDIUM | Background job queue throttles concurrent analysis jobs (`maxConcurrency: 5`). Sync requests offloaded to async job worker returning HTTP 202. | `tests/concurrency.test.js` + `docs/evidence/load_test.md` |
| **D-03** | Microservice thread exhaustion from slow external LLM API | HIGH | HIGH | LLM invocation uses strict 15.0s timeout with automatic deterministic fallback node (`llmFallback: true`), guaranteeing sub-second recovery. | `graph/tests/test_phase3.py` (LLM timeout fallback test) |

---

### 3.6 Elevation of Privilege (E)

| Threat ID | Threat Scenario | Impact | Likelihood | Mitigation Implemented | Verification Mechanism |
|:---------:|:----------------|:------:|:----------:|:-----------------------|:-----------------------|
| **E-01** | Worker tokens access administrative dashboard or doctor review routes | CRITICAL | MEDIUM | Role-based middleware `verifyToken(["admin"])` / `verifyToken(["doctor"])` validates token claims and rejects unauthorized roles with HTTP 403. | `tests/security.test.js` (RBAC role rejection test) |
| **E-02** | NoSQL parameter pollution / operator injection (`$ne`, `$gt`) | HIGH | MEDIUM | Express 5-compatible recursive NoSQL injection sanitizer strips `$` and `.` prefixes from `req.body` and `req.params`. `hpp` prevents HTTP parameter pollution. | `tests/security.test.js` + `security.middleware.js` |

---

## 4. Clinical Safety Safeguards

1. **Mandatory Non-Diagnostic Disclaimer:** Every PDF report, UI dashboard, and API response embeds an explicit clinical disclaimer stating the system provides decision support and does not replace a licensed medical practitioner.
2. **Automated Clinical Escalation & Threshold Coverage:**
   - Any prediction with model confidence < 45% automatically sets `needsEscalation: true` (`uncertaintyReason: "LOW_CONFIDENCE"`).
   - Any prediction with symptom severity >= 4.0 sets `needsEscalation: true` (`uncertaintyReason: "HIGH_SEVERITY"`).
   - Threshold coverage derived from validation data routes low-confidence and high-uncertainty cases safely to a physician.
3. **Clinical Red Flags Fail-Closed Intercept (`config/red_flags.yaml`):**
   - Startup validation strictly fails if `config/red_flags.yaml` contains unrecognized symptoms, unreviewed status, or missing notices.
   - Any patient presentation containing a red-flag symptom immediately forces `redFlag: true`, `needsEscalation: true`, `risk: "High"`, and displays an urgent red-flag banner in UI and multilingual PDF.
4. **DPDP Act (2023) Consent Refusal Gate:**
   - `/api/v1/consultation/:id/analyze` and `/analyze/async` enforce strict consent verification. If patient consent is missing (`consentGiven === false`), withdrawn (`revokedAt != null`), or the patient is soft-deleted, analysis is refused with `HTTP 403 CONSENT_REQUIRED`.
5. **Human-in-the-Loop Clinical Workflows (Flow Steps 10 & 11):**
   - Frontline health workers review AI recommendations and either accept (`PATCH /:id/accept`) or escalate to a medical officer (`PATCH /:id/escalate`).
   - Medical officers query assigned pending cases (`GET /pending`) and submit second opinions (`PATCH /:id/respond`).
   - Optimistic Concurrency Control (`optimisticConcurrency: true`) rejects concurrent modifications with `HTTP 409 Conflict`, preventing lost updates.
6. **Deterministic Safety Fallback:**
   - If the Gemini LLM endpoint is unreachable, throttled, or returns malformed text, the deterministic clinical rule engine generates localized clinical precautions directly from the validated ML feature attributions without crashing (`llmFallback: true`).
