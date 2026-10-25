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
    storeMlAnalysisResult,
    storeLlmAnalysisResult,
    storeFinalVerdictResult,
    storeAnalysisReportResult,
    getAdminConsultations,
} from "../controller/consultation.controller.js";
import verifyToken from "../middlewares/auth.middleware.js";
import upload from "../utils/upload.js";

const consultationRouter = express.Router();

// Worker routes
// multipart/form-data: fields: patientId, symptoms, notes | files: attachments[], aiReport
consultationRouter.post(
    "/",
    verifyToken(["worker"]),
    upload.fields([
        { name: "attachments", maxCount: 5 },
        { name: "aiReport", maxCount: 1 },
    ]),
    submitConsultation
); // POST /api/v1/consultation

consultationRouter.get("/my", verifyToken(["worker"]), getMyConsultations);                    // GET  /api/v1/consultation/my
consultationRouter.patch("/:id/accept", verifyToken(["worker"]), acceptAI);                    // PATCH /api/v1/consultation/:id/accept
consultationRouter.patch("/:id/escalate", verifyToken(["worker"]), escalate);                  // PATCH /api/v1/consultation/:id/escalate

// Admin routes
consultationRouter.get("/admin/all", verifyToken(["admin"]), getAdminConsultations);          // GET  /api/v1/consultation/admin/all

// Doctor routes
consultationRouter.get("/doctor/all", verifyToken(["doctor"]), getAllForDoctor);                // GET  /api/v1/consultation/doctor/all
consultationRouter.get("/pending", verifyToken(["doctor"]), getPendingForDoctor);              // GET  /api/v1/consultation/pending
consultationRouter.patch("/:id/respond", verifyToken(["doctor"]), respondWithSecondOpinion);   // PATCH /api/v1/consultation/:id/respond

// Shared (worker or doctor can view)
consultationRouter.get("/:id", verifyToken(["worker", "doctor"]), getConsultation);            // GET  /api/v1/consultation/:id

// Analysis storage routes (worker)
consultationRouter.post("/:id/analysis/ml", verifyToken(["worker"]), storeMlAnalysisResult);   // POST /api/v1/consultation/:id/analysis/ml
consultationRouter.post("/:id/analysis/llm", verifyToken(["worker"]), storeLlmAnalysisResult); // POST /api/v1/consultation/:id/analysis/llm
consultationRouter.post("/:id/analysis/verdict", verifyToken(["worker"]), storeFinalVerdictResult); // POST /api/v1/consultation/:id/analysis/verdict
consultationRouter.post("/:id/analysis/report", verifyToken(["worker"]), storeAnalysisReportResult); // POST /api/v1/consultation/:id/analysis/report

export default consultationRouter;
