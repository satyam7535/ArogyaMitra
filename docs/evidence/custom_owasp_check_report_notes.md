# Custom OWASP Top 10 API Security Check — Analysis & Notes

**Script**: `scripts/test_p6_owasp_scanner.py`  
**Raw Command Output**: [`docs/evidence/custom_owasp_check_report.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/custom_owasp_check_report.txt)  
**Target**: `https://localhost` (Edge Nginx reverse proxy + Backend Express + ML + Graph)  

---

## 1. Scope & Disclaimer

This script executes **10 custom basic API checks** implemented in Python using the `requests` library.  
**It is NOT an official OWASP ZAP baseline scan.**  
Official OWASP ZAP evaluation remains marked **`NOT RUN`** due to Docker daemon image pull failure on host storage limits.

---

## 2. Tested Check Categories (OWASP API Top 10 - 2023)

1. **API1:2023 BOLA / IDOR**: Probed foreign consultation ID across isolation boundary -> returned HTTP 404.
2. **API2:2023 Broken Authentication**: Injected forged JWT signature -> rejected with HTTP 401.
3. **API3:2023 Mass Assignment**: Injected unauthorized properties (`redFlag`, `isAdmin`) into consultation creation payload -> rejected with HTTP 400 via Zod `.strict()`.
4. **API4:2023 Resource Consumption**: Rate limiters enforced at Edge Nginx and Express authRateLimiter -> returns HTTP 429 with `Retry-After`.
5. **API5:2023 BFLA**: Health worker token attempting admin route (`GET /api/v1/admin/sessions`) -> rejected with HTTP 403.
6. **API6:2023 Sensitive Business Flows**: Worker attempting to accept a red-flag condition -> rejected with HTTP 409 `RED_FLAG_ACCEPT_BLOCKED`.
7. **API7:2023 SSRF & File Upload Validation**: Executed binary magic-byte inspection on uploads -> non-whitelisted headers rejected with HTTP 400.
8. **API8:2023 Security Misconfiguration**: Edge Nginx headers verified: HSTS, CSP, X-Frame-Options (`DENY`), `x-powered-by` stripped.
9. **API9:2023 Improper Inventory Management**: Direct requests to internal endpoints `/predict` and `/analyze` -> blocked with HTTP 403.
10. **API10:2023 Unsafe Third-Party / Upstream Consumption**: Upstream ML container outage -> Express fails closed with HTTP 503 `MODEL_UNAVAILABLE`.
