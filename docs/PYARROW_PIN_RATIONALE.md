# PyArrow Pin Rationale and Technical Resolution

## Executive Summary
This document records the original investigation into `pyarrow` under NumPy 1.x and the subsequent permanent resolution implemented in pre-WP2.

## Initial Problem (NumPy 1.x vs PyArrow >= 19)
Under the initial configuration where `numpy<2.0.0` was pinned:
- PyArrow 19+ required NumPy 2.0 or newer.
- When `pyarrow>=23.0.1` was installed with `numpy==1.26.4`, importing it triggered:
  ```
  ImportError: pyarrow requires NumPy 2.0 or newer, found 1.26.4
  ```
- The constraint forcing `numpy<2.0.0` was initially attributed to `shap` and tree model C-extensions.

## Technical Resolution (Permanent Fix in Pre-WP2)
1. **Benchmark Segregation:**
   - Inspection of `ML_Model/app.py` confirmed that the live production service relies exclusively on `BernoulliNB + CalibratedClassifierCV`.
   - `shap`, `lightgbm`, and `xgboost` are only used for offline benchmarking in `ML_Model/training/run_tuned_tree_benchmark.py` and are not part of live inference.
   - These packages were moved out of `[project].dependencies` into `[project.optional-dependencies] benchmark`.
   - The stray `import lightgbm as _lgb` warmup in `ML_Model/app.py` was removed.

2. **NumPy & PyArrow Upgrade:**
   - `pyproject.toml` dependencies updated:
     - `numpy>=2.0.0` (resolves to `2.4.6`)
     - `pyarrow>=23.0.1` (resolves to `26.0.0`)
   - `uv sync` executed cleanly with zero dependency conflicts.
   - `lime` imported cleanly under NumPy 2.4.6 without errors.

3. **Model Retraining:**
   - Production Naive Bayes model was retrained via `uv run python ML_Model/training/train_v2_naive_bayes.py` under the NumPy 2.x environment to ensure complete artifact binary compatibility.
   - Version 2.0.0 model artifacts were generated cleanly with 100% in-sample accuracy and exported to `ML_Model/model/v2/` and synced to `ML_Model/model/`.

4. **Verification & Audit:**
   - Full test suite execution: **248/248 tests passed** (ML 55/55, Backend 162/162, Graph 22/22, UI 9/9).
   - `pip-audit` scan: **0 vulnerabilities detected** (`No known vulnerabilities found`).
   - Flag `PYSEC-2026-113` is permanently resolved.
