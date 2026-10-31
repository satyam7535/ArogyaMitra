"""
ArogyaMitra — Load & Concurrency Benchmark Suite (Test Mode Stack)
Executes realistic load against https://localhost (Nginx Ingress Proxy):
- Exercises: Login, List Consultations, Submit & Analyze (Triage), Doctor Respond
- Uses dedicated test compose override (NODE_ENV=test, test-only limits, LLM off)
- Pre-creates 1 pending escalated consultation per doctor respond request
- Measures latency percentiles (p50, p90, p95, p99) and strictly counts 401 and 429 as failures
- Profiles triage latency breakdown across ML inference, PDF generation, and network/middleware
"""

import os
import sys
import time
import json
import statistics
import concurrent.futures
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://localhost"

def create_session():
    session = requests.Session()
    session.verify = False
    session.headers.update({"X-Requested-With": "XMLHttpRequest"})
    return session

def get_tokens():
    session = create_session()

    # 1. Login Worker
    res_worker = session.post(f"{BASE_URL}/api/v1/worker/login", json={
        "email": "worker@arogyamitra.gov.in",
        "password": "Worker@Arogya2026!"
    }, timeout=10)
    res_worker_json = res_worker.json()
    worker_token = res_worker_json.get("accessToken")

    # 2. Login Doctor
    res_doc = session.post(f"{BASE_URL}/api/v1/doctor/login", json={
        "email": "doctor@arogyamitra.gov.in",
        "password": "Doctor@Arogya2026!"
    }, timeout=10)
    res_doc_json = res_doc.json()
    doctor_token = res_doc_json.get("accessToken")
    doctor_id = res_doc_json.get("doctor", {}).get("id")

    if not worker_token or not doctor_token:
        raise RuntimeError(f"Authentication failed. Worker: {res_worker.status_code}, Doctor: {res_doc.status_code}")

    return worker_token, doctor_token, doctor_id

def pre_create_pending_consultations(count, worker_token, doctor_id):
    session = create_session()
    headers_w = {"Authorization": f"Bearer {worker_token}", "Content-Type": "application/json"}
    
    # Get patients list
    res_pat = session.get(f"{BASE_URL}/api/v1/patient/", headers=headers_w, timeout=10)
    patients = res_pat.json().get("patients", [])
    if patients:
        patient_id = patients[0]["_id"]
    else:
        res_create_pat = session.post(f"{BASE_URL}/api/v1/patient/", headers=headers_w, json={
            "name": "Load Test Patient",
            "age": 42,
            "gender": "male",
            "phoneNumber": "9998887776",
            "location": "Ward 4",
            "consentGiven": True
        }, timeout=10)
        patient_id = res_create_pat.json().get("patient", {}).get("_id")

    created_ids = []
    print(f"Pre-creating {count} pending escalated consultations for doctor respond benchmark...")
    for i in range(count):
        res = session.post(f"{BASE_URL}/api/v1/consultation/", headers=headers_w, json={
            "patientId": patient_id,
            "symptoms": ["chills", "vomiting", "high_fever"]
        }, timeout=10)
        if res.status_code in (200, 201):
            c_id = res.json().get("consultation", {}).get("_id")
            if c_id:
                # Escalate to doctor so it enters pending state for that doctor
                res_esc = session.patch(f"{BASE_URL}/api/v1/consultation/{c_id}/escalate", headers=headers_w, json={
                    "doctorId": doctor_id,
                    "reason": "Escalating for review under load test"
                }, timeout=10)
                if res_esc.status_code in (200, 201):
                    created_ids.append(c_id)
        time.sleep(0.01)

    print(f"Successfully created & escalated {len(created_ids)} pending consultations.")
    return created_ids

def run_single_request(req_type, worker_token, doctor_token, consultation_id=None):
    session = create_session()
    start = time.perf_counter()
    status_code = 0
    err = None

    try:
        if req_type == "health":
            res = session.get(f"{BASE_URL}/health", timeout=15)
            status_code = res.status_code
        elif req_type == "worker_list":
            headers = {"Authorization": f"Bearer {worker_token}"}
            res = session.get(f"{BASE_URL}/api/v1/consultation/my", headers=headers, timeout=15)
            status_code = res.status_code
        elif req_type == "submit_triage":
            headers = {"Authorization": f"Bearer {worker_token}", "Content-Type": "application/json"}
            res = session.post(f"{BASE_URL}/api/v1/consultation/triage", headers=headers, json={
                "symptoms": ["chills", "vomiting", "high_fever", "sweating", "headache"]
            }, timeout=30)
            status_code = res.status_code
        elif req_type == "doctor_respond":
            headers = {"Authorization": f"Bearer {doctor_token}", "Content-Type": "application/json"}
            target_id = consultation_id or "000000000000000000000000"
            res = session.patch(f"{BASE_URL}/api/v1/consultation/{target_id}/respond", headers=headers, json={
                "diagnosis": "Malaria Confirmed",
                "recommendation": "Prescribe standard antimalarial regimen.",
                "doctorNotes": "Reviewed clinical indicators and verified blood smear necessity.",
                "diagnosisConfirmed": True
            }, timeout=15)
            status_code = res.status_code
    except Exception as exc:
        err = str(exc)

    elapsed_ms = (time.perf_counter() - start) * 1000.0
    return {
        "type": req_type,
        "status_code": status_code,
        "elapsed_ms": elapsed_ms,
        "error": err
    }

def run_concurrency_batch(concurrency_level, total_requests, worker_token, doctor_token, pending_ids):
    print(f"\n========================================================")
    print(f"BENCHMARK: Concurrency = {concurrency_level} users, Total Requests = {total_requests}")
    print(f"========================================================")

    # Distribute request types across workload:
    # 25% health, 25% list, 25% triage, 25% doctor respond
    work_items = []
    pending_idx = 0
    for i in range(total_requests):
        mod = i % 4
        if mod == 0:
            work_items.append(("health", None))
        elif mod == 1:
            work_items.append(("worker_list", None))
        elif mod == 2:
            work_items.append(("submit_triage", None))
        elif mod == 3:
            c_id = pending_ids[pending_idx % len(pending_ids)] if pending_ids else None
            work_items.append(("doctor_respond", c_id))
            pending_idx += 1

    results = []
    batch_start = time.perf_counter()

    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency_level) as executor:
        futures = [
            executor.submit(run_single_request, r_type, worker_token, doctor_token, c_id)
            for r_type, c_id in work_items
        ]
        for f in concurrent.futures.as_completed(futures):
            results.append(f.result())

    total_duration_s = time.perf_counter() - batch_start
    throughput = len(results) / total_duration_s if total_duration_s > 0 else 0

    # Aggregate metrics
    latencies = [r["elapsed_ms"] for r in results]
    latencies.sort()

    status_counts = {}
    for r in results:
        code = r["status_code"]
        status_counts[code] = status_counts.get(code, 0) + 1

    failures_401 = status_counts.get(401, 0)
    failures_429 = status_counts.get(429, 0)
    failures_5xx = sum(v for k, v in status_counts.items() if isinstance(k, int) and k >= 500)
    failures_err = sum(1 for r in results if r["error"] is not None)

    p50 = statistics.median(latencies)
    p90 = latencies[int(len(latencies) * 0.90)]
    p95 = latencies[int(len(latencies) * 0.95)]
    p99 = latencies[min(len(latencies) - 1, int(len(latencies) * 0.99))]

    print(f"Summary for Concurrency = {concurrency_level}:")
    print(f"  Duration:         {total_duration_s:.2f} s")
    print(f"  Throughput:       {throughput:.1f} req/s")
    print(f"  Latency p50:      {p50:.1f} ms")
    print(f"  Latency p90:      {p90:.1f} ms")
    print(f"  Latency p95:      {p95:.1f} ms")
    print(f"  Latency p99:      {p99:.1f} ms")
    print(f"  Status Codes:     {status_counts}")
    print(f"  Failures (401):   {failures_401} (Auth failures)")
    print(f"  Failures (429):   {failures_429} (Rate limit rejections)")
    print(f"  Failures (5xx):   {failures_5xx}")
    print(f"  Exceptions:       {failures_err}")

    # Endpoint breakdown
    endpoint_types = set(r["type"] for r in results)
    print(f"  Per-Endpoint Latencies (p50 / p95):")
    endpoint_stats = {}
    for et in sorted(endpoint_types):
        elats = [r["elapsed_ms"] for r in results if r["type"] == et]
        elats.sort()
        ep50 = statistics.median(elats)
        ep95 = elats[int(len(elats) * 0.95)] if len(elats) >= 20 else elats[-1]
        print(f"    - {et:<15}: p50={ep50:.1f}ms, p95={ep95:.1f}ms (count={len(elats)})")
        endpoint_stats[et] = {"p50_ms": round(ep50, 1), "p95_ms": round(ep95, 1), "count": len(elats)}

    return {
        "concurrency": concurrency_level,
        "total_requests": total_requests,
        "duration_s": round(total_duration_s, 2),
        "throughput_rps": round(throughput, 1),
        "latencies_ms": {
            "p50": round(p50, 1),
            "p90": round(p90, 1),
            "p95": round(p95, 1),
            "p99": round(p99, 1),
        },
        "status_codes": status_counts,
        "failures": {
            "auth_401": failures_401,
            "rate_limit_429": failures_429,
            "server_5xx": failures_5xx,
            "exceptions": failures_err
        },
        "endpoints": endpoint_stats
    }

def profile_triage_latency_breakdown(worker_token):
    print(f"\n========================================================")
    print(f"PROFILING: Triage Latency Breakdown (~3s Investigation)")
    print(f"========================================================")

    session = create_session()
    symptoms = ["chills", "vomiting", "high_fever", "sweating", "headache"]

    # 1. Measure direct ML Model inference
    sys.path.insert(0, os.path.abspath("ML_Model"))
    from app import run_prediction, PredictRequest
    ml_times = []
    for _ in range(10):
        t0 = time.perf_counter()
        _ = run_prediction(PredictRequest(symptoms=symptoms))
        ml_times.append((time.perf_counter() - t0) * 1000.0)

    # 2. Measure Devanagari PDF Generation duration directly
    sys.path.insert(0, os.path.abspath("graph"))
    from utils.pdf_generator import generate_pdf
    
    mock_consultation = {
        "consultation_id": "60c72b2f9b1d8b2bad000001",
        "created_at": "2026-10-31T12:00:00.000Z",
        "patient_name": "Test Patient",
        "patient_age": 35,
        "patient_gender": "female",
        "worker_name": "Worker Rekha",
        "location": "Ward 4",
        "symptoms": symptoms,
        "disease": "Malaria",
        "confidence": 0.885,
        "severity": 3.2,
        "precautions": ["Rest", "Drink boiled water", "Use bed net"],
        "shap_explanation": [
            {"symptom": "chills", "contribution": 0.45},
            {"symptom": "high_fever", "contribution": 0.38}
        ],
        "diagnosis_summary": "Malaria indicators present with calibrated probability estimate.",
        "recommended_next_steps": "Immediate referral to PHC.",
        "llm_fallback": True
    }
    
    pdf_times = []
    for _ in range(5):
        t0 = time.perf_counter()
        _ = generate_pdf(mock_consultation)
        pdf_times.append((time.perf_counter() - t0) * 1000.0)

    # 3. Measure End-to-End Triage Endpoint via Ingress Proxy
    headers = {"Authorization": f"Bearer {worker_token}", "Content-Type": "application/json"}
    e2e_times = []
    for _ in range(5):
        t0 = time.perf_counter()
        r = session.post(f"{BASE_URL}/api/v1/consultation/triage", headers=headers, json={"symptoms": symptoms}, timeout=15)
        e2e_times.append((time.perf_counter() - t0) * 1000.0)

    avg_ml = statistics.mean(ml_times)
    avg_pdf = statistics.mean(pdf_times)
    avg_e2e = statistics.mean(e2e_times)
    network_db_overhead = max(0.0, avg_e2e - (avg_ml + avg_pdf))

    print(f"Empirical Timing Measurements (Average of trials):")
    print(f"  1. ML Bayesian Inference (FastAPI :8000 via Proxy):    {avg_ml:.1f} ms ({avg_ml/avg_e2e*100:.1f}%)")
    print(f"  2. Devanagari PDF ReportLab Synthesis (CPU):           {avg_pdf:.1f} ms ({avg_pdf/avg_e2e*100:.1f}%)")
    print(f"  3. Network Ingress, Express Middleware, DB Overhead:    {network_db_overhead:.1f} ms ({network_db_overhead/avg_e2e*100:.1f}%)")
    print(f"  -------------------------------------------------------------")
    print(f"  Total End-to-End Triage Latency (LLM Off / Fallback):  {avg_e2e:.1f} ms (100.0%)")

    return {
        "avg_ml_ms": round(avg_ml, 1),
        "avg_pdf_ms": round(avg_pdf, 1),
        "avg_e2e_ms": round(avg_e2e, 1),
        "overhead_ms": round(network_db_overhead, 1)
    }

if __name__ == "__main__":
    print("ArogyaMitra Load Benchmark Runner Starting...")
    worker_tok, doc_tok, doc_id = get_tokens()
    print("Worker and Doctor authentication verified successfully.")

    # Pre-create pending consultations for doctor respond tests
    pending_ids = pre_create_pending_consultations(75, worker_tok, doc_id)

    bench_results = []
    for c, n in [(1, 20), (10, 50), (50, 100)]:
        r = run_concurrency_batch(c, n, worker_tok, doc_tok, pending_ids)
        bench_results.append(r)

    profiling = profile_triage_latency_breakdown(worker_tok)

    report = {
        "benchmark_results": bench_results,
        "latency_profiling": profiling
    }

    with open("docs/evidence/load_test_testmode_results.json", "w") as f:
        json.dump(report, f, indent=2)

    print("\nBenchmark and Profiling complete. Results written to docs/evidence/load_test_testmode_results.json")
