"""
ArogyaMitra — Data Preparation & Augmentation Module
Handles dataset loading, symptom/disease normalization, deduplication, and symptom-dropout augmentation.
"""

import os
import re
from typing import Tuple, List, Dict, Any, Optional
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder

# Standardized normalization dictionary for known discrepancies
SYMPTOM_NAME_MAPPINGS = {
    "dischromic__patches": "dischromic_patches",
    "spotting__urination": "spotting_urination",
    "foul_smell_ofurine": "foul_smell_of_urine",
    "fluid_overload.1": "fluid_overload",
}

DISEASE_NAME_MAPPINGS = {
    "Dimorphic hemmorhoids(piles)": "Dimorphic hemorrhoids(piles)",
    "Dimorphic hemorrhoids(piles)": "Dimorphic hemorrhoids(piles)",
}

def normalize_symptom_name(name: str) -> str:
    cleaned = name.strip().lower().replace(" ", "_")
    cleaned = re.sub(r"_+", "_", cleaned)
    return SYMPTOM_NAME_MAPPINGS.get(cleaned, cleaned)

def normalize_disease_name(name: str) -> str:
    cleaned = name.strip()
    return DISEASE_NAME_MAPPINGS.get(cleaned, cleaned)

def load_and_clean_data(
    training_path: str,
    severity_path: Optional[str] = None,
    desc_path: Optional[str] = None,
    prec_path: Optional[str] = None,
    deduplicate: bool = True
) -> Dict[str, Any]:
    """
    Loads Training.csv, normalizes symptom column names, merges duplicate columns,
    deduplicates identical symptom vectors, and maps metadata.
    """
    if not os.path.exists(training_path):
        raise FileNotFoundError(f"Training dataset not found at: {training_path}")

    raw_df = pd.read_csv(training_path)
    initial_rows = len(raw_df)

    # 1. Drop unwanted columns
    cols_to_drop = [c for c in ["Unnamed: 133"] if c in raw_df.columns]
    df = raw_df.drop(columns=cols_to_drop).copy()

    # 2. Merge fluid_overload and fluid_overload.1 if present
    if "fluid_overload" in df.columns and "fluid_overload.1" in df.columns:
        df["fluid_overload"] = df["fluid_overload"] | df["fluid_overload.1"]
        df = df.drop(columns=["fluid_overload.1"])

    # 3. Normalize feature column names
    target_col = "prognosis" if "prognosis" in df.columns else df.columns[-1]
    feature_cols = [c for c in df.columns if c != target_col]

    rename_map = {}
    for c in feature_cols:
        norm = normalize_symptom_name(c)
        rename_map[c] = norm
    df = df.rename(columns=rename_map)

    # Remove duplicate columns if any resulted from normalization
    df = df.loc[:, ~df.columns.duplicated()]

    # 4. Normalize target disease names
    df[target_col] = df[target_col].astype(str).apply(normalize_disease_name)

    # 5. Deduplication
    unique_rows_before = len(df)
    if deduplicate:
        df = df.drop_duplicates().reset_index(drop=True)
    unique_rows_after = len(df)
    duplicate_rows_dropped = initial_rows - unique_rows_after

    # 6. Extract X, y, label encoder
    feature_cols = sorted([c for c in df.columns if c != target_col])
    X = df[feature_cols].astype(np.float32).values
    y_raw = df[target_col].values

    le = LabelEncoder()
    y = le.fit_transform(y_raw)
    disease_classes = list(le.classes_)

    # 7. Load Severity Map
    severity_map: Dict[str, int] = {}
    if severity_path and os.path.exists(severity_path):
        sev_df = pd.read_csv(severity_path)
        sev_df.columns = sev_df.columns.str.strip()
        for _, row in sev_df.iterrows():
            s_name = str(row["Symptom"]).strip()
            if s_name.lower() == "prognosis":
                continue
            norm_s = normalize_symptom_name(s_name)
            severity_map[norm_s] = int(row["weight"])

    # Ensure every feature has a severity weight (default to 1 if unlisted)
    for s in feature_cols:
        if s not in severity_map:
            severity_map[s] = 1

    # 8. Load Descriptions Map
    description_map: Dict[str, str] = {}
    if desc_path and os.path.exists(desc_path):
        desc_df = pd.read_csv(desc_path)
        desc_df.columns = desc_df.columns.str.strip()
        for _, row in desc_df.iterrows():
            d_name = normalize_disease_name(str(row["Disease"]))
            description_map[d_name] = str(row["Description"]).strip()

    # 9. Load Precautions Map
    precaution_map: Dict[str, List[str]] = {}
    if prec_path and os.path.exists(prec_path):
        prec_df = pd.read_csv(prec_path)
        prec_df.columns = prec_df.columns.str.strip()
        for _, row in prec_df.iterrows():
            d_name = normalize_disease_name(str(row["Disease"]))
            precautions = [
                str(row[f"Precaution_{i}"]).strip()
                for i in range(1, 5)
                if pd.notna(row[f"Precaution_{i}"]) and str(row[f"Precaution_{i}"]).strip().lower() != "nan"
            ]
            precaution_map[d_name] = precautions

    # Class balance stats
    class_counts = pd.Series(y_raw).value_counts().to_dict()

    return {
        "X": X,
        "y": y,
        "feature_names": feature_cols,
        "target_names": disease_classes,
        "label_encoder": le,
        "severity_map": severity_map,
        "description_map": description_map,
        "precaution_map": precaution_map,
        "stats": {
            "initial_rows": initial_rows,
            "unique_rows": unique_rows_after,
            "duplicate_rows_dropped": duplicate_rows_dropped,
            "num_features": len(feature_cols),
            "num_classes": len(disease_classes),
            "class_distribution": class_counts
        }
    }

def augment_training_data(
    X_train: np.ndarray,
    y_train: np.ndarray,
    min_dropout: float = 0.0,
    max_dropout: float = 0.60,
    min_symptoms_kept: int = 1,
    copies_per_sample: int = 3,
    random_state: int = 42
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Augments the training fold only with symptom-dropout copies.
    Never run on validation or test sets.
    """
    rng = np.random.RandomState(random_state)
    augmented_X = [X_train]
    augmented_y = [y_train]

    for copy_idx in range(copies_per_sample):
        X_copy = np.copy(X_train)
        for i in range(len(X_copy)):
            present_indices = np.where(X_copy[i] > 0)[0]
            num_present = len(present_indices)
            if num_present <= min_symptoms_kept:
                continue

            # Sample dropout rate for this row
            p_drop = rng.uniform(min_dropout, max_dropout)
            drop_mask = rng.binomial(1, p_drop, size=num_present).astype(bool)

            # Ensure we do not drop all symptoms
            if np.sum(~drop_mask) < min_symptoms_kept:
                keep_idx = rng.choice(num_present, size=min_symptoms_kept, replace=False)
                drop_mask = np.ones(num_present, dtype=bool)
                drop_mask[keep_idx] = False

            dropped_indices = present_indices[drop_mask]
            X_copy[i, dropped_indices] = 0.0

        augmented_X.append(X_copy)
        augmented_y.append(y_train)

    return np.vstack(augmented_X), np.concatenate(augmented_y)

def apply_symptom_masking(
    X_test: np.ndarray,
    mask_rate: float,
    min_symptoms_kept: int = 1,
    random_state: int = 42
) -> np.ndarray:
    """
    Simulates incomplete symptom reporting at test time by masking a fixed fraction of present symptoms.
    """
    if mask_rate <= 0.0:
        return np.copy(X_test)

    rng = np.random.RandomState(random_state)
    X_masked = np.copy(X_test)

    for i in range(len(X_masked)):
        present = np.where(X_masked[i] > 0)[0]
        num_present = len(present)
        if num_present <= min_symptoms_kept:
            continue

        num_to_mask = int(np.round(num_present * mask_rate))
        num_to_mask = min(num_to_mask, num_present - min_symptoms_kept)
        if num_to_mask > 0:
            mask_idx = rng.choice(present, size=num_to_mask, replace=False)
            X_masked[i, mask_idx] = 0.0

    return X_masked
