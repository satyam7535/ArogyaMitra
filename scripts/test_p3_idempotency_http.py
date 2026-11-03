#!/usr/bin/env python3
"""
ArogyaMitra — Phase P3.8 HTTP-Level Idempotency Deduplication Test in Docker
Verifies:
  1. Authenticates as worker against the Docker backend HTTPS ingress.
  2. Creates / retrieves an active consultation with patient consent.
  3. Sends 50 concurrent HTTP POST requests to /api/v1/consultation/:id/analyze/async
     with the EXACT SAME Idempotency-Key header.
  4. Asserts all 50 concurrent requests succeed with HTTP 202.
  5. Asserts every single response returns the exact same jobId.
  6. Queries MongoDB directly to prove strictly exactly 1 AnalysisJob document exists with this idempotencyKey.
  7. Sends a distinct request with a new Idempotency-Key and proves a distinct new jobId is created.
"""

import concurrent.futures
import datetime
import json
import os
import subprocess
import sys
import time
import uuid
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
    log("AROGYAMITRA — PHASE P3.8 REAL HTTP IDEMPOTENCY DEDUPLICATION TEST (DOCKER)")
    log("Date: " + datetime.datetime.now(datetime.timezone.utc).isoformat())
    log("Ingress Target: " + BASE_URL)
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
        log(f"[-] Login failed: HTTP {login_res.status_code} {login_res.text}")
        return False, "\n".join(lines)

    token = login_res.json().get("accessToken") or login_res.json().get("token")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    log("[+] Authenticated successfully as Worker.\n")

    # 2. Register a Patient with Consent
    log("[STEP 2] Creating Patient with Consent...")
    patient_phone = f"9876{int(time.time()) % 1000000:06d}"
    patient_res = session.post(f"{API_URL}/patient", json={
        "name": "Idempotency Test Subject",
        "age": 34,
        "gender": "Female",
        "phoneNumber": patient_phone,
        "address": "Community Health Center Ward 4",
        "consentGiven": True,
        "consentLanguage": "en"
    }, headers=headers, timeout=10)

    if patient_res.status_code not in (200, 201):
        log(f"[-] Patient registration failed: {patient_res.status_code} {patient_res.text}")
        return False, "\n".join(lines)

    patient_id = (
        patient_res.json().get("patient", {}).get("_id") or
        patient_res.json().get("data", {}).get("_id") or
        patient_res.json().get("_id")
    )
    log(f"[+] Patient registered: {patient_id}\n")

    # 3. Create Consultation
    log("[STEP 3] Creating Consultation...")
    cons_res = session.post(f"{API_URL}/consultation", json={
        "patientId": patient_id,
        "symptoms": ["chills", "high_fever", "sweating"],
        "notes": "Patient experiencing intermittent high fever and rigor."
    }, headers=headers, timeout=10)

    if cons_res.status_code not in (200, 201):
        log(f"[-] Consultation creation failed: {cons_res.status_code} {cons_res.text}")
        return False, "\n".join(lines)

    consultation_id = (
        cons_res.json().get("consultation", {}).get("_id") or
        cons_res.json().get("data", {}).get("_id") or
        cons_res.json().get("_id")
    )
    log(f"[+] Consultation created: {consultation_id}\n")

    # 4. 50 Parallel Requests with IDENTICAL Idempotency-Key
    idempotency_key = f"idem-key-{uuid.uuid4()}"
    log(f"[STEP 4] Firing 50 parallel HTTP POST requests with Idempotency-Key: {idempotency_key}")
    
    url = f"{API_URL}/consultation/{consultation_id}/analyze/async"

    def make_request(req_idx):
        req_headers = dict(headers)
        req_headers["Idempotency-Key"] = idempotency_key
        try:
            r = requests.post(url, json={"language": "en"}, headers=req_headers, verify=False, timeout=15)
            data = r.json()
            job_id = data.get("job", {}).get("jobId")
            return {
                "idx": req_idx,
                "status_code": r.status_code,
                "job_id": job_id,
                "duplicate": data.get("job", {}).get("isDuplicate", False),
                "error": None
            }
        except Exception as e:
            return {
                "idx": req_idx,
                "status_code": None,
                "job_id": None,
                "duplicate": False,
                "error": str(e)
            }

    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(make_request, i) for i in range(50)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    elapsed = time.time() - start_time

    status_codes = [r["status_code"] for r in results]
    job_ids = set(r["job_id"] for r in results if r["job_id"])
    errors = [r["error"] for r in results if r["error"]]

    log(f"[+] All 50 requests finished in {elapsed:.2f}s")
    log(f"[+] Status codes received: 202 x {status_codes.count(202)}, other: {len(status_codes) - status_codes.count(202)}")
    log(f"[+] Unique jobIds returned across all 50 concurrent requests: {len(job_ids)}")
    log(f"[+] Job ID values: {list(job_ids)}")

    if len(errors) > 0:
        log(f"[-] Errors encountered: {errors[:3]}")
        return False, "\n".join(lines)

    if status_codes.count(202) != 50:
        log(f"[-] Expected 50 HTTP 202 responses, got: {status_codes}")
        return False, "\n".join(lines)

    if len(job_ids) != 1:
        log(f"[-] IDEMPOTENCY VIOLATION: Expected exactly 1 unique jobId, got {len(job_ids)}: {job_ids}")
        return False, "\n".join(lines)

    canonical_job_id = list(job_ids)[0]
    log(f"[+] SUCCESS: Exactly 1 unique job was returned ({canonical_job_id}) across all 50 parallel requests.\n")

    # 5. Database Direct Verification (Inside Docker MongoDB)
    log("[STEP 5] Verifying database records directly inside MongoDB container...")
    mongo_cmd = f"docker exec arogya-backend node -e \"const mongoose = require('mongoose'); (async () => {{ await mongoose.connect(process.env.DB_URL); const count = await mongoose.connection.collection('analysisjobs').countDocuments({{ idempotencyKey: '{idempotency_key}' }}); console.log('DB_COUNT:' + count); process.exit(0); }})()\""
    db_check = subprocess.run(mongo_cmd, shell=True, capture_output=True, text=True)
    db_out = db_check.stdout + db_check.stderr
    log(f"[+] MongoDB query output: {db_out.strip()}")

    if "DB_COUNT:1" not in db_out:
        log(f"[-] DATABASE VIOLATION: Expected DB_COUNT:1 in database, got: {db_out}")
        return False, "\n".join(lines)

    log("[+] DATABASE VERIFIED: Strictly exactly 1 AnalysisJob document exists for this idempotency key.\n")

    # 6. Distinct Idempotency Key Test
    log("[STEP 6] Testing distinct Idempotency-Key creates distinct job...")
    new_key = f"idem-key-distinct-{uuid.uuid4()}"
    res2 = make_request(100)
    # now send with new key
    req_headers2 = dict(headers)
    req_headers2["Idempotency-Key"] = new_key
    r2 = requests.post(url, json={"language": "en"}, headers=req_headers2, verify=False, timeout=10)
    data2 = r2.json()
    new_job_id = data2.get("job", {}).get("jobId")
    log(f"[+] New request with key {new_key} returned jobId: {new_job_id}")

    if not new_job_id or new_job_id == canonical_job_id:
        log(f"[-] Expected different jobId, got: {new_job_id}")
        return False, "\n".join(lines)

    log("[+] Verified: Distinct idempotency key generated distinct job.\n")
    log("================================================================================")
    log("RESULT: VERIFIED — HTTP-level idempotency deduplication verified under 50-way concurrency.")
    log("================================================================================")
    return True, "\n".join(lines)

if __name__ == "__main__":
    success, output = run_test()
    header = f"""================================================================================
AROGYAMITRA EVIDENCE — PHASE P3.8 HTTP IDEMPOTENCY DEDUPLICATION TEST
Date: {datetime.datetime.now(datetime.timezone.utc).isoformat()}
Git Commit: fa04225 (working tree: dirty)
Command: python scripts/test_p3_idempotency_http.py
================================================================================

"""
    with open("docs/evidence/p3_idempotency_http.txt", "w", encoding="utf-8") as f:
        f.write(header + output)

    if not success:
        sys.exit(1)
    print("\nEvidence saved to docs/evidence/p3_idempotency_http.txt")
