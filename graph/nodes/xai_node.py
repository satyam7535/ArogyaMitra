import os

import httpx

ML_API_URL = os.getenv("ML_API_URL", "http://localhost:8000")

# Persistent connection pool with keep-alive for high concurrency
http_limits = httpx.Limits(max_keepalive_connections=20, max_connections=100, keepalive_expiry=30.0)
http_client = httpx.Client(limits=http_limits, timeout=60.0)


def xai_node(state):
    req = state["request"]

    payload = {
        "symptoms": req.symptoms,
        "patientName": req.patientName,
        "patientAge": req.patientAge,
        "patientGender": req.patientGender,
        "workerName": req.workerName,
        "location": req.location,
    }

    response = http_client.post(
        f"{ML_API_URL}/predict",
        json=payload,
    )
    response.raise_for_status()
    result = response.json()

    return {"xai_output": result}