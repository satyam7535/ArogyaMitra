# Load Test Profiling & List Optimization Analysis

**Date**: 2026-10-31  
**Target Environment**: Test-mode stack with dedicated test limits (`docker-compose.test.yml`, `NODE_ENV=test`, `ALLOW_LOAD_TEST=true`)  
**Raw Test Evidence**:
- JSON: [`docs/evidence/load_test_testmode_results.json`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/load_test_testmode_results.json)
- Text Table: [`docs/evidence/load_test_testmode_results.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/load_test_testmode_results.txt)

---

## 1. Full Benchmark Performance Across Concurrency Levels (200 req/endpoint, 800 req/level)

| Concurrency Level | Total Requests | Duration (s) | Throughput (req/s) | p50 Latency (ms) | p90 Latency (ms) | p95 Latency (ms) | p99 Latency (ms) | 400s | 401s | 429s | 5xx | Status Distribution |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **C = 1** | 800 | 78.79 | 10.2 | 79.3 | 148.9 | 190.6 | 317.4 | **0** | **0** | **0** | **0** | `{200: 800}` (100.0%) |
| **C = 10** | 800 | 57.74 | 13.9 | 500.7 | 1530.1 | 1952.3 | 2548.2 | **0** | **0** | **0** | **0** | `{200: 800}` (100.0%) |
| **C = 50** | 800 | 54.31 | 14.7 | 2428.4 | 5057.2 | 5862.8 | 8087.4 | **0** | **0** | **0** | **0** | `{200: 800}` (100.0%) |

**Total Requests Executed**: 2,400  
**Total Successful (HTTP 200)**: 2,400 (100.0%)  
**Total Failures (400, 401, 429, 5xx)**: 0  

---

## 2. Per-Endpoint Status-Code Breakdown

By pre-creating exactly 200 pending escalated consultations per batch and mapping each `doctor_respond` call 1-to-1 to a distinct consultation ID, all endpoints achieved 100% HTTP 200 OK across all concurrency levels:

### Concurrency C = 1 (200 req per endpoint):
- `doctor_respond`: p50 = 73.0 ms | p90 = 116.8 ms | p95 = 128.6 ms | p99 = 244.2 ms (count = 200, **status = {200: 200}**)
- `health`: p50 = 61.5 ms | p90 = 88.5 ms | p95 = 93.9 ms | p99 = 131.7 ms (count = 200, **status = {200: 200}**)
- `submit_triage`: p50 = 135.4 ms | p90 = 256.3 ms | p95 = 299.2 ms | p99 = 392.4 ms (count = 200, **status = {200: 200}**)
- `worker_list`: p50 = 76.2 ms | p90 = 117.9 ms | p95 = 130.3 ms | p99 = 152.0 ms (count = 200, **status = {200: 200}**)

### Concurrency C = 10 (200 req per endpoint):
- `doctor_respond`: p50 = 474.3 ms | p90 = 765.0 ms | p95 = 856.6 ms | p99 = 1286.7 ms (count = 200, **status = {200: 200}**)
- `health`: p50 = 354.3 ms | p90 = 637.7 ms | p95 = 717.2 ms | p99 = 1135.1 ms (count = 200, **status = {200: 200}**)
- `submit_triage`: p50 = 1349.2 ms | p90 = 2274.1 ms | p95 = 2443.5 ms | p99 = 2863.4 ms (count = 200, **status = {200: 200}**)
- `worker_list`: p50 = 417.7 ms | p90 = 701.2 ms | p95 = 779.4 ms | p99 = 1255.3 ms (count = 200, **status = {200: 200}**)

### Concurrency C = 50 (200 req per endpoint):
- `doctor_respond`: p50 = 2183.6 ms | p90 = 4462.1 ms | p95 = 5269.6 ms | p99 = 6676.6 ms (count = 200, **status = {200: 200}**)
- `health`: p50 = 2412.6 ms | p90 = 4734.2 ms | p95 = 5576.5 ms | p99 = 8168.2 ms (count = 200, **status = {200: 200}**)
- `submit_triage`: p50 = 3050.5 ms | p90 = 6242.4 ms | p95 = 6729.9 ms | p99 = 9930.8 ms (count = 200, **status = {200: 200}**)
- `worker_list`: p50 = 2295.1 ms | p90 = 4834.6 ms | p95 = 5468.1 ms | p99 = 7047.0 ms (count = 200, **status = {200: 200}**)

---

## 3. Worker List Optimization: Before vs. After Benchmark

### Optimization Implemented:
1. **Pagination**: Added `page` and `limit` query parameters (defaulting to 20, clamped between 1 and 100) to `GET /api/v1/consultation/my`.
2. **Projection**: Added explicit MongoDB field projection `.select("patient assignedDoctor symptoms status decisionOutcome notes mlAnalysis.disease mlAnalysis.confidence mlAnalysis.needsEscalation mlAnalysis.redFlag createdAt updatedAt")` to eliminate hydration and cryptographic decryption of unneeded fields.

### Empirical Before vs. After Latency Comparison (Concurrency C = 1):

| Metric | Before (Unpaginated Full Scan) | After (Paginated `limit=20` + Projection) | Latency Improvement |
|---|---|---|---|
| **p50 Latency** | 193.0 ms | **76.2 ms** | **60.5% faster** |
| **p90 Latency** | 349.8 ms | **117.9 ms** | **66.3% faster** |
| **p95 Latency** | 460.5 ms | **130.3 ms** | **71.7% faster** |
| **p99 Latency** | 660.6 ms | **152.0 ms** | **77.0% faster** |

### Analysis of Dominating Factors:
- **Hypothesis**: The earlier analysis hypothesized that synchronous AES-256-GCM decryption during Mongoose document hydration across unpaginated datasets was the primary cause of high list latency.
- **Empirical Assessment**: The dramatic **60% to 77% latency reduction** across all percentiles after implementing pagination and projection supports this hypothesis. Restricting document hydration and field decryption to the requested 20-item window prevents the Node.js event loop from being blocked by bulk symmetric decryption of hundreds of historical patient records.

---

## 4. Triage Latency Empirical Breakdown

Empirical profiling measured in-container inference and synthesis components:
1. **ML Bayesian Inference (`FastAPI :8000` via internal network)**: **1.8 ms** (1.4% of total triage latency)
2. **Devanagari PDF ReportLab Synthesis (CPU bound)**: **63.0 ms** (50.4% of total triage latency)
3. **Network Ingress, Express Middleware, DB Overhead**: **60.2 ms** (48.2% of total triage latency)
4. **Total End-to-End Triage Latency (LLM Off / Fallback)**: **125.0 ms** (100.0%)

*Note on Gemini LLM Latency*: When the LLM is active, network round-trip time to Gemini 2.5 Flash is external. Due to upstream API quota limits, LLM latency is marked as "not measured".

