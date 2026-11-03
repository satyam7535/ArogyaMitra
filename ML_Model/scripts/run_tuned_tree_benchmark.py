"""
ArogyaMitra — Tuned Tree Benchmark (Nested Cross-Validation)
Runs a time-boxed hyperparameter search for LightGBM and XGBoost using inner cross-validation
strictly within training folds, then evaluates on outer validation folds across 15 splits
(5-fold x 3-repeat stratified CV) under 0%, 30%, and 50% missing symptom scenarios.
Outputs raw results to docs/evidence/tuned_tree_benchmark.csv and .md.
"""

import os
import sys
import time

import lightgbm as lgb
import numpy as np
import pandas as pd
import xgboost as xgb
from scipy import stats
from sklearn.metrics import accuracy_score, log_loss
from sklearn.model_selection import RepeatedStratifiedKFold, StratifiedKFold

# Ensure root is on path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ML_Model.training.prepare_data import augment_training_data, load_and_clean_data


def compute_ece(probs: np.ndarray, labels: np.ndarray, n_bins: int = 10) -> float:
    confidences = np.max(probs, axis=1)
    predictions = np.argmax(probs, axis=1)
    accuracies = (predictions == labels).astype(float)
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    for i in range(n_bins):
        bin_mask = (confidences > bin_boundaries[i]) & (confidences <= bin_boundaries[i+1])
        if np.any(bin_mask):
            bin_acc = np.mean(accuracies[bin_mask])
            bin_conf = np.mean(confidences[bin_mask])
            ece += np.sum(bin_mask) * np.abs(bin_acc - bin_conf)
    return float(ece / len(labels))

def top_k_accuracy(probs: np.ndarray, labels: np.ndarray, k: int = 3) -> float:
    top_k_preds = np.argsort(probs, axis=1)[:, -k:]
    hits = [labels[i] in top_k_preds[i] for i in range(len(labels))]
    return float(np.mean(hits))

def apply_symptom_dropout(X_eval: np.ndarray, dropout_rate: float, seed: int) -> np.ndarray:
    if dropout_rate <= 0.0:
        return X_eval.copy()
    rng = np.random.RandomState(seed)
    X_corrupt = X_eval.copy()
    for i in range(len(X_corrupt)):
        present_indices = np.where(X_corrupt[i] == 1)[0]
        if len(present_indices) > 1:
            n_drop = int(np.ceil(len(present_indices) * dropout_rate))
            n_drop = min(n_drop, len(present_indices) - 1)
            drop_indices = rng.choice(present_indices, size=n_drop, replace=False)
            X_corrupt[i, drop_indices] = 0
    return X_corrupt

def tune_lightgbm_inner(X_train: np.ndarray, y_train: np.ndarray, seed: int) -> dict:
    """Inner 3-fold CV tuning for LightGBM on augmented fold."""
    param_grid = [
        {"n_estimators": 60, "learning_rate": 0.05, "num_leaves": 15, "min_child_samples": 1},
        {"n_estimators": 80, "learning_rate": 0.08, "num_leaves": 15, "min_child_samples": 2},
        {"n_estimators": 100, "learning_rate": 0.05, "num_leaves": 31, "min_child_samples": 2},
        {"n_estimators": 120, "learning_rate": 0.03, "num_leaves": 31, "min_child_samples": 1},
        {"n_estimators": 80, "learning_rate": 0.10, "num_leaves": 7, "min_child_samples": 1},
    ]
    inner_cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=seed)
    best_score = float("inf")
    best_params = param_grid[0]

    for p in param_grid:
        fold_scores = []
        for in_tr, in_val in inner_cv.split(X_train, y_train):
            # Augment inner training fold
            X_in_aug, y_in_aug = augment_training_data(
                X_train[in_tr], y_train[in_tr], min_dropout=0.0, max_dropout=0.5, copies_per_sample=2, random_state=seed
            )
            clf = lgb.LGBMClassifier(**p, random_state=seed, n_jobs=1, verbose=-1)
            clf.fit(X_in_aug, y_in_aug)
            preds = clf.predict_proba(X_train[in_val])
            score = log_loss(y_train[in_val], preds, labels=np.arange(41))
            fold_scores.append(score)
        avg_score = float(np.mean(fold_scores))
        if avg_score < best_score:
            best_score = avg_score
            best_params = p
    return best_params

def tune_xgboost_inner(X_train: np.ndarray, y_train: np.ndarray, seed: int) -> dict:
    """Inner 3-fold CV tuning for XGBoost on augmented fold."""
    param_grid = [
        {"n_estimators": 60, "learning_rate": 0.05, "max_depth": 3, "subsample": 0.8},
        {"n_estimators": 80, "learning_rate": 0.08, "max_depth": 4, "subsample": 0.8},
        {"n_estimators": 100, "learning_rate": 0.05, "max_depth": 5, "subsample": 1.0},
        {"n_estimators": 120, "learning_rate": 0.03, "max_depth": 3, "subsample": 0.9},
    ]
    inner_cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=seed)
    best_score = float("inf")
    best_params = param_grid[0]

    for p in param_grid:
        fold_scores = []
        for in_tr, in_val in inner_cv.split(X_train, y_train):
            X_in_aug, y_in_aug = augment_training_data(
                X_train[in_tr], y_train[in_tr], min_dropout=0.0, max_dropout=0.5, copies_per_sample=2, random_state=seed
            )
            clf = xgb.XGBClassifier(**p, random_state=seed, n_jobs=1, eval_metric="mlogloss", verbosity=0)
            clf.fit(X_in_aug, y_in_aug)
            preds = clf.predict_proba(X_train[in_val])
            score = log_loss(y_train[in_val], preds, labels=np.arange(41))
            fold_scores.append(score)
        avg_score = float(np.mean(fold_scores))
        if avg_score < best_score:
            best_score = avg_score
            best_params = p
    return best_params

def run_tuned_benchmark():
    start_time = time.time()
    print("=" * 80)
    print("AROGYAMITRA — TUNED TREE BENCHMARK (NESTED CV FOR LIGHTGBM & XGBOOST)")
    print("=" * 80)

    data_path = os.path.join(BASE_DIR, "ML_Model", "dataset", "Training.csv")
    data = load_and_clean_data(data_path, deduplicate=True)
    X, y = data["X"], data["y"]
    num_classes = len(np.unique(y))

    outer_cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=3, random_state=42)
    dropout_levels = [0.0, 0.30, 0.50]
    records = []

    total_splits = 15

    for split_idx, (tr_idx, val_idx) in enumerate(outer_cv.split(X, y), 1):
        X_tr, y_tr = X[tr_idx], y[tr_idx]
        X_val, y_val = X[val_idx], y[val_idx]

        # 1. Inner tuning for LightGBM
        best_lgb_p = tune_lightgbm_inner(X_tr, y_tr, seed=42 + split_idx)
        # 2. Inner tuning for XGBoost
        best_xgb_p = tune_xgboost_inner(X_tr, y_tr, seed=42 + split_idx)

        # In-fold augmentation for outer training fold
        X_tr_aug, y_tr_aug = augment_training_data(
            X_tr, y_tr, min_dropout=0.0, max_dropout=0.5, copies_per_sample=3, random_state=42 + split_idx
        )

        # Fit tuned LightGBM
        clf_lgb = lgb.LGBMClassifier(**best_lgb_p, random_state=42 + split_idx, n_jobs=1, verbose=-1)
        clf_lgb.fit(X_tr_aug, y_tr_aug)

        # Fit tuned XGBoost
        clf_xgb = xgb.XGBClassifier(**best_xgb_p, random_state=42 + split_idx, n_jobs=1, eval_metric="mlogloss", verbosity=0)
        clf_xgb.fit(X_tr_aug, y_tr_aug)

        for d in dropout_levels:
            X_val_drop = apply_symptom_dropout(X_val, dropout_rate=d, seed=42 + split_idx)

            for name, model in [("LightGBM (Tuned Inner-CV)", clf_lgb), ("XGBoost (Tuned Inner-CV)", clf_xgb)]:
                probs = model.predict_proba(X_val_drop)
                preds = np.argmax(probs, axis=1)

                acc = float(accuracy_score(y_val, preds))
                top3 = float(top_k_accuracy(probs, y_val, k=3))
                ll = float(log_loss(y_val, probs, labels=np.arange(num_classes)))
                ece = float(compute_ece(probs, y_val))

                records.append({
                    "Split": split_idx,
                    "Model": name,
                    "Dropout": int(d * 100),
                    "Top1_Accuracy": acc,
                    "Top3_Accuracy": top3,
                    "Log_Loss": ll,
                    "ECE": ece
                })

        print(f"  - Completed outer split {split_idx}/{total_splits}...")

    df_results = pd.DataFrame(records)
    elapsed = time.time() - start_time
    print(f"Benchmark completed in {elapsed:.2f} seconds.")

    # Save raw CSV
    csv_path = os.path.join(BASE_DIR, "docs", "evidence", "tuned_tree_benchmark.csv")
    df_results.to_csv(csv_path, index=False)
    print(f"[+] Saved raw results to: {csv_path}")

    # Compute aggregation
    summary_rows = []
    for (model, d), group in df_results.groupby(["Model", "Dropout"]):
        n = len(group)
        t_crit = stats.t.ppf(0.975, df=n - 1)

        def get_ci(series, sample_n, crit):
            m = np.mean(series)
            s = np.std(series, ddof=1)
            ci_half = crit * (s / np.sqrt(sample_n))
            return m, s, m - ci_half, m + ci_half

        top1_m, top1_s, top1_low, top1_high = get_ci(group["Top1_Accuracy"], n, t_crit)
        top3_m, top3_s, top3_low, top3_high = get_ci(group["Top3_Accuracy"], n, t_crit)
        ll_m, ll_s, ll_low, ll_high = get_ci(group["Log_Loss"], n, t_crit)
        ece_m, ece_s, ece_low, ece_high = get_ci(group["ECE"], n, t_crit)

        summary_rows.append({
            "Model": model,
            "Dropout (%)": d,
            "Top-1 Accuracy": f"{top1_m:.4f} ± {top1_s:.4f} [{top1_low:.4f}, {top1_high:.4f}]",
            "Top-3 Accuracy": f"{top3_m:.4f} ± {top3_s:.4f} [{top3_low:.4f}, {top3_high:.4f}]",
            "Log-Loss": f"{ll_m:.4f} ± {ll_s:.4f} [{ll_low:.4f}, {ll_high:.4f}]",
            "ECE": f"{ece_m:.4f} ± {ece_s:.4f} [{ece_low:.4f}, {ece_high:.4f}]",
            "Raw_Top1": top1_m,
            "Raw_LL": ll_m,
        })

    df_summary = pd.DataFrame(summary_rows)
    md_path = os.path.join(BASE_DIR, "docs", "evidence", "tuned_tree_benchmark.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# ArogyaMitra — Tuned Tree Benchmark (Nested Cross-Validation)\n\n")
        f.write("**Command**: `python ML_Model/scripts/run_tuned_tree_benchmark.py`\n")
        f.write("**Outer Protocol**: Repeated Stratified K-Fold (5 folds x 3 repeats = 15 splits)\n")
        f.write("**Inner Protocol**: Stratified 3-Fold CV per training fold for hyperparameter selection\n")
        f.write("**Dataset**: 304 unique ground truth rows across 41 classes (4,616 duplicates dropped)\n\n")

        f.write("## Tuned Results Summary (Mean ± Std [95% CI])\n\n")
        cols = ["Model", "Dropout (%)", "Top-1 Accuracy", "Top-3 Accuracy", "Log-Loss", "ECE"]
        f.write("| " + " | ".join(cols) + " |\n")
        f.write("|" + "|".join([":---:" for _ in cols]) + "|\n")
        f.writelines(f"| {r['Model']} | {r['Dropout (%)']} | {r['Top-1 Accuracy']} | {r['Top-3 Accuracy']} | {r['Log-Loss']} | {r['ECE']} |\n" for _, r in df_summary.iterrows())
        f.write("\n")

    print(f"[+] Saved formatted report to: {md_path}")

if __name__ == "__main__":
    run_tuned_benchmark()

