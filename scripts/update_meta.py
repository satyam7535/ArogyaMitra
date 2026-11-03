with open("ML_Model/model/v2/metadata.json", "r", encoding="utf-8") as f:
    text = f.read()
text = text.replace('"git_commit": "fa04225"', '"git_commit": "540e05f"')
with open("ML_Model/model/v2/metadata.json", "w", encoding="utf-8") as f:
    f.write(text)
print("Updated metadata.json")

with open("ML_Model/app.py", "r", encoding="utf-8") as f:
    app_text = f.read()

helper_fn = '''
def get_current_git_commit():
    commit = os.getenv("GIT_COMMIT")
    if commit:
        dirty_flag = os.getenv("GIT_DIRTY", "")
        return f"{commit}{dirty_flag}"
    try:
        import subprocess
        c = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.DEVNULL).decode().strip()
        status = subprocess.check_output(["git", "status", "--porcelain"], stderr=subprocess.DEVNULL).decode().strip()
        dirty = " (dirty)" if status else ""
        return f"{c}{dirty}"
    except Exception:
        return metadata.get("git_commit", "540e05f")
'''

if "def get_current_git_commit" not in app_text:
    app_text = app_text.replace("app = FastAPI(", helper_fn + "\napp = FastAPI(")

old_info = '''@app.get("/model-info")
def model_info():
    if not model_loaded:
        load_artifacts()
    return {
        "modelVersion": metadata.get("model_version", "v1.0.0"),
        "algorithm": metadata.get("model_family", "Bernoulli Naive Bayes + Exact Bayesian Log-Odds Explanation"),
        "trainingTimestamp": metadata.get("training_timestamp"),
        "gitCommit": metadata.get("git_commit"),
        "dataset": metadata.get("dataset"),
        "metrics": {
            "out_of_fold_cross_validation": metadata.get("out_of_fold_cross_validation_benchmark"),
            "in_sample_clean_data": metadata.get("in_sample_metrics_on_clean_data"),
            "model_card": "ML_Model/model/v2/metadata.json",
        },
        "totalSymptoms": len(symptom_columns),
        "totalClasses": len(label_encoder.classes_) if label_encoder else 0,
        "classes": list(label_encoder.classes_) if label_encoder else []
    }'''

new_info = '''@app.get("/model-info")
def model_info():
    if not model_loaded:
        load_artifacts()
    return {
        "modelVersion": metadata.get("model_version", "v2.0.0"),
        "algorithm": metadata.get("model_family", "Bernoulli Naive Bayes + Exact Bayesian Log-Odds Explanation"),
        "trainingTimestamp": metadata.get("training_timestamp"),
        "gitCommit": get_current_git_commit(),
        "dataset": metadata.get("dataset"),
        "metrics": {
            "out_of_fold_cross_validation": metadata.get("out_of_fold_cross_validation_benchmark"),
            "in_sample_clean_data": metadata.get("in_sample_metrics_on_clean_data"),
            "calibration": metadata.get("calibration"),
            "model_card": "ML_Model/model/v2/metadata.json",
        },
        "totalSymptoms": len(symptom_columns),
        "totalClasses": len(label_encoder.classes_) if label_encoder else 0,
        "classes": list(label_encoder.classes_) if label_encoder else []
    }'''

app_text = app_text.replace(old_info, new_info)

with open("ML_Model/app.py", "w", encoding="utf-8") as f:
    f.write(app_text)
print("Updated ML_Model/app.py")
