# 🚨 ArogyaMitra — Clinical Red-Flag Rule Layer & Safety Protocol

## 1. Overview & Statutory Status
- **File**: `config/red_flags.yaml`
- **Clinical Governance Status**: **DRAFT** (`reviewed_by: null`)
- **Review Notice**: *Pending Clinical Review by Licensed Medical Officer*.
- **Purpose**: Augment probabilistic AI predictions with a deterministic, rule-based safety intercept layer. If any presenting patient symptom matches a high-acuity clinical red flag, the system deterministically forces emergency escalation, overrides probabilistic confidence, marks risk as `"High"`, and displays an urgent clinical banner on all digital and PDF outputs.

---

## 2. Red-Flag Intercept Rule Logic
When symptom input is submitted to `POST /predict` (ML microservice) or `POST /analyze` (LangGraph / Backend):
1. **Red-Flag Match**: Input symptoms are compared against `vocabulary_red_flags`.
2. **Deterministic State Override**:
   - `redFlag`: **`true`**
   - `needsEscalation`: **`true`**
   - `risk`: **`"High"`**
   - `uncertaintyReason`: Prepend `"🚨 CLINICAL RED FLAG DETECTED: <symptom> (<clinical_rationale>). Immediate physician triage required. [DRAFT: Pending Clinical Review]"`
   - `redFlagDetails`: Array of matched red-flag objects including symptom, acuity level, rationale, immediate recommended action, and notice.
3. **UI & PDF Urgent Banner**:
   - PDF Report: Prominently renders an urgent highlighted red-flag alert box at top of report.
   - Frontline Worker Triage UI: Renders high-priority red alert (`st.error`) with specific clinical instructions and "Pending Clinical Review" disclaimer.

---

## 3. Vocabulary Mapping & Startup Validation
To prevent configuration drift and silent failures:
- **Startup Validation**: When the ML service or Graph service initializes, it loads `config/red_flags.yaml` and parses all symptoms in `vocabulary_red_flags`.
- **Fail-Closed Guarantee**: Every red-flag symptom MUST exist in `symptom_columns.pkl`. If an unmapped or misspelled symptom is found in `vocabulary_red_flags`, the service **fails closed at startup** with a fatal validation error.
- **Candidate Unmapped Symptoms**: Critical clinical presentations that are not present in the historical 131-column Kaggle benchmark (e.g., `unconsciousness`, `seizure`, `cyanosis`, `anaphylaxis`) are formally tracked in `config/red_flags.yaml` under `candidate_unmapped_symptoms` for prospective vocabulary expansion.

---

## 4. Current Red-Flag Table

| Symptom Token | Acuity Level | Clinical Rationale | Forced Escalation | Immediate Recommended Action |
|---|:---:|---|:---:|---|
| `chest_pain` | Critical | Acute coronary syndrome, myocardial infarction, pulmonary embolism. | YES (`risk: High`) | Immediate transfer to emergency cardiac facility. |
| `coma` | Critical | Severe depression of consciousness; neurological crisis. | YES (`risk: High`) | Immediate airway protection and tertiary referral. |
| `breathlessness` | High | Respiratory distress, acute pulmonary edema, severe bronchospasm. | YES (`risk: High`) | High-flow oxygen if available, immediate physician evaluation. |
| `blood_in_sputum` | High | Hemoptysis; active pulmonary hemorrhage, tuberculosis. | YES (`risk: High`) | Urgent respiratory evaluation, infectious precautions. |
| `bloody_stool` | High | Hematochezia / melena; acute gastrointestinal hemorrhage. | YES (`risk: High`) | Fluid resuscitation, urgent surgical/GI referral. |
| `loss_of_balance` | High | Acute ataxia; potential ischemic stroke or intracranial hemorrhage. | YES (`risk: High`) | Urgent stroke evaluation within thrombolytic window. |
| `fast_heart_rate` | High | Tachyarrhythmia, severe sepsis, or hypovolemic shock. | YES (`risk: High`) | Continuous pulse monitoring, ECG, urgent triage. |

