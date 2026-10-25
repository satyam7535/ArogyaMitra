# ArogyaMitra v1 — Model Diagnostic and Calibration Report

- **Total Unique Ground-Truth Samples**: 304
- **Classes Evaluated**: 41
- **Calibrated ECE**: 0.4900 (vs Uncalibrated ECE: 0.0000)
- **Multi-class Brier Score**: 0.2483

## 1. Reliability & Calibration Bins

| Confidence Bin | Sample Count | Mean Confidence | Empirical Accuracy |
|---|:---:|:---:|:---:|
| (0.2, 0.3] | 2 | 0.2804 | 1.0000 |
| (0.3, 0.4] | 11 | 0.3463 | 1.0000 |
| (0.4, 0.5] | 33 | 0.4620 | 1.0000 |
| (0.5, 0.6] | 258 | 0.5249 | 1.0000 |

## 2. Robustness Under Symptom Omission (Masking)

| Mask Rate (% Symptoms Hidden) | Top-1 Accuracy (%) | Top-3 Accuracy (%) | ECE |
|---|:---:|:---:|:---:|
| 0% | 100.0% | 100.0% | 0.49 |
| 20% | 97.04% | 99.34% | 0.5162 |
| 40% | 82.24% | 93.75% | 0.4599 |
| 60% | 59.87% | 77.3% | 0.3277 |

## 3. Per-Class Precision, Recall, and F1-Score

| Disease Class | Precision | Recall | F1-Score | Support |
|---|:---:|:---:|:---:|:---:|
| (vertigo) Paroymsal  Positional Vertigo | 1.000 | 1.000 | 1.000 | 7 |
| AIDS | 1.000 | 1.000 | 1.000 | 5 |
| Acne | 1.000 | 1.000 | 1.000 | 5 |
| Alcoholic hepatitis | 1.000 | 1.000 | 1.000 | 8 |
| Allergy | 1.000 | 1.000 | 1.000 | 5 |
| Arthritis | 1.000 | 1.000 | 1.000 | 6 |
| Bronchial Asthma | 1.000 | 1.000 | 1.000 | 7 |
| Cervical spondylosis | 1.000 | 1.000 | 1.000 | 6 |
| Chicken pox | 1.000 | 1.000 | 1.000 | 10 |
| Chronic cholestasis | 1.000 | 1.000 | 1.000 | 8 |
| Common Cold | 1.000 | 1.000 | 1.000 | 9 |
| Dengue | 1.000 | 1.000 | 1.000 | 10 |
| Diabetes | 1.000 | 1.000 | 1.000 | 9 |
| Dimorphic hemorrhoids(piles) | 1.000 | 1.000 | 1.000 | 6 |
| Drug Reaction | 1.000 | 1.000 | 1.000 | 6 |
| Fungal infection | 1.000 | 1.000 | 1.000 | 5 |
| GERD | 1.000 | 1.000 | 1.000 | 7 |
| Gastroenteritis | 1.000 | 1.000 | 1.000 | 5 |
| Heart attack | 1.000 | 1.000 | 1.000 | 5 |
| Hepatitis B | 1.000 | 1.000 | 1.000 | 9 |
| Hepatitis C | 1.000 | 1.000 | 1.000 | 7 |
| Hepatitis D | 1.000 | 1.000 | 1.000 | 10 |
| Hepatitis E | 1.000 | 1.000 | 1.000 | 9 |
| Hypertension | 1.000 | 1.000 | 1.000 | 6 |
| Hyperthyroidism | 1.000 | 1.000 | 1.000 | 9 |
| Hypoglycemia | 1.000 | 1.000 | 1.000 | 9 |
| Hypothyroidism | 1.000 | 1.000 | 1.000 | 8 |
| Impetigo | 1.000 | 1.000 | 1.000 | 6 |
| Jaundice | 1.000 | 1.000 | 1.000 | 9 |
| Malaria | 1.000 | 1.000 | 1.000 | 8 |
| Migraine | 1.000 | 1.000 | 1.000 | 10 |
| Osteoarthristis | 1.000 | 1.000 | 1.000 | 7 |
| Paralysis (brain hemorrhage) | 1.000 | 1.000 | 1.000 | 5 |
| Peptic ulcer diseae | 1.000 | 1.000 | 1.000 | 7 |
| Pneumonia | 1.000 | 1.000 | 1.000 | 9 |
| Psoriasis | 1.000 | 1.000 | 1.000 | 7 |
| Tuberculosis | 1.000 | 1.000 | 1.000 | 9 |
| Typhoid | 1.000 | 1.000 | 1.000 | 9 |
| Urinary tract infection | 1.000 | 1.000 | 1.000 | 5 |
| Varicose veins | 1.000 | 1.000 | 1.000 | 8 |
| hepatitis A | 1.000 | 1.000 | 1.000 | 9 |
| **Macro Average** | **1.000** | **1.000** | **1.000** | **304** |
