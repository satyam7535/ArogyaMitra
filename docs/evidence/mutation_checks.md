# ArogyaMitra — Mutation Checks Log

This log records intentional code mutations performed to verify that security, authorization, and cryptographic integrity tests can actually fail (Rule 3).

---

## 1. Stage 0: Forgot Password Reset Token Leak Prevention
- **Target File**: `Backend/src/service/worker.service.js`
- **Associated Test**: `Backend/tests/security.test.js` (`should never leak resetToken in forgot-password response`)
- **Baseline Behavior**: `handleForgotPassword` returns `{ message: "..." }` and does NOT return `resetToken` in HTTP response body.
- **Mutation Applied**:
  ```diff
  - return { message: "If that email exists, password reset instructions have been sent." };
  + return { message: "If that email exists, password reset instructions have been sent.", resetToken };
  ```
- **Observed Test Failure**:
  ```
  FAIL tests/security.test.js > Phase 2 — Security & Cryptographic Integrity > 8. HTTP Level Security & Disabled Public Endpoints > should never leak resetToken in forgot-password response
  AssertionError: expected 'c7288c07a9663cf1df526e7e460c415893522…' to be undefined
  - Expected: undefined
  + Received: "c7288c07a9663cf1df526e7e460c415893522ed10b8ea667ee569f98051e3889"
  ```
- **Restoration**: Code restored to return clean message without `resetToken`. Test re-ran and passed (20/20 passed).

---

## 2. Stage 0: ML Microservice Internal Token Enforcement
- **Target File**: `ML_Model/app.py`
- **Associated Test**: `ML_Model/tests/test_phase0.py` (`test_unauthenticated_predict_rejected`)
- **Baseline Behavior**: `verify_internal_service_token` rejects requests without valid `X-Internal-Service-Token` with HTTP 401/403.
- **Mutation Applied**:
  ```diff
  def verify_internal_service_token(...):
  +   return {"service": "mutated-bypassed"}
      if not REQUIRE_INTERNAL_AUTH:
  ```
- **Observed Test Failure**:
  ```
  FAILED ML_Model/tests/test_phase0.py::test_unauthenticated_predict_rejected - AssertionError: assert 200 == 401
  + where 200 = <Response [200 OK]>.status_code
  ```
- **Restoration**: Code restored to remove bypassed return. Test re-ran and passed (7/7 passed).

---

## 3. Stage 0: PDF Report TreeSHAP Label Verification
- **Target File**: `graph/utils/pdf_generator.py`
- **Associated Test**: `graph/tests/test_phase3.py` (`test_pdf_generator_labels_use_treeshap`)
- **Baseline Behavior**: `TRANSLATIONS[lang]["ai_explanation"]` contains `"AI Explanation (TreeSHAP)"` across en, hi, mr and does not contain `"LIME"`.
- **Mutation Applied**:
  ```diff
  - "ai_explanation": "AI Explanation (TreeSHAP)",
  + "ai_explanation": "AI Explanation (LIME)",
  ```
- **Observed Test Failure**:
  ```
  FAILED graph/tests/test_phase3.py::test_pdf_generator_labels_use_treeshap
  AssertionError: assert 'TreeSHAP' in 'AI Explanation (LIME)'
  ```
- **Restoration**: Code restored to `"AI Explanation (TreeSHAP)"`. Test re-ran and passed (13/13 passed).

---

## 4. Stage 0: Role Casing and Unauthorized Role Access Rejection
- **Target File**: `Backend/src/middlewares/auth.middleware.js`
- **Associated Test**: `Backend/tests/security.test.js` (`should reject wrongly-cased unauthorized roles and role spoofing attempts (403)`)
- **Baseline Behavior**: `auth.middleware.js` normalizes roles via case-insensitive whitelist matching (`allowedRolesLower.includes(userRoleLower)`), rejecting any role outside the whitelist with HTTP 403.
- **Mutation Applied**:
  ```diff
  - if (roles.length > 0) {
  + if (false) {
      const userRoleLower = (decoded.role || "").toLowerCase();
      const allowedRolesLower = roles.map((r) => r.toLowerCase());
      if (!allowedRolesLower.includes(userRoleLower)) {
        return res.status(403).json({ message: "Forbidden: Insufficient role permissions" });
      }
    }
  ```
- **Observed Test Failure**:
  ```
  FAIL tests/security.test.js > Phase 2 — Security & Cryptographic Integrity > 5. Role & Organization Authorization Middleware > should reject wrongly-cased unauthorized roles and role spoofing attempts (403)
  AssertionError: expected "vi.fn()" to be called with arguments: [ 403 ]
  Number of calls: 0
  ```
- **Restoration**: Code restored to active case-insensitive whitelist comparison. Test re-ran and passed (21/21 passed).

