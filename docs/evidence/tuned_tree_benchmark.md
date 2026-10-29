# ArogyaMitra — Tuned Tree Benchmark (Nested Cross-Validation)

**Command**: `python ML_Model/scripts/run_tuned_tree_benchmark.py`
**Outer Protocol**: Repeated Stratified K-Fold (5 folds x 3 repeats = 15 splits)
**Inner Protocol**: Stratified 3-Fold CV per training fold for hyperparameter selection
**Dataset**: 304 unique ground truth rows across 41 classes (4,616 duplicates dropped)

## Tuned Results Summary (Mean ± Std [95% CI])

| Model | Dropout (%) | Top-1 Accuracy | Top-3 Accuracy | Log-Loss | ECE |
|:---:|:---:|:---:|:---:|:---:|:---:|
| LightGBM (Tuned Inner-CV) | 0 | 0.9890 ± 0.0119 [0.9824, 0.9956] | 0.9945 ± 0.0080 [0.9901, 0.9990] | 0.0656 ± 0.0720 [0.0258, 0.1055] | 0.0098 ± 0.0079 [0.0054, 0.0142] |
| LightGBM (Tuned Inner-CV) | 30 | 0.8640 ± 0.0399 [0.8419, 0.8860] | 0.9440 ± 0.0341 [0.9252, 0.9629] | 0.7140 ± 0.2789 [0.5596, 0.8685] | 0.0975 ± 0.0370 [0.0770, 0.1180] |
| LightGBM (Tuned Inner-CV) | 50 | 0.6830 ± 0.0783 [0.6397, 0.7264] | 0.8256 ± 0.0652 [0.7895, 0.8617] | 1.7157 ± 0.5034 [1.4369, 1.9945] | 0.2019 ± 0.0508 [0.1737, 0.2300] |
| XGBoost (Tuned Inner-CV) | 0 | 0.9836 ± 0.0139 [0.9759, 0.9912] | 0.9934 ± 0.0104 [0.9877, 0.9992] | 0.1433 ± 0.0367 [0.1230, 0.1636] | 0.0826 ± 0.0129 [0.0755, 0.0898] |
| XGBoost (Tuned Inner-CV) | 30 | 0.8683 ± 0.0413 [0.8455, 0.8912] | 0.9715 ± 0.0201 [0.9604, 0.9826] | 0.6463 ± 0.1217 [0.5789, 0.7137] | 0.1983 ± 0.0346 [0.1792, 0.2175] |
| XGBoost (Tuned Inner-CV) | 50 | 0.7203 ± 0.0773 [0.6775, 0.7631] | 0.8969 ± 0.0549 [0.8665, 0.9273] | 1.2161 ± 0.2235 [1.0924, 1.3399] | 0.2118 ± 0.0474 [0.1856, 0.2381] |

