import os

import httpx

ML_API_URL = os.getenv("ML_API_URL", "http://localhost:8000")
INTERNAL_SERVICE_SECRET = os.getenv("INTERNAL_SERVICE_SECRET", "")

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

    headers = {}
    if INTERNAL_SERVICE_SECRET:
        headers["X-Internal-Service-Token"] = INTERNAL_SERVICE_SECRET
        headers["Authorization"] = f"Bearer {INTERNAL_SERVICE_SECRET}"

    response = http_client.post(
        f"{ML_API_URL}/predict",
        json=payload,
        headers=headers,
    )
    response.raise_for_status()
    result = response.json()

    return {"xai_output": result}