"""
ArogyaMitra — Compute Symptom-Disease Characteristic Frequency Matrix
Generates symptom_class_matrix.json mapping each of the 41 diseases to their symptom frequencies.
Used in live inference to suggest distinguishing follow-up questions when diagnostic margin is narrow or confidence is low.
"""

import json
import os
import sys

import numpy as np

# Ensure root on path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ML_Model.training.prepare_data import load_and_clean_data


def compute_matrix():
    data_dir = os.path.join(BASE_DIR, "ML_Model", "dataset")
    data = load_and_clean_data(os.path.join(data_dir, "Training.csv"), deduplicate=True)
    X = data["X"]
    y = data["y"]
    features = data["feature_names"]
    le = data["label_encoder"]

    symptom_matrix = {}
    for c_idx, class_name in enumerate(le.classes_):
        class_mask = (y == c_idx)
        class_X = X[class_mask]
        n_samples = len(class_X)
        if n_samples == 0:
            continue
        # Symptom frequencies in this class
        freqs = np.mean(class_X, axis=0)
        # Store non-zero symptom frequencies
        symptom_matrix[class_name] = {
            features[f_idx]: round(float(freqs[f_idx]), 4)
            for f_idx in range(len(features))
            if freqs[f_idx] > 0.0
        }

    # Save to model/v1 and model/
    for folder in [os.path.join(BASE_DIR, "ML_Model", "model", "v1"), os.path.join(BASE_DIR, "ML_Model", "model")]:
        os.makedirs(folder, exist_ok=True)
        out_path = os.path.join(folder, "symptom_class_matrix.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(symptom_matrix, f, indent=2)
        print(f"[+] Saved symptom class matrix to: {out_path}")

if __name__ == "__main__":
    compute_matrix()

