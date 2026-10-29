# Concurrency & Asynchronous Job Pipeline Investigation Report

**Document Date:** October 29, 2026  
**System:** ArogyaMitra Healthcare Platform (Phase 4 / Stage 4 Completion)  
**Status:** VERIFIED & BENCHMARKED  

---

## 1. Executive Summary & Root Cause Analysis

In earlier revisions of the codebase, the concurrency test in `Backend/tests/concurrency.test.js` tested Optimistic Concurrency Control (OCC) using an in-memory javascript helper (`simulateConcurrentWrite`) that merely checked `staleDoc.__v !== currentVersion`. While Mongoose does support `{ optimisticConcurrency: true }` on collections, relying purely on OCC for background job queues has critical failure modes:
1. **Contention Storms:** When multiple background workers poll a shared queue simultaneously, OCC causes high transaction abort rates as competing workers encounter `VersionError` write collisions.
2. **Vacuous Testing Disclosure:** The previous test asserted OCC logic on an artificial JavaScript object rather than executing against concurrent asynchronous worker threads or an atomic database primitive.

To resolve this completely, Stage 4 implements **Pessimistic Atomic Job Claiming with Lease Expiry & Dead-Letter Routing** powered by MongoDB's atomic `findOneAndUpdate` primitive.

---

## 2. Architecture: Atomic Job Claim, Lease Timeouts & Dead-Letter Queue

### 2.1 The Atomic Claim Protocol (`claimNextJob`)
When a background worker requests work, it executes an atomic `findOneAndUpdate` query against `AnalysisJob`:
```javascript
const claimed = await AnalysisJob.findOneAndUpdate(
  {
    $or: [
      {
        status: "queued",
        attempts: { $lt: 3 },
        $or: [{ nextRetryAt: null }, { nextRetryAt: { $lte: now } }],
      },
      {
        status: "processing",
        leaseExpiresAt: { $lt: now },
        attempts: { $lt: 3 },
      },
    ],
  },
  {
    $set: {
      status: "processing",
      lockedAt: now,
      lockedBy: workerId,
      leaseExpiresAt: new Date(now.getTime() + leaseDurationMs),
      startedAt: now,
    },
    $inc: { attempts: 1 },
  },
  { new: true, sort: { createdAt: 1 } }
);
```

### 2.2 Key Guarantees
- **Mutual Exclusion (0 Duplicate Claims):** MongoDB guarantees that each matching document is locked and updated atomically. Even if 50 workers issue concurrent queries in the same millisecond, each document is claimed by exactly one worker.
- **Worker Crash Resilience (Lease Expiry):** Each claimed job receives a 5-minute lease (`leaseExpiresAt = now + 300,000ms`). If a worker container crashes or hangs mid-inference, the lease expires, allowing an active worker to automatically re-claim and resume the job without manual intervention.
- **Exponential Backoff:** If transient errors occur (e.g., temporary network blip to the ML or LLM service), `releaseOrRetryJob` reschedules the job with exponential backoff:
  $$\Delta t = 2^{\text{attempts}} \times 1000\text{ ms} \quad (2\text{s}, 4\text{s}, 8\text{s})$$
- **Dead-Letter State:** After 3 failed attempts (`attempts >= maxAttempts`), the job transitions to `status: "dead_letter"`, records `deadLetterReason`, and stops polling to prevent infinite loops.

---

## 3. High-Concurrency Benchmark: 50 Concurrent Worker Contention

A high-load simulation test was executed where 50 concurrent worker promises simultaneously attempted to claim jobs from a queue of 10 available records.

### Results:
| Metric | Expected Value | Observed Result | Pass / Fail |
| :--- | :--- | :--- | :--- |
| **Simulated Workers** | 50 concurrent workers | 50 concurrent promises | PASS |
| **Available Jobs** | 10 queued records | 10 queued records | PASS |
| **Successful Claims** | Exactly 10 | 10 | PASS |
| **Empty Backoff Claims** | Exactly 40 (HTTP 204 / null) | 40 | PASS |
| **Duplicate Claim Count** | Exactly 0 (Unique IDs = 10) | 0 duplicate executions | PASS |
| **Lost Updates** | Exactly 0 (All 10 in 'processing') | 0 lost updates | PASS |
| **Race Conditions Detected**| 0 | 0 | PASS |

---

## 4. Verification Evidence

All 10 tests in `Backend/tests/concurrency.test.js` pass cleanly:
```
 RUN  v5.0.5 D:/Document/Projects/Internship/Arogyamitra/Backend
 ✓ tests/concurrency.test.js (10 tests) 38ms
 Test Files  1 passed (1)
      Tests  10 passed (10)
```

