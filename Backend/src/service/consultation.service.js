import Consultation from "../models/consultation/consultationSchema.js";
import { cloudinary } from "../config/cloudinaryConfig.js";
import jwt from "jsonwebtoken";
import serverConfig from "../config/serverConfig.js";

// Helper: upload a buffer to Cloudinary
const uploadToCloudinary = (buffer, folder, resourceType = "auto") => {
  return new Promise((resolve, reject) => {
    const stream = cloudinary.uploader.upload_stream(
      { folder, resource_type: resourceType },
      (error, result) => {
        if (error) reject(error);
        else resolve(result.secure_url);
      }
    );
    stream.end(buffer);
  });
};

// Worker submits a new consultation
const createConsultation = async (
  { patientId, symptoms, notes, attachmentFiles, aiReportFile },
  workerId,
  organization
) => {
  let attachmentUrls = [];
  if (attachmentFiles && attachmentFiles.length > 0) {
    attachmentUrls = await Promise.all(
      attachmentFiles.map((file) =>
        uploadToCloudinary(file.buffer, "consultations/attachments")
      )
    );
  }

  let aiReportUrl = null;
  if (aiReportFile) {
    aiReportUrl = await uploadToCloudinary(aiReportFile.buffer, "consultations/ai-reports");
  }

  const consultation = await Consultation.create({
    patient: patientId,
    submittedBy: workerId,
    organization,
    symptoms,
    notes,
    attachments: attachmentUrls,
    aiReport: aiReportUrl,
    status: "pending",
  });

  return consultation;
};

// Worker gets all consultations from their organization
const getConsultationsByWorker = async (workerId, organization) => {
  return await Consultation.find({ organization })
    .populate("patient", "name age gender")
    .populate("assignedDoctor", "name specialization")
    .sort({ createdAt: -1 });
};

// Admin gets all consultations from their organization
const getAllConsultationsForAdmin = async (adminId, organization) => {
  return await Consultation.find({ organization })
    .populate("patient", "name age gender")
    .populate("submittedBy", "name email")
    .populate("assignedDoctor", "name specialization")
    .sort({ createdAt: -1 });
};

// Get a single consultation by ID (strictly scoped to organization)
const getConsultationById = async (consultationId, organization) => {
  return await Consultation.findOne({ _id: consultationId, organization })
    .populate("patient")
    .populate("submittedBy", "name email")
    .populate("assignedDoctor", "name specialization email");
};

// Worker escalates to doctor (strictly scoped to organization)
const escalateToDoctor = async (consultationId, organization, doctorId, reason = "") => {
  const consultation = await Consultation.findOne({ _id: consultationId, organization });
  if (!consultation) {
    return null;
  }

  consultation.assignedDoctor = doctorId;
  consultation.escalationReason = reason;
  consultation.workerDecision = "escalated";
  consultation.status = "pending";
  await consultation.save();

  return consultation;
};

// Worker accepts AI result (strictly scoped to organization)
const acceptAiResult = async (consultationId, organization, _workerId) => {
  const consultation = await Consultation.findOne({ _id: consultationId, organization });
  if (!consultation) {
    return null;
  }

  if (consultation.status === "closed") {
    throw { status: 400, message: "Consultation is already closed" };
  }

  consultation.workerDecision = "accepted";
  consultation.status = "closed";
  await consultation.save();

  return consultation;
};

// Doctor gets pending consultations assigned to them within their organization
const getPendingConsultationsForDoctor = async (doctorId, organization) => {
  return await Consultation.find({
    assignedDoctor: doctorId,
    organization,
    workerDecision: "escalated",
    status: "pending",
  })
    .populate("patient", "name age gender medicalHistory")
    .populate("submittedBy", "name email")
    .sort({ createdAt: -1 });
};

// Doctor submits second opinion (strictly scoped to doctor and organization)
const submitSecondOpinion = async (
  consultationId,
  organization,
  doctorId,
  { diagnosis, recommendation }
) => {
  const consultation = await Consultation.findOne({
    _id: consultationId,
    organization,
    assignedDoctor: doctorId,
  });

  if (!consultation) {
    return null;
  }

  if (consultation.status === "closed") {
    throw { status: 400, message: "This consultation is already closed" };
  }

  consultation.secondOpinion = {
    diagnosis,
    recommendation,
    respondedAt: new Date(),
  };
  consultation.status = "reviewed";
  await consultation.save();

  return consultation;
};

// Doctor gets ALL consultations assigned to them within their organization
const getAllConsultationsForDoctor = async (doctorId, organization) => {
  return await Consultation.find({
    assignedDoctor: doctorId,
    organization,
  })
    .populate("patient", "name age gender medicalHistory")
    .populate("submittedBy", "name email")
    .sort({ createdAt: -1 });
};

// Store ML analysis result
const storeMlAnalysis = async (consultationId, organization, mlResult) => {
  const consultation = await Consultation.findOne({ _id: consultationId, organization });
  if (!consultation) return null;

  consultation.mlAnalysis = {
    disease: mlResult.disease,
    confidence: mlResult.confidence,
    precautions: mlResult.precautions,
    analyzedAt: new Date(),
  };
  await consultation.save();
  return consultation;
};

// Store LLM analysis result
const storeLlmAnalysis = async (consultationId, organization, llmResult) => {
  const consultation = await Consultation.findOne({ _id: consultationId, organization });
  if (!consultation) return null;

  consultation.llmAnalysis = {
    summary: llmResult.summary,
    recommendations: llmResult.recommendations,
    riskLevel: llmResult.riskLevel,
    analyzedAt: new Date(),
  };
  await consultation.save();
  return consultation;
};

// Store final verdict
const storeFinalVerdict = async (consultationId, organization, verdict) => {
  const consultation = await Consultation.findOne({ _id: consultationId, organization });
  if (!consultation) return null;

  consultation.finalVerdict = {
    conclusion: verdict,
    generatedAt: new Date(),
  };
  await consultation.save();
  return consultation;
};

// Store analysis report PDF
const storeAnalysisReport = async (consultationId, organization, pdfBuffer) => {
  const consultation = await Consultation.findOne({ _id: consultationId, organization });
  if (!consultation) return null;

  const reportUrl = await uploadToCloudinary(pdfBuffer, "consultations/analysis-reports", "auto");
  consultation.analysisReport = reportUrl;
  await consultation.save();
  return consultation;
};

// Orchestrate Server-Side AI Analysis (ML -> Safe LLM -> Multilingual PDF)
const triggerConsultationAnalysis = async (consultationId, organization, requestingUser, options = {}) => {
  const consultation = await Consultation.findOne({
    _id: consultationId,
    organization,
  }).populate("patient", "name age gender");

  if (!consultation) {
    const error = new Error("Consultation not found in your organization");
    error.statusCode = 404;
    error.code = "CONSULTATION_NOT_FOUND";
    throw error;
  }

  if (!consultation.symptoms || consultation.symptoms.length === 0) {
    const error = new Error("Consultation has no symptoms to analyze");
    error.statusCode = 400;
    error.code = "NO_SYMPTOMS_FOUND";
    throw error;
  }

  // Mint signed internal service JWT token
  const serviceToken = jwt.sign(
    {
      iss: "arogyamitra-backend",
      sub: requestingUser._id ? requestingUser._id.toString() : requestingUser.id,
      role: requestingUser.role || "worker",
      organization: organization.toString(),
      consultationId: consultationId.toString(),
    },
    serverConfig.INTERNAL_SERVICE_SECRET,
    { expiresIn: "5m" }
  );

  const payload = {
    symptoms: consultation.symptoms,
    patientName: consultation.patient?.name || "Patient",
    patientAge: consultation.patient?.age,
    patientGender: consultation.patient?.gender,
    workerName: requestingUser.name || "Healthcare Worker",
    language: options.language || "en",
  };

  const response = await fetch(`${serverConfig.GRAPH_API_URL}/analyze/json`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Internal-Service-Token": serviceToken,
      "Authorization": `Bearer ${serviceToken}`,
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errText = await response.text();
    const error = new Error(`AI Graph Pipeline failed with HTTP ${response.status}: ${errText}`);
    error.statusCode = response.status >= 500 ? 502 : response.status;
    error.code = "AI_PIPELINE_ERROR";
    throw error;
  }

  const analysisResult = await response.json();
  const { mlResult, llmResult, pdfBase64 } = analysisResult;

  // Atomically update consultation
  consultation.mlAnalysis = {
    disease: mlResult.disease,
    confidence: mlResult.confidence,
    severityScore: mlResult.severityScore,
    topPredictions: mlResult.topPredictions || [],
    matchedSymptoms: mlResult.matchedSymptoms || [],
    precautions: mlResult.precautions || [],
    description: mlResult.description || "",
    shapExplanation: mlResult.shapExplanation || [],
    needsEscalation: mlResult.needsEscalation || false,
    uncertaintyReason: mlResult.uncertaintyReason || null,
    analyzedAt: new Date(),
  };

  consultation.llmAnalysis = {
    summary: llmResult.diagnosis_summary,
    confidenceInterpretation: llmResult.confidence_interpretation,
    severityAssessment: llmResult.severity_assessment,
    keyFactors: llmResult.key_contributing_factors,
    recommendations: llmResult.recommended_next_steps,
    referral: llmResult.referral_recommendation,
    llmFallback: llmResult.llmFallback || false,
    analyzedAt: new Date(),
  };

  consultation.finalVerdict = {
    conclusion: llmResult.diagnosis_summary,
    generatedAt: new Date(),
  };

  if (pdfBase64) {
    consultation.analysisReport = `data:application/pdf;base64,${pdfBase64}`;
  }

  consultation.status = "analyzed";
  await consultation.save();

  return consultation;
};

export {
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
};
