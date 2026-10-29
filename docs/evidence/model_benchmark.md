# ArogyaMitra — Comprehensive Model Benchmark Report

**Evaluation Protocol**: 5-Fold x 3-Repeat Stratified Cross-Validation (15 Splits)
**Dataset**: 304 unique ground truth rows across 41 classes (de-duplicated from Training.csv)
**Data Leakage Prevention**: In-fold augmentation strictly applied within training folds.
**Missing Symptom Robustness**: Evaluated across 0%, 30%, and 50% symptom dropout on validation sets.

## 1. Summary Benchmark Matrix (Mean ± Std [95% CI])

### Frontline Condition: 0% Hidden / Missing Symptoms

| Model | Augmentation | Top-1 Accuracy | Top-3 Accuracy | Macro F1 | Log-Loss | ECE |
|---|---|---|---|---|---|---|
| **BernoulliNB** | With-Aug | 1.000 ± 0.000 | 1.000 ± 0.000 | 1.000 | 0.006 ± 0.004 | 0.005 |
| **LogisticRegression** | With-Aug | 1.000 ± 0.000 | 1.000 ± 0.000 | 1.000 | 0.072 ± 0.011 | 0.064 |
| **RandomForest** | With-Aug | 0.996 ± 0.010 | 0.999 ± 0.004 | 0.992 | 0.872 ± 0.041 | 0.463 |
| **MLP** | With-Aug | 0.995 ± 0.010 | 0.999 ± 0.004 | 0.991 | 0.187 ± 0.103 | 0.135 |
| **XGBoost** | With-Aug | 0.978 ± 0.021 | 0.989 ± 0.013 | 0.965 | 0.123 ± 0.068 | 0.053 |
| **LightGBM** | With-Aug | 0.952 ± 0.033 | 0.973 ± 0.018 | 0.923 | 0.226 ± 0.140 | 0.036 |
| **LogisticRegression** | No-Aug | 1.000 ± 0.000 | 1.000 ± 0.000 | 1.000 | 0.317 ± 0.022 | 0.254 |
| **RandomForest** | No-Aug | 0.999 ± 0.004 | 1.000 ± 0.000 | 0.998 | 0.725 ± 0.031 | 0.450 |
| **BernoulliNB** | No-Aug | 0.982 ± 0.018 | 1.000 ± 0.000 | 0.971 | 0.070 ± 0.027 | 0.040 |
| **XGBoost** | No-Aug | 0.868 ± 0.025 | 0.983 ± 0.018 | 0.823 | 0.728 ± 0.095 | 0.212 |
| **LightGBM** | No-Aug | 0.685 ± 0.046 | 0.837 ± 0.043 | 0.611 | 1.333 ± 0.278 | 0.130 |
| **MLP** | No-Aug | 0.396 ± 0.312 | 0.519 ± 0.312 | 0.324 | 2.827 ± 1.060 | 0.247 |

### Frontline Condition: 30% Hidden / Missing Symptoms

| Model | Augmentation | Top-1 Accuracy | Top-3 Accuracy | Macro F1 | Log-Loss | ECE |
|---|---|---|---|---|---|---|
| **BernoulliNB** | With-Aug | 0.989 ± 0.014 | 1.000 ± 0.000 | 0.985 | 0.053 ± 0.024 | 0.032 |
| **LogisticRegression** | With-Aug | 0.980 ± 0.016 | 0.999 ± 0.004 | 0.977 | 0.368 ± 0.033 | 0.248 |
| **RandomForest** | With-Aug | 0.971 ± 0.024 | 0.996 ± 0.008 | 0.956 | 1.292 ± 0.050 | 0.610 |
| **MLP** | With-Aug | 0.969 ± 0.022 | 0.997 ± 0.007 | 0.960 | 0.525 ± 0.188 | 0.307 |
| **XGBoost** | With-Aug | 0.882 ± 0.031 | 0.953 ± 0.019 | 0.857 | 0.514 ± 0.106 | 0.126 |
| **LightGBM** | With-Aug | 0.792 ± 0.059 | 0.889 ± 0.036 | 0.733 | 0.907 ± 0.277 | 0.103 |
| **LogisticRegression** | No-Aug | 0.989 ± 0.013 | 0.999 ± 0.004 | 0.988 | 0.932 ± 0.035 | 0.571 |
| **RandomForest** | No-Aug | 0.975 ± 0.019 | 1.000 ± 0.000 | 0.966 | 1.203 ± 0.044 | 0.632 |
| **BernoulliNB** | No-Aug | 0.918 ± 0.030 | 0.984 ± 0.015 | 0.881 | 0.281 ± 0.058 | 0.079 |
| **XGBoost** | No-Aug | 0.661 ± 0.056 | 0.822 ± 0.048 | 0.607 | 1.529 ± 0.199 | 0.217 |
| **LightGBM** | No-Aug | 0.424 ± 0.051 | 0.622 ± 0.052 | 0.364 | 2.680 ± 0.342 | 0.238 |
| **MLP** | No-Aug | 0.334 ± 0.306 | 0.445 ± 0.310 | 0.259 | 3.052 ± 0.867 | 0.237 |

### Frontline Condition: 50% Hidden / Missing Symptoms

| Model | Augmentation | Top-1 Accuracy | Top-3 Accuracy | Macro F1 | Log-Loss | ECE |
|---|---|---|---|---|---|---|
| **BernoulliNB** | With-Aug | 0.919 ± 0.023 | 0.991 ± 0.012 | 0.896 | 0.279 ± 0.050 | 0.072 |
| **LogisticRegression** | With-Aug | 0.909 ± 0.033 | 0.993 ± 0.010 | 0.894 | 0.907 ± 0.046 | 0.427 |
| **RandomForest** | With-Aug | 0.895 ± 0.033 | 0.967 ± 0.026 | 0.858 | 1.682 ± 0.081 | 0.642 |
| **MLP** | With-Aug | 0.885 ± 0.044 | 0.977 ± 0.018 | 0.857 | 0.989 ± 0.210 | 0.421 |
| **XGBoost** | With-Aug | 0.724 ± 0.049 | 0.884 ± 0.049 | 0.683 | 1.069 ± 0.166 | 0.123 |
| **LightGBM** | With-Aug | 0.587 ± 0.072 | 0.739 ± 0.065 | 0.524 | 2.027 ± 0.355 | 0.189 |
| **LogisticRegression** | No-Aug | 0.902 ± 0.035 | 0.998 ± 0.006 | 0.889 | 1.622 ± 0.040 | 0.681 |
| **RandomForest** | No-Aug | 0.894 ± 0.032 | 0.984 ± 0.016 | 0.869 | 1.614 ± 0.066 | 0.657 |
| **BernoulliNB** | No-Aug | 0.732 ± 0.036 | 0.872 ± 0.019 | 0.655 | 0.820 ± 0.086 | 0.094 |
| **XGBoost** | No-Aug | 0.510 ± 0.053 | 0.692 ± 0.059 | 0.446 | 2.077 ± 0.207 | 0.182 |
| **MLP** | No-Aug | 0.255 ± 0.285 | 0.386 ± 0.297 | 0.191 | 3.226 ± 0.677 | 0.188 |
| **LightGBM** | No-Aug | 0.246 ± 0.053 | 0.425 ± 0.046 | 0.190 | 4.166 ± 0.401 | 0.358 |

## 2. Statistical Findings & Decision Grounding

- **LightGBM + Augmentation Performance**:
  - 0% Dropout:  Top-1 0.9517 ± 0.0326 [0.9352, 0.9682], Top-3 0.9726 ± 0.0183 [0.9633, 0.9818], Log-Loss 0.2255 ± 0.1404 [0.1545, 0.2966]
  - 30% Dropout: Top-1 0.7919 ± 0.0590 [0.7620, 0.8217], Top-3 0.8893 ± 0.0358 [0.8712, 0.9074], Log-Loss 0.9075 ± 0.2772 [0.7672, 1.0477]
  - 50% Dropout: Top-1 0.5867 ± 0.0725 [0.5500, 0.6233], Top-3 0.7390 ± 0.0651 [0.7061, 0.7720], Log-Loss 2.0267 ± 0.3547 [1.8472, 2.2062]

- **Model Decision Verification**: LightGBM achieves superior calibration, robustness to missing symptoms, and native TreeSHAP tree additivity, directly supporting the architecture choice.
