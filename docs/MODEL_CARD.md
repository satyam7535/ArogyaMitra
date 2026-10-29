# 🩺 Model Card: ArogyaMitra Disease Prediction System (v2.0.0)

## 1. Model Details
- **Organization / Project**: ArogyaMitra — AI-Assisted Primary Healthcare Decision Support System
- **Model Version**: `v2.0.0`
- **Release Date**: October 2026
- **Architecture**: Bernoulli Naive Bayes (`alpha=1.0`, `fit_prior=True`) coupled with Exact Additive Bayesian Log-Odds Feature Attributions
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
- **Critical Finding**: 4,616 rows (93.8%) were exact duplicates. Historical baselines reporting 100% test accuracy suffered from severe duplicate data leakage (evaluating on training row duplicates).
- **Sanitized Dataset**:
  - **Unique Ground-Truth Samples**: 304 unique symptom presentations (~7.4 unique presentations per disease).
  - **Features**: 131 binary symptom indicators (after merging duplicate artifact columns like `fluid_overload` and normalizing typos like `foul_smell_ofurine`, `spotting__urination`, `dischromic__patches`).
  - **Target Classes**: 41 distinct acute and chronic medical conditions.
- **Data Characterization & Provenance**: The dataset is small and synthetically generated from per-disease characteristic symptom lists. The conditional independence assumption of Naive Bayes directly matches this synthetic generation mechanism, which accounts in part for its decisive performance over tree ensembles on this specific benchmark.
- **Augmentation Policy**: Symptom-dropout data augmentation (0% to 50% random masking of present symptoms, 3 copies per sample) applied **strictly inside training folds** during cross-validation. Zero test or validation vectors were ever augmented or leaked.

---

## 4. Empirical Evaluation & Benchmark Summary

### A. In-Sample vs. Out-of-Fold Metrics
- **In-Sample Evaluation on Clean Ground-Truth Data (Full 304 Rows)**:
  - Accuracy: **100.0%**
  - Macro F1: **1.000**
  - Log-Loss: **0.0013**
  - Expected Calibration Error (ECE): **0.0012**
  > [!NOTE]
  > In-sample metrics overstate performance due to memorization and must **never** be used to assert production diagnostic reliability. All production clinical claims must be substantiated by out-of-fold evaluation.

- **Out-of-Fold Repeated Stratified Cross-Validation (Generalization Performance)**:
  - Protocol: 5-Fold $\times$ 3-Repeat Stratified Cross-Validation (15 Splits).
  - 0% Missing Symptoms: Top-1 Accuracy **100.00 ± 0.00%** [1.000, 1.000], Top-3 Accuracy **100.00 ± 0.00%**, Log-Loss **0.0058 ± 0.0042** [0.0037, 0.0080], ECE **0.0052 ± 0.0033** [0.0035, 0.0069].
  - 30% Missing Symptoms: Top-1 Accuracy **98.90 ± 1.36%** [98.21%, 99.59%], Top-3 Accuracy **100.00 ± 0.00%**, Log-Loss **0.0531 ± 0.0240** [0.0410, 0.0652], ECE **0.0322 ± 0.0079** [0.0282, 0.0362].
  - 50% Missing Symptoms: Top-1 Accuracy **91.90 ± 2.30%** [90.73%, 93.07%], Top-3 Accuracy **99.12 ± 1.18%** [98.52%, 99.72%], Log-Loss **0.2790 ± 0.0500** [0.2536, 0.3044], ECE **0.0720 ± 0.0150** [0.0644, 0.0796].

### B. Architecture Decision: Nested CV Benchmark (Tuned Trees vs. Naive Bayes)
To resolve the architecture choice empirically under the pre-declared rule (highest Top-1 at 30% dropout, lowest log-loss; prefer simpler model if CIs overlap), a time-boxed hyperparameter tuning pass was performed for LightGBM and XGBoost using inner 3-fold cross-validation on each of the 15 outer training folds:

| Model | Tuning Protocol | Top-1 Acc (30% Dropout) | 95% Confidence Interval | Log-Loss (30% Dropout) | ECE (30% Dropout) | Decision |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Bernoulli Naive Bayes** | Fixed ($\alpha=1.0$) | **98.90 ± 1.36%** | **[98.21%, 99.59%]** | **0.0531 ± 0.0240** | **0.0322** | **SELECTED (Winner)** |
| **Tuned XGBoost** | Inner 3-Fold Grid | 86.83 ± 4.13% | [84.55%, 89.12%] | 0.6463 ± 0.2078 | 0.1983 | Rejected (Non-overlapping CI) |
| **Tuned LightGBM** | Inner 3-Fold Grid | 86.40 ± 3.99% | [84.19%, 88.60%] | 0.7140 ± 0.2312 | 0.0975 | Rejected (Non-overlapping CI) |

**Empirical Verdict**: The 95% confidence intervals do not overlap ([98.21%, 99.59%] vs [84.55%, 89.12%]). Bernoulli Naive Bayes outperforms tuned tree ensembles by over 12 percentage points in top-1 accuracy and achieves an order of magnitude lower log-loss. Under the pre-declared rule, Bernoulli Naive Bayes is deployed as the production model (`v2.0.0`).

### C. Out-of-Fold Calibration Evaluation
Out-of-fold calibration tests on Bernoulli Naive Bayes showed:
- Raw BernoulliNB: Out-of-fold log-loss = **0.0061**, Top-1 Accuracy = 100.0%
- Sigmoid Platt Scaling (`CalibratedClassifierCV(method='sigmoid')`): Out-of-fold log-loss = **0.1643** (severe degradation of probabilistic likelihood)
- Isotonic Regression (`CalibratedClassifierCV(method='isotonic')`): Out-of-fold log-loss = 0.0064
**Decision**: Post-hoc probability calibration was omitted because empirical evidence proved that sigmoid calibration substantially worsened probabilistic calibration on this data.

---

## 5. Explainability & Interpretability
- **Mechanism**: Exact Additive Bayesian Log-Odds Feature Attributions (Weight of Evidence).
- **Mathematical Integrity**: For each disease class $c$ and symptom $j \in \{1, \dots, M\}$:
  $$\phi_j = x_j \cdot \left(\log \theta_{c,j} - \log(1 - \theta_{c,j})\right)$$
  $$\phi_0 = \log P(c) + \sum_{j=1}^M \log(1 - \theta_{c,j})$$
  Efficiency axiom: $\sum_{j=1}^M \phi_j + \phi_0 = \log P(c, x)$ holds to machine tolerance ($< 10^{-10}$).
- **Attribution Granularity**: Computes exact mathematical contributions for every reported symptom. Symptoms with positive weight of evidence support the diagnosis; symptoms with negative weight argue against it.
- **Terminology Discipline**: Because the deployed model is linear/probabilistic and not a decision tree, feature attributions are strictly described in UI, reports, and documentation as **"Exact Bayesian Log-Odds"** or **"Bayesian Evidence Weights"** (never "TreeSHAP" or "SHAP").

---

## 6. Uncertainty Scoring, Thresholds & Automatic Escalation Rules
To ensure patient safety in rural triage, the inference service triggers `needsEscalation = True` and populates `uncertaintyReason` when safety criteria are met:
1. **Low Confidence Threshold**: Top-1 probability `< 70.0%`.
2. **Narrow Margin Threshold**: Difference between Top-1 and Top-2 differential diagnoses `< 25.0%`.
3. **High Clinical Acuity Trigger**: Any symptom with clinical severity `≥ 5` (e.g., `chest_pain`, severity 7) or presentation average severity `≥ 4.5 / 7`.
4. **Follow-Up Question Suggestions**: When diagnostic margin is narrow ($< 20\%$) or uncertainty is flagged, the service identifies the symptoms with the largest log-odds divergence between the top differential diagnoses and presents the 3–5 most informative follow-up questions.

### Out-of-Fold Threshold Coverage (Evaluated at 30% Missing Symptoms):
Under the calibrated production policy (`Confidence < 70% OR Margin < 25%`) on out-of-fold test sets at 30% symptom dropout:
- **Escalation Rate**: **5.26%** (16 out of 304 cases escalated to doctor)
- **Direct Frontline Coverage**: **94.74%** (288 out of 304 cases safely handled at frontline)
- **Direct Coverage Error Rate**: **1.39%** (4 out of 288 cases)
- **Escalated Case Error Rate**: **31.25%** (5 out of 16 cases — concentrated clinical ambiguity)
> [!NOTE]
> This resolves the previous LightGBM threshold defect, where poor calibration forced an unusable 94.08% escalation rate.

---

## 7. Limitations & Honest Clinical Appraisal
- **Synthetic Data Generative Artifacts**: The underlying benchmark is derived from static disease-symptom co-occurrence matrices. The exceptional performance of Naive Bayes directly reflects that the data generation process obeys its independence assumption. Clinical validation on real-world electronic health records (EHR) with co-morbidities and non-independent symptom clusters is essential before any field deployment.
- **Binary Symptom Indicators**: Inputs capture presence or absence but do not model symptom duration, onset velocity, physiological severity, or patient medical history.
- **No Autonomous Operation**: ArogyaMitra is strictly a decision support tool. All recommendations require verification by trained healthcare professionals.
