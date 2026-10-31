# ArogyaMitra — Known Limitations & Clinical Disclosures

This document candidly lists the known technical, architectural, statistical, and clinical limitations of the ArogyaMitra platform in accordance with strict engineering integrity standards.

---

## 1. Machine Learning & Dataset Constraints

1. **Synthetic & Duplicated Source Data**:
   - The underlying symptom-disease dataset originates from a public Kaggle dataset comprising 4,920 total records.
   - Rigorous data provenance analysis revealed that 4,616 of these records were exact duplicates (93.8% duplication rate), leaving only 304 unique symptom vectors across 41 disease classes.
   - While the deployed Bernoulli Naive Bayes model (`v2.0.0`) was trained and evaluated strictly on deduplicated data with symptom-dropout cross-validation, the dataset remains synthetic. It lacks real-world epidemiological frequency distributions, patient demographics, and complex co-morbidities.
   - No symptom severity grades exist in the raw training dataset: all symptoms are modeled as binary indicators ($x_i \in \{0, 1\}$).

2. **Conditional Feature Independence Assumption**:
   - Bernoulli Naive Bayes assumes conditional independence among presenting symptoms given the disease class: $P(x_1, \dots, x_d \mid Y=c) = \prod_{i=1}^d P(x_i \mid Y=c)$.
   - In human pathophysiology, symptoms are not conditionally independent given a disease (e.g., `cough`, `sputum_production`, and `chest_discomfort` share common underlying airway inflammation).
   - This assumption causes evidence from correlated symptoms to be double-counted.

3. **Uncalibrated Model Confidence Scores**:
   - The model output scores are uncalibrated Bayesian log-odds sums mapped through a softmax function.
   - They represent relative class ranking confidence rather than true statistical probabilities. A score of 0.85 does NOT mean that 85 out of 100 patients presenting with these symptoms will have that condition.
   - The platform strictly labels all model outputs as **"Model Confidence (Uncalibrated Estimate)"** rather than "Calibrated Probability" or "Certainty".

4. **Frontline Decision Support Only**:
   - The ML model outputs probability distributions across 41 predefined condition classes.
   - It is strictly an assistive screening mechanism for frontline health workers (ASHA/ANM) and cannot replace comprehensive physical examinations, lab diagnostics, or licensed clinical judgment.

---

## 2. LLM Summaries & Deterministic Clinical Fallbacks

1. **External LLM Service & Model Deprecation**:
   - The optional AI summary pipeline integrates with the Google Gemini API.
   - Public API endpoints and specific model identifiers (e.g. `gemini-1.5-flash`) are subject to vendor deprecation, retirement schedules, API quota limits, and network latency.

2. **Draft Fallback Templates**:
   - When the LLM is unreachable, unconfigured, or deprecated, the system engages a deterministic per-disease clinical template engine (`llmFallback: true`).
   - These fallback precaution templates are labeled **DRAFT** and have not undergone comprehensive review by a licensed clinical panel.
   - In accordance with medical ethics and CDSCO guidelines, fallback templates **strictly omit prescription drug names, therapeutic dosages, and invasive interventions**, offering only general supportive guidance (e.g., hydration, rest, vital signs monitoring, and referral advice).

3. **Hallucination & Output Filtering**:
   - While output guardrails enforce risk-floor adherence and reject unpredicted diagnoses, generative LLMs inherently carry a non-zero risk of hallucination. LLM summaries must never be treated as authoritative clinical orders.

---

## 3. Infrastructure & Deployment Boundaries

1. **Self-Signed TLS Certificates**:
   - The Docker edge gateway (`arogya-proxy`) uses a self-signed root certificate (`deploy/certs/arogyamitra.crt`) issued for `arogyamitra.local`.
   - Client applications, browsers, and automated scripts must explicitly trust this certificate or provide `--cacert` to establish strict TLS handshakes. In production, this must be replaced with a CA-signed certificate (e.g., Let's Encrypt or institutional PKI).

2. **Single-Replica Standalone Stack**:
   - The current deployment runs as single-replica containers on a single host node via Docker Compose.
   - It is not configured for high-availability multi-node clustering (Kubernetes), automatic pod autoscaling, or multi-region disaster recovery.

3. **In-Memory Rate Limiting**:
   - Express rate limiters (`authRateLimiter`, `generalApiLimiter`) use default memory stores local to the Node.js process.
   - If the backend is horizontally scaled across multiple container replicas behind a round-robin load balancer, a centralized Redis store must be configured to synchronize client IP quota counters across instances.

4. **Offline Capability Scope**:
   - Frontline mobile clients can cache local symptom entry forms, but executing inference requires network reachability to the local edge gateway or host backend. Fully offline on-device inference (e.g. via ONNX Runtime Web / TFLite in browser) is not yet compiled into the Streamlit interface.

---

## 4. Digital Personal Data Protection (DPDP Act 2023) Compliance

1. **Admin Approval Gate for Data Erasure & Export**:
   - In accordance with DPDP compliance controls, patient consent withdrawal (`PATCH /api/v1/patient/:id/consent`) immediately refuses subsequent AI processing.
   - However, physical data erasure (`DELETE /api/v1/patient/:id`) and bulk CSV export require two-party administrative sign-off (`exportApproved: true`, `deletionApproved: true`) to protect against rogue worker deletion or forensic record tampering.

2. **Audit Log Persistence**:
   - System audit records are stored in an append-only MongoDB collection with index-level access restrictions.
   - They are not currently mirrored to dedicated Write-Once-Read-Many (WORM) optical storage or hardware security modules (HSM).

---

## 5. Indic Script Typography & Devanagari Shaping

1. **PDF Rendering Ligature Constraints**:
   - Multilingual clinical summary PDFs are generated using ReportLab with the bundled Open Font License `Noto Sans Devanagari` typeface.
   - ReportLab utilizes a pure-Python font layout engine that does not incorporate full HarfBuzz complex text shaping.
   - Consequently, while standard Devanagari characters (Hindi and Marathi) render legibly, complex half-consonant conjunct ligatures (*samyuktaksharas*) and pre-base vowel matra reordering (e.g., *chhoti-i ki matra*) may exhibit minor typographical positioning artifacts.

2. **Medical Terminology Simplification**:
   - Regional language translations (Hindi, Marathi) use transliterated and colloquial disease names to assist rural frontline workers, but clinical precision in regional languages requires institutional medical translation review before formal clinical deployment.
