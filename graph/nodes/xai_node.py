import os
import httpx

# ML API service URL (local or docker service)
ML_API_URL = os.getenv("ML_API_URL", "http://localhost:8000")


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