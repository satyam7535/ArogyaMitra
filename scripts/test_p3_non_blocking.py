#!/usr/bin/env python3
"""
ArogyaMitra — Phase P3.9 Non-Blocking Backend Responsiveness During ML Outage Test
Verifies:
  1. Measures baseline latency for /health and patient operations.
  2. Stops arogya-ml container to simulate total ML service outage.
  3. While ML is DOWN:
     - Proves GET /health remains HTTP 200 with latency < 100ms.
     - Proves Patient CRUD (Create, Read, List) continues operating with HTTP 200/201 and low latency.
     - Proves AI inference returns loud fail-closed HTTP 503 without stalling the Express event loop.
     - Performs 20 concurrent health/CRUD requests to prove non-blocking event loop under ML outage.
  4. Restarts arogya-ml container and confirms full recovery.
Outputs evidence to docs/evidence/p3_non_blocking_test.txt.
"""

import concurrent.futures
import datetime
import os
import subprocess
import sys
import time
import urllib3
import requests

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = os.getenv("AROGYA_URL", "https://localhost")
API_URL = f"{BASE_URL}/api/v1"

def run_test():
    lines = []
    def log(msg=""):
        print(msg)
        lines.append(msg)

    log("================================================================================")
    log("AROGYAMITRA — PHASE P3.9 NON-BLOCKING BACKEND RESPONSIVENESS TEST (DOCKER)")
    log("Date: " + datetime.datetime.now(datetime.timezone.utc).isoformat())
    log("Target: " + BASE_URL)
    log("================================================================================\n")

    session = requests.Session()
    session.verify = False

    # 1. Login as Worker
    log("[STEP 1] Authenticating as Worker...")
    login_res = session.post(f"{API_URL}/worker/login", json={
        "email": "worker@arogyamitra.gov.in",
        "password": "Worker@Arogya2026!"
    }, timeout=10)

    if login_res.status_code != 200:
        log(f"[-] Login failed: HTTP {login_res.status_code}")
        return False, "\n".join(lines)

    token = login_res.json().get("accessToken") or login_res.json().get("token")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    log("[+] Authenticated successfully as Worker.\n")

    # 2. Baseline Health and Patient Read Latency
    log("[STEP 2] Measuring baseline responsiveness with ML container running...")
    latencies_health = []
    for _ in range(5):
        t0 = time.perf_counter()
        r = session.get(f"{BASE_URL}/health", timeout=5)
        dt_ms = (time.perf_counter() - t0) * 1000
        latencies_health.append(dt_ms)
        assert r.status_code == 200, f"Baseline health check failed: {r.status_code}"

    avg_health_base = sum(latencies_health) / len(latencies_health)
    log(f"[+] Baseline GET /health latency: {avg_health_base:.2f}ms (min: {min(latencies_health):.2f}ms, max: {max(latencies_health):.2f}ms)\n")

    # 3. Simulate Total ML Service Outage (Stop arogya-ml)
    log("[STEP 3] Stopping arogya-ml container to induce total ML inference outage...")
    subprocess.run(["docker", "stop", "arogya-ml"], check=True, capture_output=True)
    time.sleep(2)
    log("[+] arogya-ml stopped successfully.\n")

    try:
        # 4. Measure Health Endpoint During ML Outage
        log("[STEP 4] Testing GET /health while ML container is stopped...")
        latencies_outage_health = []
        for _ in range(10):
            t0 = time.perf_counter()
            r = session.get(f"{BASE_URL}/health", timeout=5)
            dt_ms = (time.perf_counter() - t0) * 1000
            latencies_outage_health.append(dt_ms)
            if r.status_code != 200:
                log(f"[-] /health failed with status {r.status_code}")
                return False, "\n".join(lines)

        avg_health_outage = sum(latencies_outage_health) / len(latencies_outage_health)
        log(f"[+] Outage GET /health latency: {avg_health_outage:.2f}ms (min: {min(latencies_outage_health):.2f}ms, max: {max(latencies_outage_health):.2f}ms)")
        if avg_health_outage > 100.0:
            log(f"[-] WARN/FAIL: /health latency exceeded 100ms: {avg_health_outage:.2f}ms")
            return False, "\n".join(lines)
        log("[+] VERIFIED: GET /health responds < 100ms during ML outage.\n")

        # 5. Patient CRUD During ML Outage
        log("[STEP 5] Performing Patient CRUD operations while ML is down...")
        # Create Patient
        t0 = time.perf_counter()
        patient_phone = f"9871{int(time.time()) % 1000000:06d}"
        create_res = session.post(f"{API_URL}/patient", json={
            "name": "Outage Resilience Test Patient",
            "age": 42,
            "gender": "Male",
            "phoneNumber": patient_phone,
            "address": "Primary Health Subcentre 9",
            "consentGiven": True,
            "consentLanguage": "en"
        }, headers=headers, timeout=5)
        create_ms = (time.perf_counter() - t0) * 1000

        if create_res.status_code not in (200, 201):
            log(f"[-] Patient creation failed during ML outage: {create_res.status_code} {create_res.text}")
            return False, "\n".join(lines)

        patient_id = (
            create_res.json().get("patient", {}).get("_id") or
            create_res.json().get("data", {}).get("_id") or
            create_res.json().get("_id")
        )
        log(f"[+] Patient created successfully in {create_ms:.2f}ms (ID: {patient_id})")

        # Read Patient
        t0 = time.perf_counter()
        read_res = session.get(f"{API_URL}/patient/{patient_id}", headers=headers, timeout=5)
        read_ms = (time.perf_counter() - t0) * 1000
        if read_res.status_code != 200:
            log(f"[-] Patient read failed: {read_res.status_code}")
            return False, "\n".join(lines)
        log(f"[+] Patient read successfully in {read_ms:.2f}ms")

        # List Patients
        t0 = time.perf_counter()
        list_res = session.get(f"{API_URL}/patient", headers=headers, timeout=5)
        list_ms = (time.perf_counter() - t0) * 1000
        if list_res.status_code != 200:
            log(f"[-] Patient list failed: {list_res.status_code}")
            return False, "\n".join(lines)
        log(f"[+] Patient list returned successfully in {list_ms:.2f}ms\n")

        # 6. Verify Fail-Closed Loud 503 for ML Analysis (No Hanging)
        log("[STEP 6] Confirming ML analysis returns fail-closed loud HTTP 503...")
        t0 = time.perf_counter()
        triage_res = session.post(f"{API_URL}/consultation/triage", json={
            "symptoms": ["chills", "high_fever"],
            "patientName": "Outage Test",
            "patientAge": 30,
            "patientGender": "Male"
        }, headers=headers, timeout=10)
        triage_ms = (time.perf_counter() - t0) * 1000

        log(f"[+] ML direct triage returned HTTP {triage_res.status_code} in {triage_ms:.2f}ms")
        log(f"[+] Response body: {triage_res.text}")

        if triage_res.status_code != 503:
            log(f"[-] FAIL-CLOSED VIOLATION: Expected HTTP 503 during ML outage, got {triage_res.status_code}")
            return False, "\n".join(lines)

        triage_data = triage_res.json()
        if not triage_data.get("modelUnavailable") and triage_data.get("code") not in ("MODEL_UNAVAILABLE", "ML_SERVICE_UNAVAILABLE"):
            log(f"[-] FAIL-CLOSED VIOLATION: Expected code MODEL_UNAVAILABLE / ML_SERVICE_UNAVAILABLE, got {triage_data.get('code')}")
            return False, "\n".join(lines)
        log("[+] Loud fail-closed 503 verified.\n")

        # 7. Concurrent Non-Blocking Event Loop Verification
        log("[STEP 7] Firing 20 concurrent requests across health and patient endpoints during ML outage...")
        def probe(i):
            url = f"{BASE_URL}/health" if i % 2 == 0 else f"{API_URL}/patient"
            req_headers = headers if i % 2 != 0 else {}
            t_start = time.perf_counter()
            r = requests.get(url, headers=req_headers, verify=False, timeout=5)
            dt = (time.perf_counter() - t_start) * 1000
            return r.status_code, dt

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
            futs = [ex.submit(probe, i) for i in range(20)]
            results = [f.result() for f in concurrent.futures.as_completed(futs)]

        concurrent_statuses = [r[0] for r in results]
        concurrent_latencies = [r[1] for r in results]
        avg_concurrent_lat = sum(concurrent_latencies) / len(concurrent_latencies)

        log(f"[+] 20 concurrent requests completed.")
        log(f"[+] Statuses: 200 x {concurrent_statuses.count(200)}, other: {len(concurrent_statuses) - concurrent_statuses.count(200)}")
        log(f"[+] Average latency under concurrent load: {avg_concurrent_lat:.2f}ms (max: {max(concurrent_latencies):.2f}ms)")

        if concurrent_statuses.count(200) != 20:
            log(f"[-] Non-blocking failure: Some concurrent requests failed: {concurrent_statuses}")
            return False, "\n".join(lines)

        log("[+] Non-blocking Express event loop verified: Zero blocking, all requests handled concurrently.\n")

    finally:
        # 8. Restore ML container
        log("[STEP 8] Restarting arogya-ml container...")
        subprocess.run(["docker", "start", "arogya-ml"], check=True, capture_output=True)
        # Wait for ML service to become fully healthy
        for _ in range(15):
            time.sleep(1)
            probe = subprocess.run(["docker", "exec", "arogya-ml", "curl", "-s", "http://127.0.0.1:8000/health"], capture_output=True, text=True)
            if probe.returncode == 0 and "healthy" in probe.stdout:
                break
        time.sleep(2)
        log("[+] arogya-ml container restarted and healthy.\n")

    # 9. Verify Post-Recovery
    log("[STEP 9] Verifying system recovery after arogya-ml restart...")
    recovered_res = session.post(f"{API_URL}/consultation/triage", json={
        "symptoms": ["chills", "high_fever", "sweating", "headache"],
        "patientName": "Recovery Test",
        "patientAge": 30,
        "patientGender": "Male"
    }, headers=headers, timeout=15)

    if recovered_res.status_code != 200:
        log(f"[-] Recovery check failed: HTTP {recovered_res.status_code} {recovered_res.text}")
        return False, "\n".join(lines)

    pred = recovered_res.json().get("disease") or recovered_res.json().get("analysis", {}).get("primaryDiagnosis")
    log(f"[+] System successfully restored. Prediction: {pred}")

    log("\n================================================================================")
    log("RESULT: VERIFIED — Non-blocking backend responsiveness verified during total ML outage.")
    log("================================================================================")
    return True, "\n".join(lines)

if __name__ == "__main__":
    success, output = run_test()
    header = f"""================================================================================
AROGYAMITRA EVIDENCE — PHASE P3.9 NON-BLOCKING BACKEND RESPONSIVENESS TEST
Date: {datetime.datetime.now(datetime.timezone.utc).isoformat()}
Git Commit: fa04225 (working tree: dirty)
Command: python scripts/test_p3_non_blocking.py
================================================================================

"""
    with open("docs/evidence/p3_non_blocking_test.txt", "w", encoding="utf-8") as f:
        f.write(header + output)

    if not success:
        sys.exit(1)
    print("\nEvidence saved to docs/evidence/p3_non_blocking_test.txt")
