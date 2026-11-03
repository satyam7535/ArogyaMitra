import express from "express";
import {
  submitConsultation,
  getMyConsultations,
  getConsultation,
  acceptAI,
  escalate,
  getPendingForDoctor,
  getAllForDoctor,
  respondWithSecondOpinion,
  getNotifications,
  triggerAnalysis,
  triggerAnalysisAsync,
  checkAnalysisJobStatus,
  getJobQueueDiagnostics,
  storeMlAnalysisResult,
  storeLlmAnalysisResult,
  storeFinalVerdictResult,
  storeAnalysisReportResult,
  getAdminConsultations,
  getConsultationAnalytics,
  runDirectTriage,
} from "../controller/consultation.controller.js";
import verifyToken from "../middlewares/auth.middleware.js";
import { validate } from "../middlewares/validate.middleware.js";
import {
  idParamSchema,
  jobIdParamSchema,
  submitConsultationSchema,
  acceptConsultationSchema,
  escalateConsultationSchema,
  respondConsultationSchema,
  analyzeConsultationSchema,
  triageConsultationSchema,
} from "../validators/schemas.js";
import upload from "../utils/upload.js";
import ROLES from "../config/roles.js";

const consultationRouter = express.Router();

// Worker routes
// multipart/form-data: fields: patientId, symptoms, notes | files: attachments[], aiReport
consultationRouter.post(
  "/",
  verifyToken([ROLES.WORKER]),
  upload.fields([
    { name: "attachments", maxCount: 5 },
    { name: "aiReport", maxCount: 1 },
  ]),
  validate(submitConsultationSchema),
  submitConsultation
);


// Interactive Worker Triage Route (Synchronous prediction before DB record creation)
consultationRouter.post(
  "/triage",
  verifyToken([ROLES.WORKER]),
  validate(triageConsultationSchema),
  runDirectTriage
);

consultationRouter.get("/my", verifyToken([ROLES.WORKER]), getMyConsultations);
consultationRouter.patch(
  "/:id/accept",
  verifyToken([ROLES.WORKER]),
  validate(idParamSchema, "params"),
  validate(acceptConsultationSchema),
  acceptAI
);
consultationRouter.patch(
  "/:id/escalate",
  verifyToken([ROLES.WORKER]),
  validate(idParamSchema, "params"),
  validate(escalateConsultationSchema),
  escalate
);

// Admin routes
consultationRouter.get("/admin/analytics", verifyToken([ROLES.ADMIN]), getConsultationAnalytics);
consultationRouter.get("/admin/all", verifyToken([ROLES.ADMIN]), getAdminConsultations);

// Doctor routes
consultationRouter.get("/doctor/all", verifyToken([ROLES.DOCTOR]), getAllForDoctor);
consultationRouter.get("/pending", verifyToken([ROLES.DOCTOR]), getPendingForDoctor);
consultationRouter.patch(
  "/:id/respond",
  verifyToken([ROLES.DOCTOR]),
  validate(idParamSchema, "params"),
  validate(respondConsultationSchema),
  respondWithSecondOpinion
);

// Notifications for worker / doctor / admin
consultationRouter.get("/notifications", verifyToken([ROLES.WORKER, ROLES.DOCTOR, ROLES.ADMIN]), getNotifications);

// Shared (worker or doctor can view)
consultationRouter.get("/:id", verifyToken([ROLES.WORKER, ROLES.DOCTOR]), validate(idParamSchema, "params"), getConsultation);

// Server-Side Orchestrated AI Analysis (ML -> LLM -> PDF)
consultationRouter.post(
  "/:id/analyze",
  verifyToken([ROLES.WORKER, ROLES.DOCTOR]),
  validate(idParamSchema, "params"),
  validate(analyzeConsultationSchema),
  triggerAnalysis
);
consultationRouter.post(
  "/:id/analyze/async",
  verifyToken([ROLES.WORKER, ROLES.DOCTOR]),
  validate(idParamSchema, "params"),
  validate(analyzeConsultationSchema),
  triggerAnalysisAsync
);
consultationRouter.get(
  "/:id/analyze/status/:jobId",
  verifyToken([ROLES.WORKER, ROLES.DOCTOR]),
  validate(jobIdParamSchema, "params"),
  checkAnalysisJobStatus
);
consultationRouter.get("/queue/metrics", verifyToken([ROLES.ADMIN, ROLES.DOCTOR]), getJobQueueDiagnostics);

// Direct client analysis mutation routes (Blocked with 403)
consultationRouter.post("/:id/analysis/ml", verifyToken([ROLES.WORKER]), validate(idParamSchema, "params"), storeMlAnalysisResult);
consultationRouter.post("/:id/analysis/llm", verifyToken([ROLES.WORKER]), validate(idParamSchema, "params"), storeLlmAnalysisResult);
consultationRouter.post("/:id/analysis/verdict", verifyToken([ROLES.WORKER]), validate(idParamSchema, "params"), storeFinalVerdictResult);
consultationRouter.post("/:id/analysis/report", verifyToken([ROLES.WORKER]), validate(idParamSchema, "params"), storeAnalysisReportResult);

export default consultationRouter;
