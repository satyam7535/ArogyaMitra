import {
  createConsultation,
  getConsultationsByWorker,
  getConsultationById,
  escalateToDoctor,
  acceptAiResult,
  getPendingConsultationsForDoctor,
  getAllConsultationsForDoctor,
  submitSecondOpinion,
  storeMlAnalysis,
  storeLlmAnalysis,
  storeFinalVerdict,
  storeAnalysisReport,
  triggerConsultationAnalysis,
  getAllConsultationsForAdmin,
} from "../service/consultation.service.js";
import { logAuditEvent } from "../middlewares/audit.middleware.js";

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

// Worker views all consultations from their organization
const getMyConsultations = async (req, res) => {
  try {
    const consultations = await getConsultationsByWorker(req.user.id, req.user.organization);
    return res.status(200).json({ consultations });
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

// Worker accepts AI result — closes consultation
const acceptAI = async (req, res) => {
  try {
    const consultation = await acceptAiResult(req.params.id, req.user.organization, req.user.id);
    if (!consultation) {
      return res.status(404).json({ message: "Consultation not found" });
    }

    await logAuditEvent({
      req,
      action: "CONSULTATION_ACCEPTED_AI",
      resourceType: "Consultation",
      resourceId: req.params.id,
    });

    return res.status(200).json({ message: "AI result accepted. Consultation closed.", consultation });
  } catch (error) {
    return res.status(error.status || 400).json({ message: error.message });
  }
};

// Worker escalates to doctor for second opinion
const escalate = async (req, res) => {
  try {
    const { doctorId, reason } = req.body;
    if (!doctorId) return res.status(400).json({ message: "doctorId is required" });

    const consultation = await escalateToDoctor(
      req.params.id,
      req.user.organization,
      doctorId,
      reason
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
    return res.status(400).json({ message: error.message });
  }
};

// Doctor views all pending consultations assigned to them within their organization
const getPendingForDoctor = async (req, res) => {
  try {
    const consultations = await getPendingConsultationsForDoctor(req.user.id, req.user.organization);
    return res.status(200).json({ consultations });
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
    const { diagnosis, recommendation } = req.body;

    if (!diagnosis || !recommendation) {
      return res.status(400).json({ message: "Diagnosis and recommendation are required" });
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
    return res.status(error.status || 400).json({ message: error.message });
  }
};

// Trigger Server-Side Orchestrated AI Analysis (ML -> LLM -> PDF)
const triggerAnalysis = async (req, res) => {
  try {
    const { id } = req.params;
    const { language } = req.body;

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
  storeMlAnalysisResult,
  storeLlmAnalysisResult,
  storeFinalVerdictResult,
  storeAnalysisReportResult,
  getAdminConsultations,
};
