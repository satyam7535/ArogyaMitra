# ArogyaMitra — Clinical Red-Flag Review & Vocabulary Alignment
**Status**: DRAFT — FOR CLINICAL BOARD REVIEW  
**Dataset Vocabulary Base**: 131 Standardized Clinical Symptoms (`ML_Model/model/symptom_columns.pkl`)  
**Strict Rule**: `config/red_flags.yaml` must only contain terms existing in the 131-symptom vocabulary. Unmapped terms cause startup failure.

---

## 1. Candidate Emergency Symptoms Mapped to 131-Feature Vocabulary

The following candidate emergency indicators have been verified against the 131-feature dataset vocabulary (`symptom_columns.pkl`) and are submitted for clinical review.

| Candidate Symptom (Vocab Key) | Vocabulary Status | Acuity Level | Clinical Rationale | Proposed Action if Accepted |
|---|---|---|---|---|
| `chest_pain` | **IN VOCABULARY** | Critical | Acute coronary syndrome, myocardial infarction, pulmonary embolism | Immediate cardiac emergency transfer |
| `coma` | **IN VOCABULARY** | Critical | Acute unconsciousness, metabolic encephalopathy, severe CNS depression | Airway protection & tertiary ICU referral |
| `breathlessness` | **IN VOCABULARY** | High / Critical | Acute respiratory failure, pulmonary edema, severe status asthmaticus | Oxygen administration & urgent physician triage |
| `blood_in_sputum` | **IN VOCABULARY** | High | Hemoptysis, pulmonary hemorrhage, severe open cavitary tuberculosis | Urgent isolation & chest physician review |
| `bloody_stool` | **IN VOCABULARY** | High | Massive lower/upper gastrointestinal bleeding, acute mesenteric ischemia | Hemodynamic monitoring & surgical referral |
| `loss_of_balance` | **IN VOCABULARY** | High | Acute cerebellar stroke, vestibular crisis, posterior circulation TIA | Immediate stroke protocol evaluation |
| `acute_liver_failure` | **IN VOCABULARY** | Critical | Fulminant hepatic failure, coagulopathy, hepatic encephalopathy | Urgent intensive care & hepatology referral |
| `altered_sensorium` | **IN VOCABULARY** | Critical | Delirium, sepsis, severe hypoglycemia, acute encephalitis | Neurological assessment & emergency vitals |
| `slurred_speech` | **IN VOCABULARY** | High | Acute ischemic/hemorrhagic stroke, acute cranial nerve deficit | Rapid stroke code within thrombolysis window |
| `stomach_bleeding` | **IN VOCABULARY** | High | Peptic ulcer perforation/hemorrhage, esophageal varices bleed | Immediate IV fluids & urgent endoscopy triage |
| `toxic_look_(typhos)` | **IN VOCABULARY** | High | Severe septicemia, severe typhoid crisis, systemic endotoxemia | Immediate antibiotic stabilization & admission |
| `weakness_of_one_body_side` | **IN VOCABULARY** | High | Hemiparesis, acute hemispheric ischemic stroke | Emergency transfer to stroke-capable center |

---

## 2. Emergency Candidates NOT in Current Vocabulary (Requires Model Retraining)

These terms represent acute clinical red flags in emergency medicine but **do not exist** in the legacy 131-feature dataset. Adding them to `config/red_flags.yaml` without retraining the underlying Bayesian/scikit-learn classifier would trigger fail-closed startup validation errors.

| Unmapped Emergency Term | Vocabulary Status | Clinical Significance | Recommended Vocabulary Proxy in 131-Feature Base |
|---|---|---|---|
| `unconsciousness` | **NOT IN VOCABULARY** | Profound neurological depression | Use `coma` or `altered_sensorium` |
| `cyanosis` | **NOT IN VOCABULARY** | Severe arterial hypoxemia | Use `breathlessness` |
| `stridor` | **NOT IN VOCABULARY** | Critical upper airway obstruction | Use `breathlessness` |
| `seizures` / `convulsions` | **NOT IN VOCABULARY** | Status epilepticus, eclampsia | Retraining feature candidate |
| `anaphylaxis` | **NOT IN VOCABULARY** | Severe systemic allergic reaction | Retraining feature candidate |
| `hypotension` / `shock` | **NOT IN VOCABULARY** | Circulatory collapse, septic shock | Retraining feature candidate |
| `cardiac_arrest` | **NOT IN VOCABULARY** | Asystole / VF | Retraining feature candidate |

---

## 3. Clinical Board Recommendations
1. Maintain `config/red_flags.yaml` in its current frozen state until formal sign-off by a licensed Medical Officer.
2. If approved during medical board review, candidates from Section 1 (`altered_sensorium`, `acute_liver_failure`, `slurred_speech`, `stomach_bleeding`, `weakness_of_one_body_side`, `toxic_look_(typhos)`) can be safely incorporated into `config/red_flags.yaml` as zero breaking changes occur to the 131-feature schema.
3. Features in Section 2 require dataset schema expansion (v2.0 data pipeline) before integration.
