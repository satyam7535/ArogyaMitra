# ArogyaMitra — Gitleaks Baseline & Secret Scanning Justification

**Policy**: Strict zero-secret policy across production codebase and VCS history.  
**Scanner**: `d:\tools\gitleaks.exe detect --source . -v --redact --gitleaks-ignore-path .gitleaksignore`  
**Current Status**: 0 leaks detected across all 37 commits in VCS history when evaluated against `.gitleaksignore`.

---

## 1. Raw Gitleaks Output for the 5 Baseline Findings

When evaluated without `.gitleaksignore`, `gitleaks detect -v --redact` identifies exactly 5 historical findings across 37 commits:

```text
Finding:     ... POST requests with Idempotency-Key: REDACTED
Secret:      REDACTED
RuleID:      generic-api-key
Entropy:     3.933209
File:        docs/evidence/p3_idempotency_http.txt
Line:        23
Commit:      0ddca8db370c2343460bb68a6c6807321966fe36
Fingerprint: 0ddca8db370c2343460bb68a6c6807321966fe36:docs/evidence/p3_idempotency_http.txt:generic-api-key:23

Finding:     ...env.ENCRYPTION_KEY) process.env.ENCRYPTION_KEY = "REDACTED"
Secret:      REDACTED
RuleID:      generic-api-key
Entropy:     4.000000
File:        Backend/tests/setup.js
Line:        8
Commit:      201dc9c442b4b9332c925f0409ccd66e3b661be7
Fingerprint: 201dc9c442b4b9332c925f0409ccd66e3b661be7:Backend/tests/setup.js:generic-api-key:8

Finding:     ENCRYPTION_KEY: "REDACTED"
Secret:      REDACTED
RuleID:      generic-api-key
Entropy:     4.000000
File:        Backend/tests/security.test.js
Line:        1615
Commit:      201dc9c442b4b9332c925f0409ccd66e3b661be7
Fingerprint: 201dc9c442b4b9332c925f0409ccd66e3b661be7:Backend/tests/security.test.js:generic-api-key:1615

Finding:     const idempotencyKey = "REDACTED"
Secret:      REDACTED
RuleID:      generic-api-key
Entropy:     4.063651
File:        Backend/tests/raceOcc.test.js
Line:        59
Commit:      2f28743514cbaf36b828b9c0d9b556106ef020de
Fingerprint: 2f28743514cbaf36b828b9c0d9b556106ef020de:Backend/tests/raceOcc.test.js:generic-api-key:59

Finding:     ENCRYPTION_KEY: "REDACTED"
Secret:      REDACTED
RuleID:      generic-api-key
Entropy:     4.000000
File:        Backend/src/config/serverConfig.js
Line:        56
Commit:      fa04225773c30a4258acba01b5f615e54c7cac2e
Fingerprint: fa04225773c30a4258acba01b5f615e54c7cac2e:Backend/src/config/serverConfig.js:generic-api-key:56
```

---

## 2. Forensic Descriptions & Justifications

| # | Fingerprint | Commit | File & Line | Detailed Forensic Justification |
|---|---|---|---|---|
| **1** | `0ddca8db...` | `0ddca8d` | `docs/evidence/p3_idempotency_http.txt:23` | **Synthetic Test UUID**: Console stdout captured from executing `scripts/test_p3_idempotency_http.py` in Docker. The script printed `idem-key-{uuid4()}` which triggered Gitleaks generic-api-key rule. Redacted in working tree. |
| **2** | `201dc9c4...` | `201dc9c` | `Backend/tests/setup.js:8` | **Isolated Test Key Fixture**: Fallback encryption key provided to Vitest in-memory test runner so unit tests execute in isolated worker environments without requiring a local `.env`. Never loaded in Docker production containers. |
| **3** | `201dc9c4...` | `201dc9c` | `Backend/tests/security.test.js:1615` | **Schema Validation Test**: Assertion testing `serverConfig.envSchema` validation against 64-character hex strings. Dynamic `.padEnd(64, "0")` replaces static fixtures in subsequent tests. |
| **4** | `2f287435...` | `2f28743` | `Backend/tests/raceOcc.test.js:59` | **Synthetic OCC Test Key**: A static test string (`"unique-idempotency-key-test-12345"`) used in unit tests verifying that Express OCC job queue prevents double-processing. |
| **5** | `fa042257...` | `fa04225` | `Backend/src/config/serverConfig.js:56` | **Historical Default Fallback**: A placeholder string (`0123456789abcdef...`) used as a fallback if `ENCRYPTION_KEY` was unset. **Remediated in commit `201dc9c`**: removed completely and replaced by fail-closed Zod schema validation requiring a real 64-char hex key from environment variables. |

---

## 3. Clarification on Legacy Filenames (`dataEncryption.js` & `cryptoUtils.js`)

- **Correction**: Earlier documentation erroneously referenced `dataEncryption.js` and `cryptoUtils.js` in relation to the Gitleaks baseline.
- **Fact**: Neither `dataEncryption.js` nor `cryptoUtils.js` exist in the repository or git commit history, and neither file was ever flagged by Gitleaks or included in `.gitleaksignore`.
- The active cryptographic implementation is strictly [`Backend/src/utils/crypto.js`](file:///d:/Document/Projects/Internship/Arogyamitra/Backend/src/utils/crypto.js).
- All fallback strings (`default_hmac_secret_for_blind_index`) have been removed from `Backend/src/utils/crypto.js`.
- Missing `ENCRYPTION_KEY` under `NODE_ENV=production` causes immediate process termination with code 1 (`Backend/tests/encryption_key_exit.test.js`).
