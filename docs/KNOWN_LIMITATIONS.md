# ArogyaMitra — Known Limitations & Clinical Disclosures

This document candidly lists the known technical, architectural, and clinical limitations of the ArogyaMitra platform in accordance with strict engineering integrity standards.

---

## 1. Machine Learning & Dataset Constraints

1. **Synthetic & Duplicated Source Data**:
   - The underlying symptom-disease dataset originates from a public Kaggle dataset comprising 4,920 total records.
   - Rigorous data provenance analysis revealed that 4,616 of these records were exact duplicates (93.8% duplication rate), leaving only 304 unique symptom vectors across 41 disease classes.
   - While the deployed Bernoulli Naive Bayes model (`v2.0.0`) was trained and evaluated strictly on deduplicated data with symptom-dropout cross-validation, the dataset remains synthetic. It lacks real-world epidemiological frequency distributions, patient demographics, and complex co-morbidities.

2. **Conditional Feature Independence Assumption**:
   - Bernoulli Naive Bayes assumes conditional independence among presenting symptoms given the disease class.
   - Although this inductive bias proved superior to decision trees on sparse binary symptom vectors, biological symptoms in human patients often exhibit biological co-dependence (e.g., fever and chills occurring in physiological concert).

3. **Frontline Decision Support Only**:
   - The ML model outputs probability distributions across 41 predefined condition classes.
   - It is strictly an assistive screening mechanism for frontline health workers (ASHA/ANM) and cannot replace comprehensive physical examinations, lab diagnostics, or licensed clinical judgment.

---

## 2. Indic Script Typography & Devanagari Shaping

1. **Pure Python PDF Rendering Engine**:
   - Multilingual clinical summary PDFs are generated using ReportLab with the bundled Open Font License (OFL) `Noto Sans Devanagari` typeface.
   - ReportLab utilizes a pure-Python font layout engine that does not incorporate full HarfBuzz complex text shaping.
   - Consequently, while standard Devanagari characters (Hindi and Marathi) render legibly, complex half-consonant conjunct ligatures (*samyuktaksharas*) and pre-base vowel matra reordering (e.g., *chhoti-i ki matra*) may exhibit typographical positioning artifacts.

2. **Mitigation**:
   - The primary interactive workstation (Streamlit Web UI) leverages modern browser layout engines (Blink / WebKit) with native HarfBuzz/DirectWrite rendering, displaying Hindi and Marathi scripts flawlessly.
   - The PDF report includes standard clinical English disease terminology alongside regional translations to eliminate diagnostic ambiguity.

---

## 3. Concurrency, Scale & Ingress Boundaries

1. **Optimistic Concurrency Control (OCC)**:
   - Clinical second opinions use Mongoose versioning (`optimisticConcurrency: true` on `__v`).
   - If two doctors attempt to submit a review for the same consultation simultaneously, the second write is rejected with HTTP 409 Conflict. The UI prompts the doctor to reload the latest record.

2. **Rate Limiting & Queue Throughput**:
   - In-memory rate limiting (15 requests / 15 minutes for authentication, 150 requests / minute for API endpoints) is enforced per client IP.
   - In multi-instance or horizontally scaled production clusters behind load balancers, rate limiting must be backed by a centralized Redis cluster rather than local node memory.
   - Background triage jobs are persisted in MongoDB (`AnalysisJob`) and processed via atomic `findOneAndUpdate` leases. This queue design is optimized for rural clinic volumes (~100–500 consultations/day) rather than high-frequency enterprise queues.

---

## 4. LLM & External Cloud Service Dependencies

1. **Third-Party API & Quota Limits**:
   - The clinical summary pipeline utilizes the Google Gemini API (via its OpenAI-compatible endpoint).
   - In the free development tier, rate limits (15 requests per minute) and occasional network jitter can occur.

2. **Deterministic Fallback Guarantee**:
   - The system is architected with a fail-safe fallback mechanism (`llmFallback: true`).
   - If the Gemini API times out, throws a quota error, or fails Pydantic schema validation, the system falls back immediately to a deterministic, rules-based clinical summary derived directly from the ML prediction and standard PHC precaution guidelines. No consultation is blocked or lost due to external LLM downtime.

3. **Strict Zero-PII Privacy Boundary**:
   - In accordance with the Digital Personal Data Protection (DPDP) Act, no patient names, phone numbers, addresses, or personal identifiers are ever sent to the LLM. Only de-identified symptom tokens and demographic categories are transmitted.

