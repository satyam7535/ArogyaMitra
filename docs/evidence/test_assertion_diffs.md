# ArogyaMitra — Test Assertion Diffs & Architectural Invariants

This document details the exact changes and test assertions added across the test suite during the remediation and hardening process. It also formally documents the architectural resolution and distinction between HTTP 400 Bad Request and HTTP 409 Conflict.

---

## 1. Architectural Justification: HTTP 400 Bad Request vs HTTP 409 Conflict

In the consultation review workflow (`PATCH /api/v1/consultation/:id/respond`), double-processing attempts can manifest in two distinct operational scenarios: **sequential re-processing** and **concurrent race conditions**. ArogyaMitra explicitly distinguishes between these two states to provide precise, standards-compliant HTTP status codes.

### Scenario A: Sequential Double Accept -> HTTP 400 Bad Request
- **Context**: A client submits a response (accept/override) to a consultation that has **already completed** its lifecycle transition in a prior, committed transaction.
- **Root Cause**: The resource is in an invalid state (`status !== "pending"`). For example, the status is already `"accepted"`, `"rejected"`, or `"referred"`.
- **Handling**: The domain logic checks `consultation.status === "pending"`. Because the document is already in a terminal/resolved state, the request violates domain business rules (an invalid state machine transition).
- **HTTP Code**: **400 Bad Request** (`{"error": "Invalid status transition", "message": "Consultation has already been processed and is no longer pending."}`).
- **Semantics**: The client sent a request that cannot be fulfilled given the known, current state of the resource. Retrying the identical request will never succeed.

### Scenario B: Concurrent Double Accept -> HTTP 409 Conflict
- **Context**: Two or more simultaneous requests (e.g. from two doctors or a double-clicking client) attempt to accept/respond to the **same pending consultation at the exact same instant**.
- **Root Cause**: Both requests read `status: "pending"` at `__v: 0`. Both execute concurrently.
- **Handling**: MongoDB executes an atomic conditional update:
  ```javascript
  const updated = await Consultation.findOneAndUpdate(
    { _id: consultationId, status: "pending", __v: expectedVersion },
    { $set: { status: newStatus, ...reviewData }, $inc: { __v: 1 } },
    { new: true }
  );
  ```
- **Result**: Exactly one request wins the database write lock, transitions the state, and increments `__v` to 1. The losing request's conditional filter fails to match because `__v` is no longer `expectedVersion`.
- **HTTP Code**: **409 Conflict** (`{"error": "CONCURRENT_MODIFICATION", "message": "The consultation was modified concurrently by another session. Please refresh and review latest state."}`).
- **Semantics**: RFC 9110 specifies HTTP 409 Conflict for requests that cannot be completed due to a conflict with the current state of the target resource caused by concurrency control (Optimistic Concurrency Control / OCC collision).

---

## 2. Test Assertion Diffs & Verifications

### 2.1 `Backend/tests/decisionB.test.js`
- **Assertion Added**: Red-flag cases cannot be accepted by any role; response status must strictly equal 409 Conflict / 403 Forbidden:
  ```javascript
  expect(res.status).toBe(409);
  expect(res.body.error).toMatch(/RED_FLAG_OVERRIDE_DISALLOWED/i);
  ```
- **Assertion Added**: Overrides on `needs_escalation` require a valid reason and a clinically justifiable note >= 10 non-whitespace characters:
  ```javascript
  expect(res.status).toBe(400);
  expect(res.body.error).toMatch(/clinical rationale.*10 characters/i);
  ```
- **Assertion Added**: OCC race conditions under 50 concurrent threads yield exactly 1 winner (HTTP 200) and 49 conflicts (HTTP 409):
  ```javascript
  const winners = responses.filter(r => r.status === 200);
  const conflicts = responses.filter(r => r.status === 409);
  expect(winners.length).toBe(1);
  expect(conflicts.length).toBe(49);
  ```

### 2.2 `Backend/tests/authMatrix.test.js`
- **Assertion Added**: Dynamically traverses the Express 5 routing tree and asserts that every single registered route is covered by the canonical role authorization matrix:
  ```javascript
  const unmappedRoutes = registeredRoutes.filter(r => !isCovered(r));
  expect(unmappedRoutes).toHaveLength(0);
  ```
- **Assertion Added**: Explicit role validation ensuring doctors cannot access worker-specific routes, workers cannot access doctor-specific routes, and unauthenticated requests are rejected with 401:
  ```javascript
  expect(doctorOnWorkerRoute.status).toBe(403);
  expect(workerOnDoctorRoute.status).toBe(403);
  expect(unauthRequest.status).toBe(401);
  ```

### 2.3 `Backend/tests/security.test.js`
- **Assertion Added**: Strict HTTP security headers enforced by Helmet:
  ```javascript
  expect(res.headers["x-content-type-options"]).toBe("nosniff");
  expect(res.headers["x-frame-options"]).toBe("DENY");
  expect(res.headers["strict-transport-security"]).toContain("max-age=31536000");
  ```
- **Assertion Added**: Rate-limiting returns 429 Too Many Requests when request limits are exceeded:
  ```javascript
  expect(res.status).toBe(429);
  expect(res.headers["retry-after"]).toBeDefined();
  ```

### 2.4 `Backend/tests/upload_adapter.test.js`
- **Assertion Added**: Magic-byte verification rejects spoofed file extensions (e.g., `.png` containing executable payload):
  ```javascript
  expect(res.status).toBe(400);
  expect(res.body.error).toMatch(/INVALID_FILE_MAGIC_BYTES/i);
  ```
- **Assertion Added**: Path traversal sanitization in file uploads:
  ```javascript
  expect(safeFilename).not.toContain("..");
  expect(safeFilename).not.toContain("/");
  ```

### 2.5 `scripts/test_p4_playwright_suite.mjs`
- **E2E Browser Scenarios**: 10 comprehensive headless Chromium scenarios interacting with https://localhost:
  1. Worker Triage End-to-End Diagnostic Pipeline (P0 Malaria verification).
  2. Patient Record Creation & Phone Blind-Indexing.
  3. Doctor Review, Clinical Summary & Prescription Generation.
  4. Red-Flag Emergency Override Blocking (Hard Block 409).
  5. Admin Audit Log & Export Safety (CSV Formula-Injection Escaping).
  6. Idempotency Key De-duplication (1 Job Created for duplicate submissions).
  7. High-Concurrency OCC Race Condition (1 Winner, 49 Conflicts).
  8. DPDP Act (2023) Consent Withdrawal & Deletion Safeguard.
  9. ML Outage Error State (503 Fail-Closed Alert Panel).
  10. Role-Based Navigation & Gateway Isolation.

