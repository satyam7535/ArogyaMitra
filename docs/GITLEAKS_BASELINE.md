# ArogyaMitra — Gitleaks Baseline & Secret Scanning Justification

**Policy**: Strict zero-secret policy across production codebase and VCS history.  
**Scanner**: `gitleaks detect --source . -v --redact --gitleaks-ignore-path .gitleaksignore`  
**Current Status**: 0 leaks detected across all 36 commits in VCS history when evaluated against this baseline.

---

## Baseline Exceptions & Forensic Justifications

Every entry in `.gitleaksignore` has been manually inspected and justified below:

| Fingerprint | Category | Commit | File & Line | Detailed Justification |
|---|---|---|---|---|
| `2f287435...` | Test Fixture | `2f28743` | `Backend/tests/raceOcc.test.js:59` | **Synthetic Idempotency Key**: Used as a static mock string (`"unique-idempotency-key-test-12345"`) to assert that Express in-memory OCC queue rejects duplicate jobs. Contains no real secret material. |
| `fa042257...` | Historical Placeholder | `fa04225` | `Backend/src/config/serverConfig.js:56` | **Remediated Fallback Key**: Contained a placeholder hex string (`0123456789abcdef...`) used as a fallback if `ENCRYPTION_KEY` was unset. **Remediated in commit `201dc9c`**: removed completely and replaced with fail-closed Zod schema validation requiring a real 64-char hex key from environment variables. |
| `201dc9c4...` | Test Fixture | `201dc9c` | `Backend/tests/security.test.js:1615` | **Schema Validation Test**: Test assertion verifying that `serverConfig.envSchema` validates 64-character hex strings correctly. Replaced with dynamic `.padEnd(64, "0")` in subsequent commits. |
| `201dc9c4...` | Test Fixture | `201dc9c` | `Backend/tests/setup.js:8` | **Ephemeral Test Key**: Fallback key used strictly by Vitest when executing in-memory unit tests in isolated test runners. Never loaded in production container. |
| `0ddca8db...` | Raw Evidence | `0ddca8d` | `docs/evidence/p3_idempotency_http.txt:23` | **Synthetic Test UUID**: Raw console stdout from running `scripts/test_p3_idempotency_http.py` in Docker. The script generated `idem-key-{uuid.uuid4()}` which matched the Gitleaks generic API key regex. Redacted in working tree. |

---

## Production Security Verification

1. **Zero Real Credentials**: No real AWS, Cloudinary, Gemini, or JWT secrets exist in VCS history.
2. **Environment Isolation**: `.env` and `*.key` files are strictly excluded via `.gitignore`.
3. **Fail-Closed Runtime**: All services fail immediately upon startup if `JWT_SECRET`, `INTERNAL_SERVICE_SECRET`, or `ENCRYPTION_KEY` are missing or default values.
