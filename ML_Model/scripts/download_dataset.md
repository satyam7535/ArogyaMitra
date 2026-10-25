# Dataset Acquisition and Setup Instructions

ArogyaMitra uses two public Kaggle datasets for primary healthcare symptom mapping and disease classification.

## Required Dataset Files

Place the following 6 CSV files into `ML_Model/dataset/`:

### 1. Disease Prediction Using Machine Learning
- **Source**: [Kaggle: Disease Prediction Using Machine Learning](https://www.kaggle.com/datasets/kaushil268/disease-prediction-using-machine-learning)
- **Files**:
  - `Training.csv`: 4,920 rows × 133 columns (132 symptoms + `prognosis`, plus an empty `Unnamed: 133` column to be dropped). Contains 304 unique rows across 41 disease classes.
  - `Testing.csv`: 42 rows × 133 columns (benchmark reference; note that 41 of 42 rows overlap with Training.csv, so evaluation uses stratified cross-validation on deduplicated data).

### 2. Disease Symptom Prediction (Descriptions & Precautions)
- **Source**: [Kaggle: Disease Symptom Prediction](https://www.kaggle.com/datasets/itachi9604/disease-symptom-description-dataset)
- **Files**:
  - `dataset.csv`: Symptom combinations per disease.
  - `Symptom-severity.csv`: Numerical weights (1 to 7) for clinical symptom severity scoring.
  - `symptom_Description.csv`: Layman and clinical descriptions per disease class.
  - `symptom_precaution.csv`: 4 recommended lifestyle/precaution steps per disease.

## Verification
Ensure the following directory structure:
```
ML_Model/dataset/
├── dataset.csv
├── Symptom-severity.csv
├── symptom_Description.csv
├── symptom_precaution.csv
├── Testing.csv
└── Training.csv
```

**Note**: Do NOT commit raw `.csv` files to Git. The `.gitignore` at the repository root automatically excludes CSV files.
