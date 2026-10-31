# 🚨 ArogyaMitra — Clinical Red-Flag Governance & Review Protocol

> [!IMPORTANT]
> **Status**: `DRAFT` (Pending Institutional Ethics & Medical Board Review)  
> **Notice**: All red-flag triggers and escalation criteria in `config/red_flags.yaml` represent a provisional decision-support baseline. They MUST be formally reviewed, calibrated to regional disease patterns, and approved by a licensed Medical Officer prior to field deployment.

---

## 1. Clinical Rationale & Objective
In primary rural healthcare triage, community health workers (ASHA/ANM) frequently encounter acute presentations that carry severe morbidity or mortality risk if treatment is delayed. 

The **ArogyaMitra Red-Flag Safety Subsystem** operates as a deterministic clinical override layer sitting in front of the statistical machine learning model. Whenever an alert symptom or critical condition is detected:
1. `needsEscalation` is forced to `true`.
2. `redFlag` is forced to `true`.
3. `risk` acuity is elevated to `High`.
4. **Decision B Override Gate**: Direct local worker acceptance is **strictly blocked** (HTTP 409 Conflict). The case cannot be closed locally and must be formally referred to a registered medical practitioner.

---

## 2. Red-Flag Symptom Matrix (131-Feature Vocabulary)

The table below lists each configured red-flag trigger strictly mapped to the model's feature vocabulary:

| Symptom Token | Acuity | Presumed Clinical Risk / Differential | Required Immediate Action | Clinician Sign-Off |
|---|---|---|---|---|
| `chest_pain` | Critical | Acute Coronary Syndrome (MI), Pulmonary Embolism, Aortic Dissection | Immediate emergency transfer to facility with 12-lead ECG & cardiac care. | `[ ] Approved [ ] Modified` |
| `coma` | Critical | Acute neurological crisis, traumatic brain injury, severe diabetic ketoacidosis/hypoglycemia | Immediate airway stabilization, emergency 108 transfer. | `[ ] Approved [ ] Modified` |
| `breathlessness` | High | Acute pulmonary edema, severe bronchospasm, tension pneumothorax | High-flow oxygen if available; urgent physician assessment. | `[ ] Approved [ ] Modified` |
| `blood_in_sputum` | High | Active pulmonary hemorrhage, cavitary tuberculosis, bronchogenic malignancy | Airborne isolation precautions; urgent chest radiography and sputum smear. | `[ ] Approved [ ] Modified` |
| `bloody_stool` | High | Acute lower/upper gastrointestinal hemorrhage, dysentery with dehydration | Hemodynamic monitoring, IV fluid access, urgent medical officer referral. | `[ ] Approved [ ] Modified` |
| `loss_of_balance` | High | Cerebellar stroke, intracranial hemorrhage, acute vestibular crisis | Neurological deficit evaluation within thrombolysis window. | `[ ] Approved [ ] Modified` |

---

## 3. High-Risk Disease Categories (Acuity Escalation)

| Primary Condition | Clinical Category | Clinical Rule | Overriding Rationale |
|---|---|---|---|
| `Heart attack` | Cardiovascular | Forced Escalation | High mortality risk outside hospital intervention. |
| `Paralysis (brain hemorrhage)` | Neurological | Forced Escalation | Acute stroke pathway required. |
| `Tuberculosis` | Infectious Disease | Forced Escalation | Public health notification, DOTS protocol, MDR risk. |
| `Pneumonia` | Respiratory | Forced Escalation | Hypoxia risk requiring auscultation, CXR, and antibiotic prescription. |

---

## 4. Clinician Formal Review & Sign-Off Template

### Medical Review Board Attestation

*This section must be completed and signed by an authorized physician holding a valid Medical Council registration prior to non-experimental use.*

```
Reviewing Clinician Information:
  Full Name: ___________________________________________________________
  State Medical Council Registration No.: ______________________________
  Clinical Specialty: ___________________________________________________
  Affiliated Hospital / PHC: ___________________________________________
  Contact Email / Phone: _______________________________________________

Evaluation Checklist:
  [ ] 1. Are the designated red-flag symptoms sufficient to capture acute life threats in rural primary care?
  [ ] 2. Are the recommended triage immediate actions clinically safe, evidence-based, and non-prescriptive?
  [ ] 3. Is the mandatory escalation rule (blocking local worker closure) clinically appropriate for frontline safety?
  [ ] 4. Are there regional endemic conditions (e.g. Kyasanur Forest Disease, Scrub Typhus) that warrant addition?

Review Decision:
  [ ] APPROVED WITHOUT MODIFICATION
  [ ] APPROVED WITH NOTED MODIFICATIONS (see attached comments)
  [ ] REJECTED (requires revision of symptom thresholds)

Clinician Signature: ___________________________    Date: _______________
Hospital Seal:
```

---

## 5. Software Fail-Closed Verification
Software enforcement of this review state is verified in the automated test suite:
- `ML_Model/tests/test_clinical_red_flags.py`: Validates that unmapped vocabulary terms fail closed at startup.
- `Backend/tests/security.test.js`: Confirms that attempting to accept a red-flag consultation locally strictly returns `HTTP 409 Conflict`.
