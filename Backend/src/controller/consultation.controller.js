import {
  createConsultation,
  getConsultationsByWorker,
  getConsultationById,
  escalateToDoctor,
  acceptAiResult,
  getPendingConsultationsForDoctor,
  getAllConsultationsForDoctor,
  submitSecondOpinion,
  getUserNotifications,
  triggerConsultationAnalysis,
  getAllConsultationsForAdmin,
  getAdminAggregates,
} from "../service/consultation.service.js";
import {
  enqueueAnalysisJob,
  getJobStatus,
  getQueueMetrics,
} from "../service/jobQueue.service.js";
import { logAuditEvent } from "../middlewares/audit.middleware.js";
import Consultation from "../models/consultation/consultationSchema.js";
import AnalysisJob from "../models/job/jobSchema.js";
import { getJobStatusFromDb } from "../service/jobQueue.service.js";
import jwt from "jsonwebtoken";
import serverConfig from "../config/serverConfig.js";
import ROLES from "../config/roles.js";
import { validatePredictionBoundary } from "../validators/diseaseClasses.js";

// Worker submits a new consultation
const submitConsultation = async (req, res) => {
  try {
    const { patientId, symptoms, notes } = req.body;

    if (!patientId || !symptoms) {
      return res.status(400).json({ message: "patientId and symptoms are required" });
    }

    let symptomsArray = symptoms;
    if (typeof symptoms === "string") {
      try {
        symptomsArray = JSON.parse(symptoms);
      } catch {
        symptomsArray = symptoms.split(",").map((s) => s.trim());
      }
    }

    const attachmentFiles = req.files?.attachments || [];
    const aiReportFile = req.files?.aiReport?.[0] || null;

    // Stage 2 D7: Magic-byte inspection for all uploaded files
    const { validateFileMagicBytes } = await import("../utils/upload.js");
    const allFiles = [...attachmentFiles, ...(aiReportFile ? [aiReportFile] : [])];
    for (const f of allFiles) {
      if (!validateFileMagicBytes(f.buffer, f.mimetype)) {
        return res.status(400).json({
          message: `File validation failed for '${f.originalname}': binary magic bytes do not match declared MIME type ${f.mimetype}. Disguised executables and polyglots are rejected.`,
        });
      }
    }

    const consultation = await createConsultation(
      { patientId, symptoms: symptomsArray, notes, attachmentFiles, aiReportFile },
      req.user.id,
      req.user.organization
    );

    await logAuditEvent({
      req,
      action: "CONSULTATION_SUBMITTED",
      resourceType: "Consultation",
      resourceId: consultation._id,
      metadata: { patientId },
    });

    return res.status(201).json({ message: "Consultation submitted successfully", consultation });
  } catch (error) {
    return res.status(500).json({ message: error.message });
  }
};

// Worker views consultations from their organization (paginated & projected)
const getMyConsultations = async (req, res) => {
  try {
    const { page, limit } = req.query || {};
    const result = await getConsultationsByWorker(req.user.id, req.user.organization, { page, limit });
    return res.status(200).json(result);
  } catch (error) {
    return res.status(500).json({ message: error.message });
  }
};

// Admin views all consultations in their organization
const getAdminConsultations = async (req, res) => {
  try {
    const consultations = await getAllConsultationsForAdmin(req.user.id, req.user.organization);
    return res.status(200).json({ consultations });
  } catch (error) {
    return res.status(500).json({ message: error.message });
  }
};

// Get a single consultation (strictly scoped to organization)
const getConsultation = async (req, res) => {
  try {
    const consultation = await getConsultationById(req.params.id, req.user.organization);
    if (!consultation) {
      // 404 Not Found to prevent enumeration across organizations
      return res.status(404).json({ message: "Consultation not found" });
    }

    await logAuditEvent({
      req,
      action: "CONSULTATION_VIEWED",
      resourceType: "Consultation",
      resourceId: req.params.id,
    });

    return res.status(200).json({ consultation });
  } catch (error) {
    return res.status(500).json({ message: error.message });
  }
};

// Worker accepts AI result or refers to hospital — closes consultation
const acceptAI = async (req, res) => {
  try {
    const { notes, decisionOutcome, overrideReason, overrideNote, version } = req.body || {};
    const expectedVersion = version !== undefined ? version : (req.headers["if-match"] ? parseInt(req.headers["if-match"], 10) : undefined);
    const consultation = await acceptAiResult(
      req.params.id,
      req.user.organization,
      req.user.id,
      { notes, decisionOutcome, overrideReason, overrideNote, version: expectedVersion }
    );
    if (!consultation) {
      return res.status(404).json({ message: "Consultation not found" });
    }

    const actionType = consultation.decisionOutcome === "referred_to_hospital"
      ? "CONSULTATION_REFERRED_HOSPITAL"
      : overrideReason
      ? "CONSULTATION_ACCEPTED_WITH_OVERRIDE"
      : "CONSULTATION_ACCEPTED_AI";

    await logAuditEvent({
      req,
      action: actionType,
      resourceType: "Consultation",
      resourceId: req.params.id,
      metadata: {
        outcome: consultation.decisionOutcome,
        overrideReason: consultation.overrideReason || null,
        overrideNote: consultation.overrideDetails?.note || null,
      },
    });

    const msg = consultation.decisionOutcome === "referred_to_hospital"
      ? "Consultation closed with referral to hospital."
      : overrideReason
      ? "AI recommendation overridden by worker. Consultation closed."
      : "AI result accepted. Consultation closed.";

    return res.status(200).json({ message: msg, consultation });
  } catch (error) {
    if (error.code === "RED_FLAG_ACCEPT_BLOCKED") {
      return res.status(409).json({
        message: error.message,
        code: "RED_FLAG_ACCEPT_BLOCKED",
      });
    }
    if (error.name === "VersionError" || error.status === 409) {
      return res.status(409).json({
        message: error.message || "Conflict: consultation was updated concurrently. Please refresh and try again.",
        code: error.code || "CONCURRENCY_CONFLICT",
      });
    }
    const statusCode = error.status || 400;
    return res.status(statusCode).json({
      message: error.message,
      code: error.code || "ACCEPT_ERROR",
    });
  }
};

// Worker escalates to doctor for second opinion
const escalate = async (req, res) => {
  try {
    const doctorId = req.body.doctorId || req.body.targetDoctorId;
    const reason = req.body.reason || "";
    const version = req.body.version !== undefined ? req.body.version : (req.headers["if-match"] ? parseInt(req.headers["if-match"], 10) : undefined);
    if (!doctorId) return res.status(400).json({ message: "doctorId is required" });

    const consultation = await escalateToDoctor(
      req.params.id,
      req.user.organization,
      doctorId,
      reason,
      { version }
    );

    if (!consultation) {
      return res.status(404).json({ message: "Consultation not found" });
    }

    await logAuditEvent({
      req,
      action: "CONSULTATION_ESCALATED",
      resourceType: "Consultation",
      resourceId: req.params.id,
      metadata: { doctorId, reason },
    });

    return res.status(200).json({ message: "Consultation escalated to doctor", consultation });
  } catch (error) {
    if (error.name === "VersionError" || error.status === 409) {
      return res.status(409).json({ message: "Conflict: consultation was updated concurrently. Please refresh and try again." });
    }
    return res.status(400).json({ message: error.message });
  }
};

// Doctor views all pending consultations assigned to them within their organization (with overdue badge)
const getPendingForDoctor = async (req, res) => {
  try {
    const overdueHours = req.query.overdueHours ? parseInt(req.query.overdueHours, 10) : 24;
    const consultations = await getPendingConsultationsForDoctor(req.user.id, req.user.organization, overdueHours);
    return res.status(200).json({ consultations });
  } catch (error) {
    return res.status(500).json({ message: error.message });
  }
};

// In-app notifications for authenticated user
const getNotifications = async (req, res) => {
  try {
    const notifications = await getUserNotifications(req.user.id, req.user.role, req.user.organization);
    return res.status(200).json({ notifications });
  } catch (error) {
    return res.status(500).json({ message: error.message });
  }
};

// Doctor views ALL consultations assigned to them
const getAllForDoctor = async (req, res) => {
  try {
    const consultations = await getAllConsultationsForDoctor(req.user.id, req.user.organization);
    return res.status(200).json({ consultations });
  } catch (error) {
    return res.status(500).json({ message: error.message });
  }
};

// Doctor submits second opinion
const respondWithSecondOpinion = async (req, res) => {
  try {
    const diagnosis = req.body.diagnosis || req.body.doctorNotes;
    const recommendation = req.body.recommendation || (req.body.prescription ? JSON.stringify(req.body.prescription) : "Review completed by doctor");

    if (!diagnosis) {
      return res.status(400).json({ message: "Diagnosis or doctorNotes is required" });
    }

    const consultation = await submitSecondOpinion(
      req.params.id,
      req.user.organization,
      req.user.id,
      { diagnosis, recommendation }
    );

    if (!consultation) {
      return res.status(404).json({ message: "Consultation not found or not assigned to you" });
    }

    await logAuditEvent({
      req,
      action: "SECOND_OPINION_SUBMITTED",
      resourceType: "Consultation",
      resourceId: req.params.id,
    });

    return res.status(200).json({ message: "Second opinion submitted successfully", consultation });
  } catch (error) {
    if (error.name === "VersionError") {
      return res.status(409).json({ message: "Conflict: consultation was updated concurrently. Please refresh and try again." });
    }
    return res.status(error.status || 400).json({ message: error.message });
  }
};

// Trigger Server-Side Orchestrated AI Analysis (ML -> LLM -> PDF)
const triggerAnalysis = async (req, res) => {
  try {
    const { id } = req.params;
    const { language } = req.body;
    const idempotencyKey = req.headers["idempotency-key"] || req.headers["x-idempotency-key"] || req.body?.idempotencyKey;

    const consultation = await triggerConsultationAnalysis(
      id,
      req.user.organization,
      req.user,
      { language: language || "en" }
    );

    await logAuditEvent({
      req,
      action: "CONSULTATION_ANALYZED",
      resourceType: "Consultation",
      resourceId: consultation._id,
      metadata: {
        disease: consultation.mlAnalysis?.disease,
        confidence: consultation.mlAnalysis?.confidence,
        llmFallback: consultation.llmAnalysis?.llmFallback,
      },
    });

    return res.status(200).json({
      message: "Consultation analysis completed successfully",
      consultation,
    });
  } catch (error) {
    return res.status(error.statusCode || 500).json({
      message: error.message,
      code: error.code || "ANALYSIS_FAILED",
    });
  }
};

// Asynchronous background job enqueue (returns HTTP 202 immediately)
const triggerAnalysisAsync = async (req, res) => {
  try {
    const { id } = req.params;
    const { language } = req.body;
    const idempotencyKey = req.headers["idempotency-key"] || req.headers["x-idempotency-key"] || req.body?.idempotencyKey;

    const consultation = await Consultation.findOne({
      _id: id,
      organization: req.user.organization,
    }).populate("patient", "name age gender consentGiven revokedAt isDeleted");

    if (!consultation) {
      return res.status(404).json({
        message: "Consultation not found in your organization",
        code: "CONSULTATION_NOT_FOUND",
      });
    }

    if (
      !consultation.patient ||
      consultation.patient.consentGiven === false ||
      consultation.patient.revokedAt ||
      consultation.patient.isDeleted === true
    ) {
      return res.status(403).json({
        message: "Patient consent is inactive or has been withdrawn. Processing refused under DPDP Act.",
        code: "CONSENT_REQUIRED",
      });
    }

    if (idempotencyKey) {
      const existingJob = await AnalysisJob.findOne({
        idempotencyKey,
        organization: req.user.organization,
      });
      if (existingJob) {
        return res.status(202).json({
          message: "Analysis job already enqueued",
          job: {
            jobId: existingJob.jobId,
            status: existingJob.status,
            createdAt: existingJob.createdAt,
            isDuplicate: true,
          },
        });
      }
    }
    const job = enqueueAnalysisJob({
      consultationId: id,
      organization: req.user.organization,
      requestingUser: req.user,
      options: { language: language || "en" },
      idempotencyKey,
    });

    await logAuditEvent({
      req,
      action: "CONSULTATION_ANALYSIS_JOB_ENQUEUED",
      resourceType: "Consultation",
      resourceId: id,
      metadata: { jobId: job.jobId },
    });

    return res.status(202).json({
      message: "Analysis job accepted for processing",
      job,
    });
  } catch (error) {
    return res.status(error.statusCode || 500).json({
      message: error.message,
      code: error.code || "JOB_ENQUEUE_FAILED",
    });
  }
};

// Check status of asynchronous analysis job
const checkAnalysisJobStatus = async (req, res) => {
  try {
    const { jobId } = req.params;
    const job = await getJobStatusFromDb(jobId, req.user.organization);

    if (!job) {
      return res.status(404).json({
        message: "Analysis job not found in your organization",
        code: "JOB_NOT_FOUND",
      });
    }

    return res.status(200).json({
      message: "Analysis job status retrieved",
      job,
    });
  } catch (error) {
    return res.status(500).json({ message: error.message });
  }
};

// Queue diagnostics for observability
const getJobQueueDiagnostics = async (req, res) => {
  try {
    const metrics = getQueueMetrics();
    return res.status(200).json({ metrics });
  } catch (error) {
    return res.status(500).json({ message: error.message });
  }
};

// Store ML analysis (Direct client write disabled for security)
const storeMlAnalysisResult = async (req, res) => {
  return res.status(403).json({
    message: "Direct client analysis mutations are forbidden. Use POST /api/v1/consultation/:id/analyze for server-side orchestrated analysis.",
    code: "DIRECT_ANALYSIS_WRITE_FORBIDDEN",
  });
};

// Store LLM analysis (Direct client write disabled for security)
const storeLlmAnalysisResult = async (req, res) => {
  return res.status(403).json({
    message: "Direct client analysis mutations are forbidden. Use POST /api/v1/consultation/:id/analyze for server-side orchestrated analysis.",
    code: "DIRECT_ANALYSIS_WRITE_FORBIDDEN",
  });
};

// Store final verdict (Direct client write disabled for security)
const storeFinalVerdictResult = async (req, res) => {
  return res.status(403).json({
    message: "Direct client analysis mutations are forbidden. Use POST /api/v1/consultation/:id/analyze for server-side orchestrated analysis.",
    code: "DIRECT_ANALYSIS_WRITE_FORBIDDEN",
  });
};

// Store AI analysis PDF report (Direct client write disabled for security)
const storeAnalysisReportResult = async (req, res) => {
  return res.status(403).json({
    message: "Direct client analysis mutations are forbidden. Use POST /api/v1/consultation/:id/analyze for server-side orchestrated analysis.",
    code: "DIRECT_ANALYSIS_WRITE_FORBIDDEN",
  });
};


// Admin views aggregated organizational analytics (WP5)
const getConsultationAnalytics = async (req, res) => {
  try {
    const analytics = await getAdminAggregates(req.user.organization);
    return res.status(200).json({ analytics });
  } catch (error) {
    return res.status(500).json({ message: error.message });
  }
};


// Worker runs direct interactive triage analysis before consultation persistence
const runDirectTriage = async (req, res) => {
  try {
    const { symptoms, patientName, patientAge, patientGender, workerName, location, language } = req.body;

    if (!symptoms || !Array.isArray(symptoms) || symptoms.length === 0) {
      return res.status(400).json({
        success: false,
        message: "Symptoms list is required and must contain at least one symptom",
      });
    }

    // Mint internal service token
    const serviceToken = jwt.sign(
      {
        iss: "arogyamitra-backend",
        sub: req.user._id ? req.user._id.toString() : req.user.id,
        aud: "arogyamitra-internal",
        role: req.user.role || ROLES.WORKER,
        organization: req.user.organization?.toString() || "default",
      },
      serverConfig.INTERNAL_SERVICE_SECRET,
      { expiresIn: "5m" }
    );

    const payload = {
      symptoms,
      patientName: patientName || "Patient",
      patientAge: patientAge ? Number(patientAge) : undefined,
      patientGender: patientGender || undefined,
      workerName: workerName || req.user.name || "Community Health Worker",
      location: location || "",
      language: language || "en",
    };

    let response;
    try {
      const controller = new globalThis.AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 20000);

      response = await fetch(`${serverConfig.GRAPH_API_URL}/analyze/json`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Internal-Service-Token": serviceToken,
          "Authorization": `Bearer ${serviceToken}`,
        },
        body: JSON.stringify(payload),
        signal: controller.signal,
      });
      clearTimeout(timeoutId);
    } catch (netErr) {
      return res.status(503).json({
        success: false,
        code: "MODEL_UNAVAILABLE",
        message: `AI Pipeline unreachable: ${netErr.message}`,
      });
    }

    if (!response.ok) {
      const errText = await response.text();
      return res.status(503).json({
        success: false,
        code: "MODEL_UNAVAILABLE",
        message: `AI Pipeline failed with HTTP ${response.status}: ${errText}`,
      });
    }

    const data = await response.json();
    const boundaryCheck = validatePredictionBoundary(data.mlResult);
    if (!boundaryCheck.valid) {
      return res.status(503).json({
        success: false,
        code: "MODEL_UNAVAILABLE",
        message: `Prediction boundary violation: ${boundaryCheck.reason}`,
      });
    }

    return res.status(200).json({
      success: true,
      mlResult: data.mlResult,
      llmResult: data.llmResult,
      pdfBase64: data.pdfBase64,
      filename: data.filename,
    });
  } catch (error) {
    return res.status(500).json({
      success: false,
      code: "INTERNAL_SERVER_ERROR",
      message: error.message,
    });
  }
};

export {
  submitConsultation,
  getMyConsultations,
  getConsultation,
  acceptAI,
  escalate,
  getPendingForDoctor,
  getAllForDoctor,
  respondWithSecondOpinion,
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
  getNotifications,
  runDirectTriage,
};
