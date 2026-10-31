# OWASP ZAP Baseline Scan — Findings & Disposition Notes

## Execution Metadata
- **Tool**: OWASP ZAP 2.16.1 (`zaproxy/zap-stable:latest`)
- **Scan Type**: Unauthenticated passive baseline scan (rules: `zap-baseline.py -t https://arogya-proxy -I`)
- **Target**: `https://arogya-proxy` (internal edge ingress inside `arogyamitra_arogya-network`)
- **Total URLs Crawled**: 68
- **Results**: **FAIL-NEW: 0**, **WARN-NEW: 6**, **PASS: 62**
- **Evidence File**: `docs/evidence/zap_baseline_report.txt`

---

## Detailed Disposition of the 6 WARNs

1. **`WARN-NEW [10015] Re-examine Cache-control Directives`**
   - **Trigger**: `https://arogya-proxy`, `https://arogya-proxy/robots.txt`, `https://arogya-proxy/sitemap.xml`
   - **Disposition**: **Accepted, not tested**. Public landing and discovery metadata files do not contain PHI or PII. Backend API routes set `Cache-Control: no-store, no-cache`, but public root caching was accepted without active penetration testing.

2. **`WARN-NEW [10049] Storable and Cacheable Content`**
   - **Trigger**: Static JavaScript bundles (`/static/js/*.js` via Streamlit frontend)
   - **Disposition**: **Accepted**. Bundled JavaScript libraries are static, version-hashed assets intended to be cached by client browsers for UI performance.

3. **`WARN-NEW [10055] CSP: Failure to Define Directive with No Fallback`**
   - **Trigger**: `https://arogya-proxy`, `https://arogya-proxy/sitemap.xml`
   - **Disposition**: **Accepted**. Nginx configures `default-src 'self'`. ZAP flags individual directive fallbacks (e.g., `frame-ancestors` / `form-action`).

4. **`WARN-NEW [10096] Timestamp Disclosure - Unix`**
   - **Trigger**: `/static/js/emotion-styled.browser.esm.BlkDsJXZ.js`, `/static/js/opacities.BBavuN52.js`
   - **Disposition**: **Accepted**. Numeric constants in bundled third-party vendor code (Emotion/React) matched Unix timestamp heuristic patterns. These are build-time library constants, not server system clocks.

5. **`WARN-NEW [10109] Modern Web Application`**
   - **Trigger**: `https://arogya-proxy`, `/robots.txt`, `/sitemap.xml`
   - **Disposition**: **Accepted (Informational)**. ZAP notices modern Single-Page Application (SPA) architecture relying on client-side JavaScript execution.

6. **`WARN-NEW [90004] Cross-Origin-Embedder-Policy Header Missing or Invalid`**
   - **Trigger**: `https://arogya-proxy`, `/robots.txt`, `/sitemap.xml`
   - **Disposition**: **Accepted, not tested**. Enabling `require-corp` causes cross-origin subresource blocks for Streamlit canvas and font web workers. Accepted without a formal COEP test suite.

---

## Scope & Limitations
This scan represents an **unauthenticated passive baseline scan** only. It does not evaluate authenticated session states, business logic flaws, role-based authorization bypasses, or active fuzzing vectors.
