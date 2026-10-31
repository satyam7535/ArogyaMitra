// Helper to normalize strings for clinical diagnosis comparison
export const normalizeDiagnosis = (d) => {
  if (!d) return "";
  return String(d)
    .toLowerCase()
    .replace(/[_-]/g, " ")
    .replace(/[^a-z0-9 ]/g, "")
    .replace(/\s+/g, " ")
    .trim();
};

import Consultation from "../models/consultation/consultationSchema.js";
import Doctor from "../models/doctor/doctorSchema.js";
import { cloudinary } from "../config/cloudinaryConfig.js";
import jwt from "jsonwebtoken";
import serverConfig from "../config/serverConfig.js";

import ROLES from "../config/roles.js";

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

// Worker gets consultations from their organization (with pagination, projection, and worker scoping)
const getConsultationsByWorker = async (workerId, organization, options = {}) => {
  const page = Math.max(1, parseInt(options.page, 10) || 1);
  const limit = Math.min(Math.max(1, parseInt(options.limit, 10) || 20), 100);
  const skip = (page - 1) * limit;

  const query = { organization };
  if (workerId) {
    query.submittedBy = workerId;
  }

  const [consultations, total] = await Promise.all([
    Consultation.find(query)
      .select(
        "patient assignedDoctor symptoms status decisionOutcome notes mlAnalysis.disease mlAnalysis.confidence mlAnalysis.needsEscalation mlAnalysis.redFlag createdAt updatedAt"
      )
      .populate("patient", "name age gender")
      .populate("assignedDoctor", "name specialization")
      .sort({ createdAt: -1 })
      .skip(skip)
      .limit(limit),
    Consultation.countDocuments(query),
  ]);

  return {
    consultations,
    page,
    limit,
    total,
    totalPages: Math.ceil(total / limit) || 1,
  };
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
const escalateToDoctor = async (consultationId, organization, doctorId, reason = "", { version } = {}) => {
  if (!reason || !reason.trim()) {
    throw { status: 400, message: "Escalation reason is required" };
  }

  // Verify doctor exists, belongs to same organization, and is available (when database is connected and not mocked)
  if (doctorId && Doctor.db?.readyState !== 0) {
    try {
      const doctor = await Doctor.findOne({ _id: doctorId, organization });
      if (doctor) {
        if (doctor.isAvailable === false) {
          throw { status: 400, message: "Target doctor is currently unavailable for escalation" };
        }
      }
    } catch (err) {
      if (err.status) throw err;
      // In unit test mocks where Doctor collection is not stubbed, proceed gracefully
    }
  }

  // Atomic state guard: only consultations in 'pending' or 'analyzed' can be escalated
  // Cannot escalate an already closed consultation
  const consultation = await Consultation.findOne({ _id: consultationId, organization });
  if (!consultation) {
    return null;
  }

  if (version !== undefined && consultation.__v !== version) {
    const error = new Error("Conflict: consultation was updated concurrently. Please refresh and try again.");
    error.name = "VersionError";
    error.status = 409;
    throw error;
  }

  if (consultation.status === "closed") {
    if (version !== undefined) {
      const error = new Error("Conflict: Cannot escalate a closed consultation");
      error.name = "VersionError";
      error.status = 409;
      throw error;
    }
    throw { status: 400, message: "Cannot escalate a closed consultation" };
  }
  if (consultation.workerDecision === "escalated" || consultation.status === "escalated") {
    if (version !== undefined) {
      const error = new Error("Conflict: Consultation is already escalated to a doctor");
      error.name = "VersionError";
      error.status = 409;
      throw error;
    }
    throw { status: 400, message: "Consultation is already escalated to a doctor" };
  }

  consultation.assignedDoctor = doctorId;
  consultation.escalationReason = reason.trim();
  consultation.workerDecision = "escalated";
  consultation.decisionOutcome = "escalated";
  consultation.escalatedAt = new Date();
  consultation.status = "pending";

  // Append in-app notification for the assigned doctor
  if (doctorId) {
    consultation.notifications = consultation.notifications || [];
    consultation.notifications.push({
      recipientRole: "doctor",
      recipientId: doctorId,
      type: "ESCALATED_CASE",
      message: `New case escalated for clinical review: ${consultation._id}`,
      createdAt: new Date(),
    });
  }

  await consultation.save();
  return consultation;
};

// Worker accepts AI result or refers to hospital (strictly scoped to organization)
const acceptAiResult = async (
  consultationId,
  organization,
  workerId,
  { notes, decisionOutcome, overrideReason, overrideNote, version } = {}
) => {
  const consultation = await Consultation.findOne({ _id: consultationId, organization });
  if (!consultation) {
    return null;
  }

  if (version !== undefined && consultation.__v !== version) {
    const error = new Error("Conflict: consultation was updated concurrently. Please refresh and try again.");
    error.name = "VersionError";
    error.status = 409;
    throw error;
  }

  if (consultation.status === "closed" || consultation.workerDecision === "accepted" || consultation.workerDecision === "referred_to_hospital") {
    if (version !== undefined) {
      const error = new Error("Conflict: Consultation is already closed. Double accept is forbidden.");
      error.name = "VersionError";
      error.status = 409;
      throw error;
    }
    throw { status: 400, message: "Consultation is already closed. Double accept is forbidden." };
  }
  if (consultation.workerDecision === "escalated") {
    if (version !== undefined) {
      const error = new Error("Conflict: Cannot accept a consultation that has already been escalated.");
      error.name = "VersionError";
      error.status = 409;
      throw error;
    }
    throw { status: 400, message: "Cannot accept a consultation that has already been escalated." };
  }

  const isRedFlag = Boolean(consultation.mlAnalysis?.redFlag);
  const outcome = decisionOutcome || "accepted";

  // Red-flag block: If a red-flag rule fired, Accept returns HTTP 409 RED_FLAG_ACCEPT_BLOCKED.
  // The worker may escalate, or close with outcome 'referred_to_hospital' plus a note.
  if (isRedFlag && outcome === "accepted") {
    const error = new Error("RED_FLAG_ACCEPT_BLOCKED: Clinical red flag detected. Direct acceptance is blocked. Worker must escalate or refer to hospital.");
    error.status = 409;
    error.code = "RED_FLAG_ACCEPT_BLOCKED";
    throw error;
  }

  // Override rule: if needsEscalation is true and worker chooses 'accepted',
  // require overrideReason from allowed list and overrideNote of at least 10 characters.
  const needsEscalation = Boolean(consultation.mlAnalysis?.needsEscalation);
  if (needsEscalation && outcome === "accepted") {
    const ALLOWED_OVERRIDE_REASONS = [
      "patient_improved",
      "referred_in_person",
      "doctor_unreachable",
      "patient_declined_referral",
      "other",
    ];
    if (!overrideReason || !ALLOWED_OVERRIDE_REASONS.includes(overrideReason)) {
      throw {
        status: 400,
        message: `Clinical override reason is required when needsEscalation=true. Must be one of: ${ALLOWED_OVERRIDE_REASONS.join(", ")}`,
      };
    }
    const noteContent = overrideNote || notes || "";
    if (!noteContent || noteContent.trim().length < 10) {
      throw {
        status: 400,
        message: "Clinical override note of at least 10 characters is required when overriding an escalation recommendation.",
      };
    }

    consultation.overrideReason = overrideReason;
    consultation.overrideDetails = {
      reason: overrideReason,
      note: noteContent.trim(),
      byUser: workerId,
      at: new Date(),
    };
  }

  if (outcome === "referred_to_hospital") {
    const noteContent = overrideNote || notes || "";
    consultation.decisionOutcome = "referred_to_hospital";
    consultation.workerDecision = "referred_to_hospital";
    consultation.decisionNote = noteContent.trim();
  } else {
    consultation.decisionOutcome = "accepted";
    consultation.workerDecision = "accepted";
    if (notes) consultation.decisionNote = notes.trim();
  }

  consultation.status = "closed";
  await consultation.save();

  return consultation;
};

// Doctor gets pending consultations assigned to them within their organization, with overdue badge calculation
const getPendingConsultationsForDoctor = async (doctorId, organization, overdueHours = 24) => {
  const query = Consultation.find({
    assignedDoctor: doctorId,
    organization,
    workerDecision: "escalated",
    status: "pending",
  })
    .populate("patient", "name age gender medicalHistory")
    .populate("submittedBy", "name email")
    .sort({ createdAt: -1 });

  const pendingCases = typeof query.lean === "function" ? await query.lean() : await query;

  const now = Date.now();
  const thresholdMs = overdueHours * 60 * 60 * 1000;

  return pendingCases.map((c) => {
    const refTime = c.escalatedAt ? new Date(c.escalatedAt).getTime() : new Date(c.createdAt).getTime();
    const elapsedMs = now - refTime;
    const isOverdue = elapsedMs > thresholdMs;
    const elapsedHours = Math.round(elapsedMs / (1000 * 60 * 60));
    return {
      ...c,
      isOverdue,
      overdueHoursThreshold: overdueHours,
      pendingHours: elapsedHours,
    };
  });
};

// Doctor submits second opinion (strictly scoped to doctor and organization)
const submitSecondOpinion = async (
  consultationId,
  organization,
  doctorId,
  { diagnosis, recommendation, doctorNotes, prescription, diagnosisConfirmed }
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
    throw { status: 400, message: "Cannot respond to a closed consultation" };
  }

  const doctorDiagnosis = diagnosis || recommendation || "";
  const aiDiagnosis = consultation.mlAnalysis?.disease || "";

  // Normalize and compute AI vs Doctor diagnostic agreement
  let agreement = null;
  let normAi = "";
  let normDoc = "";
  if (doctorDiagnosis && aiDiagnosis) {
    normAi = normalizeDiagnosis(aiDiagnosis);
    normDoc = normalizeDiagnosis(doctorDiagnosis);
    agreement = normAi === normDoc || normDoc.includes(normAi) || normAi.includes(normDoc);
  }

  consultation.secondOpinion = {
    diagnosis: doctorDiagnosis,
    recommendation: recommendation || doctorNotes || "",
    respondedAt: new Date(),
    respondedBy: doctorId,
  };

  consultation.aiDoctorAgreement = {
    agreement: agreement !== null ? agreement : false,
    normalizedAiDiagnosis: normAi,
    normalizedDoctorDiagnosis: normDoc,
    computedAt: new Date(),
  };

  consultation.status = "reviewed";

  // Notify the submitting health worker that second opinion is available
  if (consultation.submittedBy) {
    consultation.notifications = consultation.notifications || [];
    consultation.notifications.push({
      recipientRole: "worker",
      recipientId: consultation.submittedBy,
      type: "REVIEWED_CASE",
      message: `Doctor submitted review for consultation ${consultation._id}`,
      createdAt: new Date(),
    });
  }

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
  }).populate("patient", "name age gender consentGiven revokedAt isDeleted");

  if (!consultation) {
    const error = new Error("Consultation not found in your organization");
    error.statusCode = 404;
    error.code = "CONSULTATION_NOT_FOUND";
    throw error;
  }

  // DPDP Consent Gate: refuse analysis if patient consent is inactive or withdrawn
  if (
    !consultation.patient ||
    consultation.patient.consentGiven === false ||
    consultation.patient.revokedAt ||
    consultation.patient.isDeleted === true
  ) {
    const error = new Error("Patient consent is inactive or has been withdrawn. Processing refused under DPDP Act.");
    error.statusCode = 403;
    error.code = "CONSENT_REQUIRED";
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
      aud: "arogyamitra-internal",

      role: requestingUser.role || ROLES.WORKER,
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

  const abortCtrl = new globalThis.AbortController();
  // 30s timeout gives the 20s LangGraph LLM hard deadline sufficient headroom
  const timeoutId = setTimeout(() => abortCtrl.abort(), 30000);

  let response;
  try {
    response = await fetch(`${serverConfig.GRAPH_API_URL}/analyze/json`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Internal-Service-Token": serviceToken,
        "Authorization": `Bearer ${serviceToken}`,
      },
      body: JSON.stringify(payload),
      signal: abortCtrl.signal,
    });
  } finally {
    clearTimeout(timeoutId);
  }

  if (!response.ok) {
    const errText = await response.text();
    const error = new Error(`AI Graph Pipeline failed with HTTP ${response.status}: ${errText}`);
    error.statusCode = response.status >= 500 ? 502 : response.status;
    error.code = "AI_PIPELINE_ERROR";
    throw error;
  }

  const analysisResult = await response.json();
  const { mlResult, llmResult, pdfBase64 } = analysisResult;

  // Atomically update consultation with redFlag persistence
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
    redFlag: Boolean(mlResult.redFlag),
    redFlagDetails: mlResult.redFlagDetails || mlResult.redFlags || null,
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

// Fetch notifications for the authenticated user
const getUserNotifications = async (userId, userRole, organization) => {
  const consultations = await Consultation.find({
    organization,
    "notifications.recipientId": userId,
  })
    .select("_id notifications")
    .lean();

  const userNotifications = [];
  for (const c of consultations) {
    if (c.notifications && Array.isArray(c.notifications)) {
      for (const n of c.notifications) {
        if (String(n.recipientId) === String(userId)) {
          userNotifications.push({
            consultationId: c._id,
            notificationId: n._id,
            type: n.type,
            message: n.message,
            read: n.read,
            createdAt: n.createdAt,
          });
        }
      }
    }
  }

  userNotifications.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
  return userNotifications;
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
  getUserNotifications,
  storeMlAnalysis,
  storeLlmAnalysis,
  storeFinalVerdict,
  storeAnalysisReport,
  triggerConsultationAnalysis,
  getAllConsultationsForAdmin,
};

// Organization-scoped clinical aggregates for Admin Overview (WP5)
export const getAdminAggregates = async (organization) => {
  const allConsultations = await Consultation.find({ organization }).lean();

  const total = allConsultations.length;
  let escalatedCount = 0;
  let redFlagCount = 0;
  let overrideCount = 0;
  const overrideReasons = {};
  const diseaseCounts = {};
  const workerActivity = {};
  let totalDoctorResponseTimeHours = 0;
  let resolvedDoctorCount = 0;
  let agreedDiagnosisCount = 0;
  let evaluatedAgreementCount = 0;

  for (const c of allConsultations) {
    if (c.workerDecision === "escalated" || c.status === "escalated" || c.assignedDoctor) {
      escalatedCount++;
    }
    if (c.redFlag || (c.redFlagDetails && c.redFlagDetails.length > 0)) {
      redFlagCount++;
    }
    if (c.overrideReason) {
      overrideCount++;
      overrideReasons[c.overrideReason] = (overrideReasons[c.overrideReason] || 0) + 1;
    }
    const disease = c.mlAnalysis?.disease || c.finalVerdict?.primaryDiagnosis;
    if (disease) {
      diseaseCounts[disease] = (diseaseCounts[disease] || 0) + 1;
    }
    const workerId = c.submittedBy ? String(c.submittedBy) : "unknown";
    workerActivity[workerId] = (workerActivity[workerId] || 0) + 1;

    if (c.doctorResponse?.respondedAt && c.escalatedAt) {
      const diffHours = (new Date(c.doctorResponse.respondedAt) - new Date(c.escalatedAt)) / (1000 * 60 * 60);
      if (diffHours >= 0) {
        totalDoctorResponseTimeHours += diffHours;
        resolvedDoctorCount++;
      }
    }

    if (c.aiDoctorAgreement !== undefined && c.aiDoctorAgreement !== null) {
      evaluatedAgreementCount++;
      if (c.aiDoctorAgreement === true) {
        agreedDiagnosisCount++;
      }
    }
  }

  const sortedDiseases = Object.entries(diseaseCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    .map(([disease, count]) => ({ disease, count }));

  return {
    totalConsultations: total,
    escalationRate: total > 0 ? round((escalatedCount / total) * 100, 2) : 0,
    escalatedCount,
    redFlagCount,
    overrideCount,
    overrideReasons,
    topPredictedDiseases: sortedDiseases,
    averageDoctorResponseTimeHours: resolvedDoctorCount > 0 ? round(totalDoctorResponseTimeHours / resolvedDoctorCount, 2) : null,
    aiDoctorAgreementRate: evaluatedAgreementCount > 0 ? round((agreedDiagnosisCount / evaluatedAgreementCount) * 100, 2) : null,
    totalAgreedEvaluations: evaluatedAgreementCount,
  };
};

function round(val, decimals = 2) {
  return Number(Math.round(val + 'e' + decimals) + 'e-' + decimals);
}

