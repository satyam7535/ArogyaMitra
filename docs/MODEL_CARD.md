# 🩺 Model Card: ArogyaMitra Disease Prediction System (v1.0.0)

## 1. Model Details
- **Organization / Project**: ArogyaMitra — AI-Assisted Primary Healthcare Decision Support System
- **Model Version**: `v1.0.0`
- **Release Date**: October 2026
- **Architecture**: Gradient Boosted Decision Trees (`LightGBM`) coupled with `CalibratedClassifierCV` (sigmoid scaling) and `TreeSHAP` (`shap.TreeExplainer`)
- **Downstream Consumers**: ArogyaMitra Backend API (`POST /api/v1/consultation/:id/analyze`), LangGraph Orchestration Service, Streamlit Clinical Triage UI
- **License**: Apache 2.0 / Academic Project License

---

## 2. Intended Use & Clinical Scope
- **Primary Purpose**: Assist Accredited Social Health Activists (ASHA) and rural community health workers in structuring symptom intake and prioritizing differential diagnoses before physician consultation.
- **Intended Users**: Community health workers, primary care triage nurses, and supervising medical doctors.
- **Out-of-Scope & Contraindicated Uses**:
  - **NEVER** for autonomous prescription or unverified diagnosis.
  - **NEVER** for emergency trauma triage (e.g., severe blunt trauma, acute cardiac arrest, active stroke) without immediate physical emergency response.
  - **NEVER** without the presence of human medical supervision.

---

## 3. Dataset Hygiene & Integrity
- **Source**: Curated Kaggle Disease-Symptom Benchmark.
- **Original Training Set**: 4,920 rows.
- **Critical Finding**: 4,616 rows (93.8%) were exact duplicates. Past published baselines reporting 100% test accuracy suffered from severe duplicate data leakage (testing on rows already present in the training set).
- **Sanitized Dataset**:
  - **Unique Ground-Truth Samples**: 304 unique symptom presentations (~7.4 unique presentations per disease).
  - **Features**: 131 binary symptom indicators (after merging duplicate artifact columns like `fluid_overload` and normalizing typos like `foul_smell_ofurine`, `spotting__urination`, `dischromic__patches`).
  - **Target Classes**: 41 distinct acute and chronic medical conditions.
- **Augmentation Policy**: Symptom-dropout data augmentation (0% to 50% random masking of present symptoms, 3 copies per sample) applied **strictly inside training folds** during cross-validation. Zero test or validation vectors were ever augmented or leaked.

---

## 4. Empirical Evaluation & Benchmark Summary
Evaluated across 15 validation splits (Repeated Stratified K-Fold: 5 splits × 3 repeats) across 6 model families with and without symptom-dropout augmentation under realistic missing symptom rates (0%, 30%, 50% omitted symptoms).

| Model Family | Augmentation | Accuracy (0% Hidden) | Accuracy (50% Hidden) | Top-3 Accuracy (50% Hidden) | Log Loss (50% Hidden) | ECE (50% Hidden) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Logistic Regression** | Yes | 99.89 ± 0.41% | 91.23 ± 3.15% | 98.90 ± 1.15% | 0.8240 | 0.3915 |
| **Bernoulli Naive Bayes** | Yes | 100.00 ± 0.00% | 92.65 ± 2.62% | 99.12 ± 1.32% | 0.2136 | 0.0609 |
| **Random Forest** | Yes | 99.45 ± 0.98% | 88.05 ± 3.25% | 96.71 ± 2.32% | 1.7086 | 0.6302 |
| **MLP (Small)** | Yes | 99.67 ± 0.66% | 88.37 ± 4.42% | 98.25 ± 1.40% | 0.9086 | 0.3830 |
| **XGBoost** | Yes | 98.79 ± 1.27% | 77.29 ± 5.81% | 90.46 ± 2.96% | 0.8934 | 0.1316 |
| **LightGBM (Final)** | Yes | 94.51 ± 3.11% | 57.88 ± 7.73% | 75.42 ± 5.69% | 1.8346 | 0.1991 |

---

## 5. Explainability & Interpretability
- **Mechanism**: `TreeSHAP` (`shap.TreeExplainer`).
- **Attribution Granularity**: Computes exact Shapley values per present and absent symptom for the top-predicted differential diagnosis.
- **Directionality**: Classified as `"Supports Diagnosis"` (positive attribution) or `"Against Diagnosis"` (negative attribution).
- **Clinical Utility**: Enables the consulting doctor to audit exactly which patient symptoms drove the algorithm's suspicion.

---

## 6. Uncertainty Scoring & Automatic Escalation Rules
To guarantee patient safety, the inference service triggers `needsEscalation = True` and populates `uncertaintyReason` when any of the following safety thresholds are breached:
1. **Low Confidence Threshold**: Top-1 calibrated probability `< 55%`. Indicates ambiguous presentation requiring physician differentiation.
2. **Narrow Margin Threshold**: Margin between Top-1 and Top-2 differential diagnoses `< 15%`. Indicates high diagnostic overlap.
3. **High-Acuity Symptom Trigger**: Any reported symptom with clinical severity score `≥ 4.5 / 7` (e.g., chest pain, breathlessness, blood in sputum). Triggers urgent physician escalation regardless of confidence.

---

## 7. Limitations & Ethical Safeguards
- **Binary Symptom Input**: Current model takes binary presence/absence and does not capture symptom duration, trajectory, or severity gradations.
- **Geographic Bias**: Disease prevalence distributions in Kaggle benchmark may differ from specific district-level epidemiology in rural India.
- **Statutory Disclaimer**: *ArogyaMitra is a clinical decision-support software tool designed to augment healthcare professionals. It does not provide medical diagnosis, prescribe pharmaceutical treatments, or replace the clinical judgment of a licensed medical practitioner.*
