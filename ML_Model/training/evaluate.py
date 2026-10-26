"""
ArogyaMitra — Comprehensive Model Evaluation & Diagnostic Report
Computes reliability calibration curves, ECE, Brier score, per-class F1,
and confusion matrix diagnostics across full and masked test inputs.
Saves empirical evidence to docs/evidence/.
"""

import os
import sys

os.environ["TEMP"] = r"D:\temp"
os.environ["TMP"] = r"D:\temp"
os.environ["UV_CACHE_DIR"] = r"D:\.uv_cache"

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

import joblib
import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import (
    classification_report,
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ML_Model.training.prepare_data import apply_symptom_masking, load_and_clean_data


def compute_multiclass_ece(probs: np.ndarray, labels: np.ndarray, n_bins: int = 10):
    confidences = np.max(probs, axis=1)
    predictions = np.argmax(probs, axis=1)
    accuracies = (predictions == labels).astype(float)
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    bin_stats = []
    for i in range(n_bins):
        bin_mask = (confidences > bin_boundaries[i]) & (confidences <= bin_boundaries[i+1])
        count = int(np.sum(bin_mask))
        if count > 0:
            bin_acc = float(np.mean(accuracies[bin_mask]))
            bin_conf = float(np.mean(confidences[bin_mask]))
            ece += count * np.abs(bin_acc - bin_conf)
            bin_stats.append({
                "bin": f"({bin_boundaries[i]:.1f}, {bin_boundaries[i+1]:.1f}]",
                "count": count,
                "confidence": round(bin_conf, 4),
                "accuracy": round(bin_acc, 4)
            })
    return float(ece / len(labels)), bin_stats

def run_evaluation():
    print("[EVAL] Commencing detailed diagnostic evaluation...")
    model_dir = os.path.join(BASE_DIR, "ML_Model", "model", "v1")
    evidence_dir = os.path.join(BASE_DIR, "docs", "evidence")
    os.makedirs(evidence_dir, exist_ok=True)

    calibrator = joblib.load(os.path.join(model_dir, "calibrator.pkl"))
    base_model = joblib.load(os.path.join(model_dir, "disease_model.pkl"))
    label_encoder = joblib.load(os.path.join(model_dir, "label_encoder.pkl"))

    data_dir = os.path.join(BASE_DIR, "ML_Model", "dataset")
    data = load_and_clean_data(os.path.join(data_dir, "Training.csv"), deduplicate=True)
    X, y = data["X"], data["y"]
    classes = label_encoder.classes_
    num_classes = len(classes)

    # 1. Predictions on clean ground-truth
    probs_uncal = base_model.predict_proba(X)
    probs_cal = calibrator.predict_proba(X)
    preds_cal = np.argmax(probs_cal, axis=1)

    ece_uncal, _ = compute_multiclass_ece(probs_uncal, y)
    ece_cal, bin_stats = compute_multiclass_ece(probs_cal, y)

    # Multi-class Brier score
    y_one_hot = np.zeros_like(probs_cal)
    for i, label in enumerate(y):
        y_one_hot[i, label] = 1.0
    brier = float(np.mean(np.sum((probs_cal - y_one_hot) ** 2, axis=1)))

    print(f"  Uncalibrated ECE: {ece_uncal:.4f}")
    print(f"  Calibrated ECE:   {ece_cal:.4f}")
    print(f"  Brier Score:      {brier:.4f}")

    # 2. Generate Reliability Plot
    fig, ax = plt.subplots(figsize=(6, 5), dpi=150)
    confidences = np.max(probs_cal, axis=1)
    accuracies = (preds_cal == y).astype(float)
    bins = np.linspace(0, 1, 11)
    bin_accs = []
    bin_confs = []
    for i in range(10):
        mask = (confidences > bins[i]) & (confidences <= bins[i+1])
        if np.any(mask):
            bin_accs.append(np.mean(accuracies[mask]))
            bin_confs.append(np.mean(confidences[mask]))
    ax.plot([0, 1], [0, 1], "k--", label="Perfect Calibration")
    if bin_confs:
        ax.plot(bin_confs, bin_accs, "s-", color="#1f77b4", label=f"Calibrated LightGBM (ECE={ece_cal:.3f})")
    ax.set_xlabel("Mean Predicted Confidence")
    ax.set_ylabel("Empirical Accuracy")
    ax.set_title("Reliability Diagram (ArogyaMitra v1)")
    ax.legend(loc="lower right")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    plot_path = os.path.join(evidence_dir, "calibration_reliability.png")
    fig.savefig(plot_path)
    plt.close(fig)
    print(f"  [SAVED] Calibration plot: {plot_path}")

    # 3. Robustness under symptom masking
    mask_results = []
    for rate in [0.0, 0.2, 0.4, 0.6]:
        masked_X = apply_symptom_masking(X, mask_rate=rate, random_state=42)
        p = calibrator.predict_proba(masked_X)
        pred = np.argmax(p, axis=1)
        acc = float(np.mean(pred == y))
        top3_acc = float(np.mean([y[i] in np.argsort(p[i])[-3:] for i in range(len(y))]))
        ece, _ = compute_multiclass_ece(p, y)
        mask_results.append({
            "mask_rate": f"{int(rate*100)}%",
            "top1_accuracy": round(acc * 100, 2),
            "top3_accuracy": round(top3_acc * 100, 2),
            "ece": round(ece, 4)
        })

    # 4. Per-Class Classification Report
    clf_report = classification_report(y, preds_cal, target_names=classes, output_dict=True, zero_division=0)
    report_md_path = os.path.join(evidence_dir, "classification_report.md")
    with open(report_md_path, "w", encoding="utf-8") as f:
        f.write("# ArogyaMitra v1 — Model Diagnostic and Calibration Report\n\n")
        f.write(f"- **Total Unique Ground-Truth Samples**: {len(X)}\n")
        f.write(f"- **Classes Evaluated**: {num_classes}\n")
        f.write(f"- **Calibrated ECE**: {ece_cal:.4f} (vs Uncalibrated ECE: {ece_uncal:.4f})\n")
        f.write(f"- **Multi-class Brier Score**: {brier:.4f}\n\n")

        f.write("## 1. Reliability & Calibration Bins\n\n")
        f.write("| Confidence Bin | Sample Count | Mean Confidence | Empirical Accuracy |\n")
        f.write("|---|:---:|:---:|:---:|\n")
        f.writelines(f"| {b['bin']} | {b['count']} | {b['confidence']:.4f} | {b['accuracy']:.4f} |\n" for b in bin_stats)

        f.write("\n## 2. Robustness Under Symptom Omission (Masking)\n\n")
        f.write("| Mask Rate (% Symptoms Hidden) | Top-1 Accuracy (%) | Top-3 Accuracy (%) | ECE |\n")
        f.write("|---|:---:|:---:|:---:|\n")
        f.writelines(f"| {mr['mask_rate']} | {mr['top1_accuracy']}% | {mr['top3_accuracy']}% | {mr['ece']} |\n" for mr in mask_results)

        f.write("\n## 3. Per-Class Precision, Recall, and F1-Score\n\n")
        f.write("| Disease Class | Precision | Recall | F1-Score | Support |\n")
        f.write("|---|:---:|:---:|:---:|:---:|\n")
        for disease in classes:
            metrics = clf_report.get(disease, {})
            f.write(f"| {disease} | {metrics.get('precision', 0.0):.3f} | {metrics.get('recall', 0.0):.3f} | {metrics.get('f1-score', 0.0):.3f} | {int(metrics.get('support', 0))} |\n")

        macro = clf_report.get("macro avg", {})
        f.write(f"| **Macro Average** | **{macro.get('precision', 0.0):.3f}** | **{macro.get('recall', 0.0):.3f}** | **{macro.get('f1-score', 0.0):.3f}** | **{int(macro.get('support', 0))}** |\n")

    print(f"  [SAVED] Diagnostic report: {report_md_path}")
    print("[SUCCESS] Model evaluation complete.")

if __name__ == "__main__":
    run_evaluation()
