import os
import httpx

# Deployed ML API on HuggingFace Spaces
ML_API_URL = os.getenv("ML_API_URL", "https://dashayush-arogyamitra-api.hf.space")


def xai_node(state):
    req = state["request"]

    payload = {
        "symptoms":      req.symptoms,
        "patientName":   req.patientName,
        "patientAge":    req.patientAge,
        "patientGender": req.patientGender,
        "workerName":    req.workerName,
        "location":      req.location,
    }

    response = httpx.post(
        f"{ML_API_URL}/predict",
        json=payload,
        timeout=60.0,  # HF Spaces may need a cold-start
    )
    response.raise_for_status()
    result = response.json()

    return {"xai_output": result}