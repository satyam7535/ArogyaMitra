"""
Baseline Training Script for ArogyaMitra (Phase 0)
Trains a baseline Random Forest model from Kaggle CSVs and exports artifacts to ML_Model/model/.
"""

import json
import os
import sys

import joblib
import numpy as np
import pandas as pd

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder


def train_and_export():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ml_root = os.path.dirname(script_dir)
    dataset_dir = os.path.join(ml_root, "dataset")
    model_dir = os.path.join(ml_root, "model")
    os.makedirs(model_dir, exist_ok=True)

    print("[INFO] Starting ArogyaMitra Baseline Model Training...")
    print(f"[INFO] Dataset directory: {dataset_dir}")
    print(f"[INFO] Output model directory: {model_dir}")

    # 1. Load Datasets
    dataset_path = os.path.join(dataset_dir, "dataset.csv")
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"dataset.csv not found in {dataset_dir}. See download_dataset.md.")

    df = pd.read_csv(dataset_path).fillna("0")

    # Load Severity
    sev_path = os.path.join(dataset_dir, "Symptom-severity.csv")
    sev_df = pd.read_csv(sev_path)
    sev_df.columns = sev_df.columns.str.strip()
    severity_map = dict(zip(
        sev_df['Symptom'].str.strip().str.lower().str.replace(' ', '_'),
        sev_df['weight']
    ))

    # Load Descriptions
    desc_path = os.path.join(dataset_dir, "symptom_Description.csv")
    desc_df = pd.read_csv(desc_path)
    desc_df.columns = desc_df.columns.str.strip()
    description_map = dict(zip(
        desc_df['Disease'].str.strip(),
        desc_df['Description'].str.strip()
    ))

    # Load Precautions
    prec_path = os.path.join(dataset_dir, "symptom_precaution.csv")
    prec_df = pd.read_csv(prec_path)
    prec_df.columns = prec_df.columns.str.strip()
    precaution_map = {}
    for _, row in prec_df.iterrows():
        disease = str(row['Disease']).strip()
        precautions = [
            str(row[f'Precaution_{i}']).strip()
            for i in range(1, 5)
            if pd.notna(row[f'Precaution_{i}']) and str(row[f'Precaution_{i}']).strip() != 'nan'
        ]
        precaution_map[disease] = precautions

    # 2. Extract Symptoms and Build Feature Matrix
    symptom_cols_raw = [c for c in df.columns if 'Symptom' in c]
    all_symptoms = set()
    for col in symptom_cols_raw:
        df[col] = df[col].astype(str).str.strip().str.lower().str.replace(' ', '_')
        all_symptoms.update(df[col].unique())

    all_symptoms = sorted([s for s in all_symptoms if s and s != '0' and s != 'nan'])
    symptom_columns = all_symptoms
    print(f"[INFO] Unique symptoms found: {len(symptom_columns)}")

    X = pd.DataFrame(0, index=df.index, columns=symptom_columns, dtype=np.float32)
    for col in symptom_cols_raw:
        for s in symptom_columns:
            X.loc[df[col] == s, s] = 1.0

    # 3. Target Encoding
    le = LabelEncoder()
    y = le.fit_transform(df['Disease'].astype(str).str.strip())
    disease_classes = list(le.classes_)
    print(f"[INFO] Disease classes: {len(disease_classes)}")

    # 4. Train Baseline Model
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    clf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    clf.fit(X_train, y_train)

    train_acc = clf.score(X_train, y_train)
    test_acc = clf.score(X_test, y_test)
    print(f"[SUCCESS] Baseline RF Train Acc: {train_acc*100:.2f}% | Test Acc: {test_acc*100:.2f}%")

    # 5. Save Artifacts
    joblib.dump(clf, os.path.join(model_dir, "disease_model.pkl"))
    joblib.dump(le, os.path.join(model_dir, "label_encoder.pkl"))
    joblib.dump(symptom_columns, os.path.join(model_dir, "symptom_columns.pkl"))
    joblib.dump(np.array(X_train), os.path.join(model_dir, "X_train.pkl"))
    joblib.dump(severity_map, os.path.join(model_dir, "severity_map.pkl"))
    joblib.dump(description_map, os.path.join(model_dir, "description_map.pkl"))
    joblib.dump(precaution_map, os.path.join(model_dir, "precaution_map.pkl"))

    metadata = {
        "best_model": "RandomForestClassifier",
        "accuracy": round(float(test_acc) * 100, 2),
        "total_diseases": len(disease_classes),
        "total_symptoms": len(symptom_columns),
        "diseases": disease_classes,
        "symptoms": symptom_columns,
        "note": "Phase 0 baseline model. To be upgraded with LightGBM + TreeSHAP in Phase 1."
    }
    with open(os.path.join(model_dir, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print("[SUCCESS] All Phase 0 model artifacts successfully exported to ML_Model/model/")

if __name__ == "__main__":
    train_and_export()
