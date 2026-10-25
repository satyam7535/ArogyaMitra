"""
ArogyaMitra — Final Model Training, Calibration & Artifact Export
Tunes LightGBM with Optuna, trains on augmented deduplicated dataset,
calibrates probabilities with CalibratedClassifierCV, fits TreeSHAP explainer,
and exports versioned artifacts to ML_Model/model/v1/.
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime
from typing import Dict, Any

os.environ["TEMP"] = r"D:\temp"
os.environ["TMP"] = r"D:\temp"
os.environ["UV_CACHE_DIR"] = r"D:\.uv_cache"

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

import yaml
import joblib
import optuna
import shap
import numpy as np
import pandas as pd
from lightgbm import LGBMClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import accuracy_score, log_loss, f1_score

# Ensure root is on sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ML_Model.training.prepare_data import load_and_clean_data, augment_training_data

def get_git_commit_hash() -> str:
    try:
        res = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except Exception:
        return "unknown"

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

def optimize_lightgbm(X: np.ndarray, y: np.ndarray, n_trials: int = 25, seed: int = 42) -> Dict[str, Any]:
    print(f"[OPTUNA] Beginning Bayesian hyperparameter search ({n_trials} trials)...")
    optuna.logging.set_verbosity(optuna.logging.WARNING)

    skf = StratifiedKFold(n_splits=3, shuffle=True, random_state=seed)

    def objective(trial: optuna.Trial) -> float:
        params = {
            "n_estimators": trial.suggest_int("n_estimators", 40, 200),
            "max_depth": trial.suggest_int("max_depth", 3, 9),
            "num_leaves": trial.suggest_int("num_leaves", 15, 63),
            "learning_rate": trial.suggest_float("learning_rate", 0.02, 0.25, log=True),
            "min_child_samples": trial.suggest_int("min_child_samples", 2, 15),
            "subsample": trial.suggest_float("subsample", 0.6, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
            "random_state": seed,
            "verbose": -1,
            "n_jobs": 1
        }
        scores = []
        for tr_idx, val_idx in skf.split(X, y):
            X_tr, y_tr = X[tr_idx], y[tr_idx]
            X_val, y_val = X[val_idx], y[val_idx]
            # Augment training fold
            X_tr_aug, y_tr_aug = augment_training_data(X_tr, y_tr, min_dropout=0.0, max_dropout=0.5, copies_per_sample=3, random_state=seed)
            clf = LGBMClassifier(**params)
            clf.fit(X_tr_aug, y_tr_aug)
            preds = clf.predict_proba(X_val)
            scores.append(log_loss(y_val, preds, labels=np.arange(len(np.unique(y)))))
        return float(np.mean(scores))

    study = optuna.create_study(direction="minimize", sampler=optuna.samplers.TPESampler(seed=seed))
    study.optimize(objective, n_trials=n_trials)
    print(f"[OPTUNA] Best Trial Score (LogLoss): {study.best_value:.4f}")
    print(f"[OPTUNA] Best Params: {study.best_params}")
    return study.best_params

def train_and_export_v1():
    print("=" * 60)
    print("ArogyaMitra — Training Production Model (v1)")
    print("=" * 60)

    config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    data_dir = os.path.join(BASE_DIR, "ML_Model", "dataset")
    data = load_and_clean_data(
        training_path=os.path.join(data_dir, "Training.csv"),
        severity_path=os.path.join(data_dir, "Symptom-severity.csv"),
        desc_path=os.path.join(data_dir, "symptom_Description.csv"),
        prec_path=os.path.join(data_dir, "symptom_precaution.csv"),
        deduplicate=True
    )

    X_clean, y_clean = data["X"], data["y"]
    feature_names = data["feature_names"]
    label_encoder = data["label_encoder"]
    num_classes = len(label_encoder.classes_)
    seed = cfg["seed"]

    print(f"[DATA] Clean unique samples: {len(X_clean)} across {num_classes} classes and {len(feature_names)} features.")

    # 1. Hyperparameter tuning
    best_params = optimize_lightgbm(X_clean, y_clean, n_trials=cfg["optuna"]["n_trials"], seed=seed)
    best_params["random_state"] = seed
    best_params["verbose"] = -1
    best_params["n_jobs"] = 1

    # 2. Augment full dataset for final training
    print("[AUGMENT] Generating symptom-dropout augmented training set...")
    X_aug, y_aug = augment_training_data(
        X_clean, y_clean,
        min_dropout=cfg["augmentation"]["min_dropout"],
        max_dropout=cfg["augmentation"]["max_dropout"],
        copies_per_sample=cfg["augmentation"].get("copies_per_sample", 3),
        random_state=seed
    )
    print(f"[AUGMENT] Augmented training dataset size: {len(X_aug)} rows (from {len(X_clean)} unique ground-truth rows).")

    # 3. Fit base LightGBM model
    print("[FIT] Fitting final LightGBM model...")
    base_model = LGBMClassifier(**best_params)
    base_model.fit(X_aug, y_aug)

    # 4. Fit Calibrator
    print("[CALIBRATE] Fitting CalibratedClassifierCV (isotonic / sigmoid) on training data...")
    # Using 5-fold cross-validation inside CalibratedClassifierCV
    calibrated_model = CalibratedClassifierCV(
        estimator=base_model,
        method="sigmoid",
        cv=5
    )
    calibrated_model.fit(X_clean, y_clean)

    # Evaluate calibration on ground truth unique samples
    cal_probs = calibrated_model.predict_proba(X_clean)
    cal_preds = np.argmax(cal_probs, axis=1)
    ece_val = compute_ece(cal_probs, y_clean)
    log_loss_val = log_loss(y_clean, cal_probs, labels=np.arange(num_classes))
    acc_val = accuracy_score(y_clean, cal_preds)
    f1_val = f1_score(y_clean, cal_preds, average="macro")

    print(f"[METRICS] Calibrated Model on Clean Ground Truth:")
    print(f"  Accuracy: {acc_val*100:.2f}%")
    print(f"  Macro-F1: {f1_val:.4f}")
    print(f"  Log Loss: {log_loss_val:.4f}")
    print(f"  ECE:      {ece_val:.4f}")

    # 5. Build TreeSHAP explainer
    print("[SHAP] Initializing TreeSHAP explainer...")
    shap_explainer = shap.TreeExplainer(base_model)

    # 6. Export artifacts to ML_Model/model/v1/
    v1_dir = os.path.join(BASE_DIR, "ML_Model", "model", "v1")
    os.makedirs(v1_dir, exist_ok=True)

    print(f"[EXPORT] Saving artifacts to: {v1_dir}")
    joblib.dump(base_model, os.path.join(v1_dir, "disease_model.pkl"))
    joblib.dump(calibrated_model, os.path.join(v1_dir, "calibrator.pkl"))
    joblib.dump(shap_explainer, os.path.join(v1_dir, "shap_explainer.pkl"))
    joblib.dump(label_encoder, os.path.join(v1_dir, "label_encoder.pkl"))
    joblib.dump(feature_names, os.path.join(v1_dir, "symptom_columns.pkl"))
    joblib.dump(data["severity_map"], os.path.join(v1_dir, "severity_map.pkl"))
    joblib.dump(data["description_map"], os.path.join(v1_dir, "description_map.pkl"))
    joblib.dump(data["precaution_map"], os.path.join(v1_dir, "precaution_map.pkl"))

    # Also sync root model/ directory
    root_model_dir = os.path.join(BASE_DIR, "ML_Model", "model")
    for f_name in ["disease_model.pkl", "calibrator.pkl", "shap_explainer.pkl", "label_encoder.pkl",
                   "symptom_columns.pkl", "severity_map.pkl", "description_map.pkl", "precaution_map.pkl"]:
        joblib.dump(joblib.load(os.path.join(v1_dir, f_name)), os.path.join(root_model_dir, f_name))

    # Metadata JSON
    metadata = {
        "model_version": "v1.0.0",
        "model_family": "LightGBM + CalibratedClassifierCV (sigmoid) + TreeSHAP",
        "training_timestamp": datetime.utcnow().isoformat() + "Z",
        "git_commit": get_git_commit_hash(),
        "dataset": {
            "initial_rows": data["stats"]["initial_rows"],
            "unique_rows": data["stats"]["unique_rows"],
            "duplicate_rows_dropped": data["stats"]["duplicate_rows_dropped"],
            "num_features": len(feature_names),
            "num_classes": num_classes
        },
        "best_hyperparameters": best_params,
        "metrics_on_unique_ground_truth": {
            "accuracy": round(float(acc_val), 4),
            "macro_f1": round(float(f1_val), 4),
            "log_loss": round(float(log_loss_val), 4),
            "expected_calibration_error": round(float(ece_val), 4)
        },
        "augmentation_policy": {
            "technique": "symptom_dropout",
            "min_dropout": cfg["augmentation"]["min_dropout"],
            "max_dropout": cfg["augmentation"]["max_dropout"],
            "copies_per_sample": cfg["augmentation"].get("copies_per_sample", 3)
        }
    }

    metadata_path = os.path.join(v1_dir, "metadata.json")
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    with open(os.path.join(root_model_dir, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"[SUCCESS] Version 1 artifacts exported with metadata.json!")

if __name__ == "__main__":
    train_and_export_v1()
