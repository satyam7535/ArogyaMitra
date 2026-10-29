# ArogyaMitra — Empirical Decision Thresholds & Clinical Coverage Report

**Command**: `python ML_Model/scripts/evaluate_thresholds.py`
**Model Evaluated**: Bernoulli Naive Bayes (`v2.0.0`)
**Condition**: Out-of-fold cross-validation under 30% realistic symptom omission (304 unique ground truth presentations)

## 1. Primary Policy: Uncertainty Escalation Matrix

| Policy | Total Cases | Escalated Cases | Escalation Rate | Direct Coverage | Error Rate (Direct) | Error Rate (Escalated) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| `Confidence < 70% OR Margin < 25%` | 304 | 16 | **5.26%** | **94.74%** | **1.39%** | 31.25% |

## 2. Confidence Threshold Sensitivity Analysis

| Confidence Threshold (%) | Escalation Rate (%) | Direct Treatment Coverage (%) | Error Rate (Direct Cases) (%) | Error Rate (Escalated Cases) (%) |
|:---:|:---:|:---:|:---:|:---:|
| 50.0 | 0.99 | 99.01 | 2.33 | 66.67 |
| 60.0 | 2.63 | 97.37 | 2.03 | 37.5 |
| 70.0 | 5.26 | 94.74 | 1.39 | 31.25 |
| 80.0 | 9.21 | 90.79 | 1.09 | 21.43 |
| 90.0 | 17.76 | 82.24 | 0.0 | 16.67 |

## 3. Differential Margin Threshold Sensitivity Analysis

| Margin Threshold (%) | Escalation Rate (%) | Direct Treatment Coverage (%) | Error Rate (Direct Cases) (%) | Error Rate (Escalated Cases) (%) |
|:---:|:---:|:---:|:---:|:---:|
| 10.0 | 1.32 | 98.68 | 2.0 | 75.0 |
| 15.0 | 1.32 | 98.68 | 2.0 | 75.0 |
| 20.0 | 2.3 | 97.7 | 2.02 | 42.86 |
| 25.0 | 2.3 | 97.7 | 2.02 | 42.86 |
| 30.0 | 2.96 | 97.04 | 2.03 | 33.33 |

## 4. Key Clinical Safety Insight

- Under the production threshold (`Confidence < 70% OR Margin < 25%`), **94.74% of patient presentations receive direct frontline guidance**, while **5.26% are safely escalated to a physician**.
- The error rate in the un-escalated cohort is only **1.39%**, while the error rate in the escalated cohort is **31.25%**, demonstrating effective triage isolation without overwhelming physician workload.
