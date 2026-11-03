"""
ArogyaMitra P5.3 HTTP-Level Atomic Race Tests
Tests real concurrency through the Express HTTP API with MongoDB in Docker.
1. Test 1: 50 concurrent PATCH requests accepting the SAME consultation with different notes.
   Expected: exactly 1 returns 200, 49 return 409.
2. Test 2: 50 concurrent requests (25 accept, 25 escalate) on the SAME consultation.
   Expected: exactly 1 succeeds (200), 49 return 409.
"""

import concurrent.futures
import datetime
import json
import subprocess
import time
import urllib3
import requests

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://localhost/api/v1"

def get_git_info():
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    status = subprocess.check_output(["git", "status", "--porcelain"], text=True).strip()
    dirty = "DIRTY" if status else "CLEAN"
    date = datetime.datetime.now(datetime.timezone.utc).isoformat()
    return commit, dirty, date

def get_seeded_doctor_id():
    out = subprocess.check_output([
        "docker", "exec", "arogya-mongo", "mongosh", "arogyamitra",
        "--quiet", "--eval", "db.doctors.findOne({}, {_id: 1})._id.toString()"
    ], text=True).strip()
    return out

def main():
    commit, dirty, date = get_git_info()
    doctor_id = get_seeded_doctor_id()
    
    out = []
    out.append("# EVIDENCE RECORD: P5.3 HTTP-Level Atomic Race Tests")
    out.append("# COMMAND: python scripts/test_p5_race_suite.py")
    out.append(f"# DATE: {date}")
    out.append(f"# COMMIT: {commit}")
    out.append(f"# STATUS: {dirty}")
    out.append("# TARGET: https://localhost/api/v1 (Docker Nginx + Express + MongoDB)")
    out.append(f"# SEEDED DOCTOR ID: {doctor_id}")
    out.append("# -------------------------------------------------------------\n")
    
    session = requests.Session()
    session.verify = False
    
    # Authenticate as Worker
    login_res = session.post(f"{BASE_URL}/worker/login", json={
        "email": "worker@arogyamitra.gov.in",
        "password": "Worker@Arogya2026!"
    }, timeout=10)
    token = login_res.json().get("accessToken") or login_res.json().get("token")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # -------------------------------------------------------------------------
    # TEST 1: 50 Concurrent Accept Requests on the SAME Consultation
    # -------------------------------------------------------------------------
    out.append("### TEST 1: 50 Concurrent Accept Requests on Single Consultation")
    
    # Register Patient
    phone_t1 = f"9821{int(time.time()) % 1000000:06d}"
    p1 = session.post(f"{BASE_URL}/patient", json={
        "name": f"Race Subject Alpha {phone_t1}",
        "age": 30,
        "gender": "Male",
        "phoneNumber": phone_t1,
        "address": "Primary Health Centre Subcenter A",
        "consentGiven": True,
        "consentLanguage": "en"
    }, headers=headers).json()
    p1_id = p1.get("patient", {}).get("_id") or p1.get("data", {}).get("_id") or p1.get("_id")
    
    c1 = session.post(f"{BASE_URL}/consultation", json={
        "patientId": p1_id,
        "symptoms": ["headache", "mild_fever", "fatigue"],
        "notes": "Testing atomic accept race condition"
    }, headers=headers).json()
    c1_doc = c1.get("consultation") or c1.get("data") or c1
    c1_id = c1_doc.get("_id")
    c1_ver = c1_doc.get("__v", 0)
    
    out.append(f"Created Target Consultation: {c1_id} (Initial __v: {c1_ver}, status: {c1_doc.get('status')})")
    out.append("Firing 50 parallel accept requests simultaneously...")
    
    def exec_accept(idx):
        payload = {
            "notes": f"Worker accept decision thread #{idx:02d}",
            "version": c1_ver
        }
        r = requests.patch(
            f"{BASE_URL}/consultation/{c1_id}/accept",
            json=payload,
            headers=headers,
            verify=False,
            timeout=15
        )
        return idx, r.status_code, r.text
        
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(exec_accept, i) for i in range(50)]
        t1_results = [f.result() for f in futures]
        
    t1_status_counts = {}
    for idx, sc, txt in t1_results:
        t1_status_counts[sc] = t1_status_counts.get(sc, 0) + 1
        
    out.append(f"Test 1 HTTP Status Distribution: {t1_status_counts}")
    success_200_count = t1_status_counts.get(200, 0)
    conflict_409_count = t1_status_counts.get(409, 0)
    out.append(f"200 OK (Winner): {success_200_count}")
    out.append(f"409 Conflict (Losers): {conflict_409_count}")
    
    winner_t1 = next((res for res in t1_results if res[1] == 200), None)
    loser_sample_t1 = next((res for res in t1_results if res[1] == 409), None)
    
    if winner_t1:
        out.append(f"Winning Response (Thread #{winner_t1[0]}): {winner_t1[2][:160]}")
    if loser_sample_t1:
        out.append(f"Sample Conflict Response (Thread #{loser_sample_t1[0]}): {loser_sample_t1[2][:160]}")
        
    test1_passed = (success_200_count == 1 and conflict_409_count == 49)
    out.append(f"TEST 1 RESULT: {'PASS' if test1_passed else 'FAIL'} (Expected 1x 200, 49x 409)\n")
    
    # -------------------------------------------------------------------------
    # TEST 2: 50 Concurrent Requests (25 Accept vs 25 Escalate)
    # -------------------------------------------------------------------------
    out.append("### TEST 2: 50 Concurrent Mixed Requests (25 Accept vs 25 Escalate)")
    
    phone_t2 = f"9822{int(time.time()) % 1000000:06d}"
    p2 = session.post(f"{BASE_URL}/patient", json={
        "name": f"Race Subject Beta {phone_t2}",
        "age": 42,
        "gender": "Female",
        "phoneNumber": phone_t2,
        "address": "Community Health Centre Ward 3",
        "consentGiven": True,
        "consentLanguage": "en"
    }, headers=headers).json()
    p2_id = p2.get("patient", {}).get("_id") or p2.get("data", {}).get("_id") or p2.get("_id")
    
    c2 = session.post(f"{BASE_URL}/consultation", json={
        "patientId": p2_id,
        "symptoms": ["chest_pain", "shortness_of_breath"],
        "notes": "Testing accept vs escalate concurrency conflict"
    }, headers=headers).json()
    c2_doc = c2.get("consultation") or c2.get("data") or c2
    c2_id = c2_doc.get("_id")
    c2_ver = c2_doc.get("__v", 0)
    
    out.append(f"Created Target Consultation: {c2_id} (Initial __v: {c2_ver}, status: {c2_doc.get('status')})")
    out.append("Firing 25 accept and 25 escalate requests simultaneously (50 total)...")
    
    def exec_mixed(idx):
        if idx % 2 == 0:
            # Accept request
            payload = {
                "notes": f"Worker accept decision #{idx:02d}",
                "version": c2_ver
            }
            r = requests.patch(
                f"{BASE_URL}/consultation/{c2_id}/accept",
                json=payload,
                headers=headers,
                verify=False,
                timeout=15
            )
            return idx, "accept", r.status_code, r.text
        else:
            # Escalate request
            payload = {
                "doctorId": doctor_id,
                "reason": f"Clinical uncertainty thread #{idx:02d}",
                "version": c2_ver
            }
            r = requests.patch(
                f"{BASE_URL}/consultation/{c2_id}/escalate",
                json=payload,
                headers=headers,
                verify=False,
                timeout=15
            )
            return idx, "escalate", r.status_code, r.text
            
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(exec_mixed, i) for i in range(50)]
        t2_results = [f.result() for f in futures]
        
    t2_status_counts = {}
    for idx, kind, sc, txt in t2_results:
        t2_status_counts[sc] = t2_status_counts.get(sc, 0) + 1
        
    out.append(f"Test 2 HTTP Status Distribution: {t2_status_counts}")
    success_200_count_2 = t2_status_counts.get(200, 0)
    conflict_409_count_2 = t2_status_counts.get(409, 0)
    out.append(f"200 OK (Winner): {success_200_count_2}")
    out.append(f"409 Conflict (Losers): {conflict_409_count_2}")
    
    winner_t2 = next((res for res in t2_results if res[2] == 200), None)
    loser_sample_t2 = next((res for res in t2_results if res[2] == 409), None)
    
    if winner_t2:
        out.append(f"Winning Action: {winner_t2[1].upper()} (Thread #{winner_t2[0]}): {winner_t2[3][:160]}")
    if loser_sample_t2:
        out.append(f"Sample Conflict Response ({loser_sample_t2[1].upper()} Thread #{loser_sample_t2[0]}): {loser_sample_t2[3][:160]}")
        
    test2_passed = (success_200_count_2 == 1 and conflict_409_count_2 == 49)
    out.append(f"TEST 2 RESULT: {'PASS' if test2_passed else 'FAIL'} (Expected 1x 200, 49x 409)\n")
    
    report = "\n".join(out)
    print(report)
    with open("docs/evidence/http_race_tests.txt", "w", encoding="utf-8") as f:
        f.write(report)
        
    if test1_passed and test2_passed:
        print("\nAll P5.3 atomic race tests passed with exact 1-winner / 49-conflict verification.")
    else:
        print("\nTest failed to achieve exact 1/49 distribution.")

if __name__ == "__main__":
    main()

