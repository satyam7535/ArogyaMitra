# ArogyaMitra — Express Routes Inventory Map (`docs/inventory/routes.md`)

This machine-readable map documents every Express endpoint defined across `Backend/src/routes/*.js`, its middleware chain, controller handler, and test coverage.

---

## Route Catalog

| # | Method | Path | Middleware Chain (Auth, Role, Scoping, Validation, Rate Limit) | Controller Handler | Test Coverage | Notes |
| :-: | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | `GET` | `/` | None (Public) | Inline (`src/index.js:49`) | None | Service heartbeat |
| **2** | `GET` | `/health` | None (Public) | Inline (`src/index.js:53`) | None | Healthcheck |
| **3** | `POST` | `/api/v1/admin/register` | None (Public) | `admin.controller.js:register` | `security.test.js` | Handled: returns `403 REGISTRATION_DISABLED` |
| **4** | `POST` | `/api/v1/admin/login` | `authRateLimiter` (15 req / 15m) | `admin.controller.js:login` | `security.test.js` | Argon2id auth, lockout check, sets cookies |
| **5** | `POST` | `/api/v1/admin/refresh-token` | None (Public) | `admin.controller.js:refreshSession` | `security.test.js` | Rotating refresh token family |
| **6** | `POST` | `/api/v1/admin/forgot-password` | `authRateLimiter` (15 req / 15m) | `admin.controller.js:forgotPassword` | None | Returns token directly in JSON (stub) |
| **7** | `POST` | `/api/v1/admin/reset-password` | `authRateLimiter` (15 req / 15m) | `admin.controller.js:resetPassword` | `security.test.js` | SHA-256 hashed token validation |
| **8** | `POST` | `/api/v1/admin/logout` | `verifyToken(["Admin", "admin"])` | `admin.controller.js:logout` | None | Revokes refresh token, clears cookie |
| **9** | `GET` | `/api/v1/admin/profile` | `verifyToken(["Admin", "admin"])` | `admin.controller.js:getProfile` | None | Returns admin profile |
| **10** | `POST` | `/api/v1/worker/login` | `authRateLimiter` (15 req / 15m) | `worker.controller.js:login` | None | Worker login |
| **11** | `POST` | `/api/v1/worker/refresh-token` | None (Public) | `worker.controller.js:refreshSession` | None | Token rotation |
| **12** | `POST` | `/api/v1/worker/forgot-password` | `authRateLimiter` (15 req / 15m) | `worker.controller.js:forgotPassword` | None | Returns token directly in JSON (stub) |
| **13** | `POST` | `/api/v1/worker/reset-password` | `authRateLimiter` (15 req / 15m) | `worker.controller.js:resetPassword` | None | Token reset |
| **14** | `POST` | `/api/v1/worker/logout` | `verifyToken(["Worker", "worker"])` | `worker.controller.js:logout` | None | Worker logout |
| **15** | `POST` | `/api/v1/worker/` | `verifyToken(["Admin", "admin"])` | `worker.controller.js:createWorker` | None | Admin provisions worker in their org |
| **16** | `GET` | `/api/v1/worker/` | `verifyToken(["Admin", "admin"])` | `worker.controller.js:getWorkers` | None | Lists workers in admin's org |
| **17** | `DELETE` | `/api/v1/worker/:id` | `verifyToken(["Admin", "admin"])` | `worker.controller.js:deleteWorker` | None | Hard deletes worker document |
| **18** | `POST` | `/api/v1/doctor/login` | `authRateLimiter` (15 req / 15m) | `doctor.controller.js:login` | None | Doctor login |
| **19** | `POST` | `/api/v1/doctor/refresh-token` | None (Public) | `doctor.controller.js:refreshSession` | None | Token rotation |
| **20** | `POST` | `/api/v1/doctor/forgot-password` | `authRateLimiter` (15 req / 15m) | `doctor.controller.js:forgotPassword` | None | Returns token directly in JSON (stub) |
| **21** | `POST` | `/api/v1/doctor/reset-password` | `authRateLimiter` (15 req / 15m) | `doctor.controller.js:resetPassword` | None | Token reset |
| **22** | `POST` | `/api/v1/doctor/logout` | `verifyToken(["Doctor", "doctor"])` | `doctor.controller.js:logout` | None | Doctor logout |
| **23** | `POST` | `/api/v1/doctor/` | `verifyToken(["Admin", "admin"])` | `doctor.controller.js:createDoctor` | None | Admin provisions doctor in their org |
| **24** | `GET` | `/api/v1/doctor/` | `verifyToken(["Admin", "admin"])` | `doctor.controller.js:getDoctors` | None | Lists doctors in admin's org |
| **25** | `DELETE` | `/api/v1/doctor/:id` | `verifyToken(["Admin", "admin"])` | `doctor.controller.js:deleteDoctor` | None | Hard deletes doctor document |
| **26** | `GET` | `/api/v1/doctor/list` | `verifyToken(["Worker", "worker", "Admin", "admin"])` | `doctor.controller.js:getAllDoctors` | None | Worker lists doctors for referral |
| **27** | `POST` | `/api/v1/patient/` | `verifyToken(["worker"])` | `patient.controller.js:registerPatient` | None | Worker registers patient in org |
| **28** | `GET` | `/api/v1/patient/` | `verifyToken(["worker"])` | `patient.controller.js:getPatients` | None | Lists patients in worker's org |
| **29** | `GET` | `/api/v1/patient/:id` | `verifyToken(["worker"])` | `patient.controller.js:getPatient` | None | Single patient scoped to org (404 rule) |
| **30** | `POST` | `/api/v1/consultation/` | `verifyToken(["worker"])`, `upload.fields(...)` | `consultation.controller.js:submitConsultation` | None | Submits consultation (Cloudinary stream) |
| **31** | `GET` | `/api/v1/consultation/my` | `verifyToken(["worker"])` | `consultation.controller.js:getMyConsultations` | None | Lists consultations by worker |
| **32** | `PATCH` | `/api/v1/consultation/:id/accept` | `verifyToken(["worker"])` | `consultation.controller.js:acceptAI` | None | Closes consultation with AI acceptance |
| **33** | `PATCH` | `/api/v1/consultation/:id/escalate` | `verifyToken(["worker"])` | `consultation.controller.js:escalate` | None | Assigns doctor, sets status pending |
| **34** | `GET` | `/api/v1/consultation/admin/all` | `verifyToken(["admin"])` | `consultation.controller.js:getAdminConsultations` | None | Admin lists all consultations in org |
| **35** | `GET` | `/api/v1/consultation/doctor/all` | `verifyToken(["doctor"])` | `consultation.controller.js:getAllForDoctor` | None | Doctor lists assigned consultations |
| **36** | `GET` | `/api/v1/consultation/pending` | `verifyToken(["doctor"])` | `consultation.controller.js:getPendingForDoctor` | None | Doctor reviews pending escalated cases |
| **37** | `PATCH` | `/api/v1/consultation/:id/respond` | `verifyToken(["doctor"])` | `consultation.controller.js:respondWithSecondOpinion` | None | Doctor submits second opinion diagnosis |
| **38** | `GET` | `/api/v1/consultation/:id` | `verifyToken(["worker", "doctor"])` | `consultation.controller.js:getConsultation` | None | Consultation detail scoped to org |
| **39** | `POST` | `/api/v1/consultation/:id/analyze` | `verifyToken(["worker", "doctor"])` | `consultation.controller.js:triggerAnalysis` | None | Synchronous server-side AI pipeline |
| **40** | `POST` | `/api/v1/consultation/:id/analyze/async` | `verifyToken(["worker", "doctor"])` | `consultation.controller.js:triggerAnalysisAsync` | `concurrency.test.js` | Enqueues job in memory, returns HTTP 202 |
| **41** | `GET` | `/api/v1/consultation/:id/analyze/status/:jobId` | `verifyToken(["worker", "doctor"])` | `consultation.controller.js:checkAnalysisJobStatus` | `concurrency.test.js` | Polls async job status |
| **42** | `GET` | `/api/v1/consultation/queue/metrics` | `verifyToken(["admin", "doctor"])` | `consultation.controller.js:getJobQueueDiagnostics` | `concurrency.test.js` | Returns in-memory queue metrics |
| **43** | `POST` | `/api/v1/consultation/:id/analysis/ml` | `verifyToken(["worker"])` | `consultation.controller.js:storeMlAnalysisResult` | `security.test.js` | Disabled: returns 403 Forbidden |
| **44** | `POST` | `/api/v1/consultation/:id/analysis/llm` | `verifyToken(["worker"])` | `consultation.controller.js:storeLlmAnalysisResult` | `security.test.js` | Disabled: returns 403 Forbidden |
| **45** | `POST` | `/api/v1/consultation/:id/analysis/verdict` | `verifyToken(["worker"])` | `consultation.controller.js:storeFinalVerdictResult` | `security.test.js` | Disabled: returns 403 Forbidden |
| **46** | `POST` | `/api/v1/consultation/:id/analysis/report` | `verifyToken(["worker"])` | `consultation.controller.js:storeAnalysisReportResult` | `security.test.js` | Disabled: returns 403 Forbidden |

---

## Architectural Findings on Route Layer

1. **Zod Validation Missing on Routes**: Although `zod` is installed and used in `serverConfig.js`, **zero** Express routes have Zod request body/query validation middleware.
2. **Missing `enforceOrgScope` Middleware**: The middleware exists in `orgScope.middleware.js` and was unit-tested with mock objects in `security.test.js`, but it is **not imported or mounted on any route** in `routes/*.js`. Scoping is done manually in `service/*.js`.
3. **No CSRF Protection**: No CSRF middleware exists for cookie-authenticated sessions.
4. **No Admin Audit Log Route**: No route exists to query `AuditLog` records (`GET /api/v1/admin/audit` is missing).
5. **Direct Reset Token Exposure**: Password reset routes return raw tokens in HTTP response JSON rather than dispatching via email or console-logging only in dev.
