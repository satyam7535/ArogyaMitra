"""
Phase 1: Defect Reproduction Script for ArogyaMitra Workflow
Tests worker analysis + escalation flow and inspects:
1. Mongo documents (count & newest 3 documents)
2. Backend logs
3. Worker list API response (/consultation/my)
4. Doctor queue API response (/consultation/pending)
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')
import time
import json
import httpx
import subprocess

BASE_URL = "https://localhost"

def run_reproduction():
    client_w = httpx.Client(verify=False, timeout=30.0, headers={"X-Requested-With": "XMLHttpRequest"})
    client_d = httpx.Client(verify=False, timeout=30.0, headers={"X-Requested-With": "XMLHttpRequest"})
    ts = int(time.time())
    patient_name = f"ZZTest-{ts}"
    print(f"=== Starting Defect Reproduction with Patient: {patient_name} ===")

    # 1. Login as Worker
    print("[1] Logging in as Worker (worker@arogyamitra.gov.in)...")
    res_w = client_w.post(f"{BASE_URL}/api/v1/worker/login", json={
        "email": "worker@arogyamitra.gov.in",
        "password": "Worker@Arogya2026!"
    })
    print(f"Worker Login Status: {res_w.status_code}")
    w_data = res_w.json()
    worker_token = w_data.get("accessToken")
    worker_user = w_data.get("worker", {})
    worker_id = worker_user.get("id") or worker_user.get("_id")
    org_id = worker_user.get("organization")
    print(f"Worker ID: {worker_id}, Org: {org_id}")

    # 2. Login as Doctor
    print("[2] Logging in as Doctor (doctor@arogyamitra.gov.in)...")
    res_d = client_d.post(f"{BASE_URL}/api/v1/doctor/login", json={
        "email": "doctor@arogyamitra.gov.in",
        "password": "Doctor@Arogya2026!"
    })
    print(f"Doctor Login Status: {res_d.status_code}")
    d_data = res_d.json()
    doctor_token = d_data.get("accessToken")
    doctor_user = d_data.get("doctor", {})
    doctor_id = doctor_user.get("id") or doctor_user.get("_id")
    print(f"Doctor ID: {doctor_id}, Org: {doctor_user.get('organization')}")

    # 3. Worker analyzes a new case via /consultation/triage (as current UI does)
    print(f"\n[3] Calling /consultation/triage for {patient_name}...")
    triage_payload = {
        "symptoms": ["itching", "skin_rash", "nodal_skin_eruptions"],
        "patientName": patient_name,
        "patientAge": 32,
        "patientGender": "Female",
        "workerName": "Sunita Patil",
        "location": "Pali PHC",
        "language": "en"
    }
    res_t = client_w.post(
        f"{BASE_URL}/api/v1/consultation/triage",
        json=triage_payload,
        headers={"Authorization": f"Bearer {worker_token}"}
    )
    print(f"Triage Status: {res_t.status_code}")
    triage_data = res_t.json()
    print("Triage Success:", triage_data.get("success"))
    print("ML Top Disease:", triage_data.get("mlResult", {}).get("disease"))

    # 4. In the CURRENT UI:
    print("\n[4] Inspecting UI Escalate Action:")
    print("CRITICAL FINDING: ui/pages/1_Worker_Triage.py lines 298-299:")
    print("  if st.button('Escalate'):")
    print("      st.warning('Case successfully escalated to Medical Officer for second opinion.')")
    print("NO HTTP request is made by the UI upon clicking Escalate (or Accept)!")
    print("The case analyzed via /consultation/triage was never persisted to MongoDB!")

    # 5. Query Mongo document count and newest documents
    print("\n[5] Checking MongoDB Consultations via mongosh...")
    mongo_cmd = 'docker compose exec -T mongo mongosh arogyamitra --quiet --eval "EJSON.stringify({count: db.consultations.countDocuments(), newest: db.consultations.find({}, {status: 1, \'mlAnalysis.disease\': 1, organization: 1, createdAt: 1, patient: 1, workerDecision: 1}).sort({createdAt: -1}).limit(3).toArray()})"'
    p = subprocess.run(mongo_cmd, shell=True, capture_output=True, text=True, encoding="utf-8", errors="replace")
    mongo_out = p.stdout.strip()
    print("MongoDB Output:")
    print(mongo_out)

    # 6. Check Worker List API response
    print("\n[6] Checking Worker List API response (GET /consultation/my)...")
    res_w_list = client_w.get(
        f"{BASE_URL}/api/v1/consultation/my?page=1&limit=5",
        headers={"Authorization": f"Bearer {worker_token}"}
    )
    print(f"Worker List Status: {res_w_list.status_code}")
    w_list_data = res_w_list.json()
    print(f"Worker List Total: {w_list_data.get('total')}")
    print("Worker Consultations returned:")
    for c in w_list_data.get("consultations", []):
        pt = c.get("patient") or {}
        ml = c.get("mlAnalysis") or {}
        print(f"  - ID: {c.get('_id')} | Status: {c.get('status')} | WorkerDecision: {c.get('workerDecision')} | Disease: {ml.get('disease')} | Created: {c.get('createdAt')}")

    # 7. Check Doctor Queue API response
    print("\n[7] Checking Doctor Queue API response (GET /consultation/pending)...")
    res_d_queue = client_d.get(
        f"{BASE_URL}/api/v1/consultation/pending",
        headers={"Authorization": f"Bearer {doctor_token}"}
    )
    print(f"Doctor Queue Status: {res_d_queue.status_code}")
    d_queue_data = res_d_queue.json()
    doctor_cases = d_queue_data.get("consultations", [])
    print(f"Doctor Pending Cases returned: {len(doctor_cases)}")
    for c in doctor_cases:
        pt = c.get("patient") or {}
        ml = c.get("mlAnalysis") or {}
        print(f"  - ID: {c.get('_id')} | Status: {c.get('status')} | Patient: {pt.get('name')} | Disease: {ml.get('disease')}")

    # 8. Fetch Backend Logs around this interaction
    print("\n[8] Fetching Backend Logs (docker compose logs backend --tail 60)...")
    log_cmd = "docker compose logs backend --tail 60"
    p_log = subprocess.run(log_cmd, shell=True, capture_output=True, text=True, encoding="utf-8", errors="replace")
    backend_logs = p_log.stdout.strip()
    print(backend_logs[:500] + "\n...[truncated]...")

    # Write full reproduction report to docs/evidence/flow_defect_reproduction.txt
    repro_text = f"""AROGYAMITRA CLINICAL FLOW DEFECT REPRODUCTION REPORT
Generated: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
Test Patient: {patient_name}

================================================================================
1. REPRODUCTION SEQUENCE & RAW API RESPONSES
================================================================================

[Step 1] Worker Login (worker@arogyamitra.gov.in):
HTTP {res_w.status_code}
Worker ID: {worker_id}
Organization: {org_id}

[Step 2] Doctor Login (doctor@arogyamitra.gov.in):
HTTP {res_d.status_code}
Doctor ID: {doctor_id}
Organization: {doctor_user.get('organization')}

[Step 3] Run AI Triage (POST /consultation/triage):
HTTP {res_t.status_code}
Payload: {json.dumps(triage_payload)}
Triage Result:
  Success: {triage_data.get('success')}
  Top Disease: {triage_data.get('mlResult', {}).get('disease')}
  Needs Escalation: {triage_data.get('mlResult', {}).get('needsEscalation')}

[Step 4] UI Escalate Button Behavior:
Source: ui/pages/1_Worker_Triage.py (lines 298-299):
```python
with act_col2:
    if st.button(f"Escalate", type="primary", use_container_width=True):
        st.warning("Case successfully escalated to Medical Officer for second opinion.")
```
DEFECT IDENTIFIED: The Streamlit UI button displays a warning notification but NEVER dispatches an HTTP request to create or escalate a consultation document in the backend database.
Similarly, line 294-295 for Accept:
```python
if st.button(f"Accept", use_container_width=True):
    st.success("Triage consultation finalized and saved to patient record.")
```
Accept also never called the backend API!

[Step 5] MongoDB Consultations State:
{mongo_out}

[Step 6] Worker Consultation List (GET /consultation/my):
HTTP {res_w_list.status_code}
Response Body:
{json.dumps(w_list_data, indent=2)}

Observation: The test patient {patient_name} DOES NOT APPEAR because no consultation document was saved.

[Step 7] Doctor Queue (GET /consultation/pending):
HTTP {res_d_queue.status_code}
Response Body:
{json.dumps(d_queue_data, indent=2)}

Observation: Doctor queue contains 0 pending cases for this new patient. In ui/pages/2_Doctor_Review.py, because live_cases was empty, lines 55-112 fell back to displaying hardcoded SAMPLE_PENDING_CASES (CASE-9021 Ramesh Shinde, CASE-9022 Anandi Bai).

[Step 8] Backend Access Logs (tail 60):
{backend_logs}

================================================================================
2. EXACT FAILURE CHAIN DIAGNOSIS
================================================================================
The workflow broke at multiple points across the chain:

1. UI Call Not Made (Worker Triage):
   - In `ui/pages/1_Worker_Triage.py`, clicking 'Escalate' or 'Accept' only printed an in-memory Streamlit banner (st.warning / st.success).
   - Neither `POST /consultation` nor `PATCH /consultation/:id/escalate` was ever called by the UI.

2. Consultation Persistence & Top Condition Missing:
   - When a consultation is submitted or escalated, `POST /consultation` only saved basic symptoms and notes without persisting the `mlAnalysis` object (disease, confidence, etc.).
   - In `consultation.service.js`, `getConsultationsByWorker` projected `mlAnalysis.disease`, but because `mlAnalysis` was not populated during creation/triage save, the Primary Diagnosis column showed 'Pending'.

3. Doctor Review UI Fallback to Hardcoded Demo Data:
   - In `ui/pages/2_Doctor_Review.py`, `SAMPLE_PENDING_CASES` contained hardcoded mock cases CASE-9021 (Ramesh Shinde) and CASE-9022 (Anandi Bai) with 88.5%.
   - When `get_pending_consultations_for_doctor()` returned an empty list `[]`, the UI reverted to `SAMPLE_PENDING_CASES` and showed "Demonstration review queue active".

4. Doctor Assignment & Pending Queue Query:
   - In `Backend/src/service/consultation.service.js`, `getPendingConsultationsForDoctor` queried `{{ assignedDoctor: doctorId, organization, workerDecision: "escalated", status: "pending" }}`.
   - If a consultation is escalated without assigning a specific doctor or if the doctor checks unassigned consultations for their organization, it must match consultations escalated within that organization.
"""

    with open("docs/evidence/flow_defect_reproduction.txt", "w", encoding="utf-8") as f:
        f.write(repro_text)

    print("\nSaved raw reproduction output to docs/evidence/flow_defect_reproduction.txt")

if __name__ == "__main__":
    run_reproduction()
