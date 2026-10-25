import Consultation from "../models/consultation/consultationSchema.js";
import Worker from "../models/worker/workerSchema.js";
import { cloudinary } from "../config/cloudinaryConfig.js";

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
const createConsultation = async ({ patientId, symptoms, notes, attachmentFiles, aiReportFile }, workerId) => {
    // Upload patient report attachments to Cloudinary
    let attachmentUrls = [];
    if (attachmentFiles && attachmentFiles.length > 0) {
        attachmentUrls = await Promise.all(
            attachmentFiles.map(file => uploadToCloudinary(file.buffer, "consultations/attachments"))
        );
    }

    // Upload AI-generated report if provided
    let aiReportUrl = null;
    if (aiReportFile) {
        aiReportUrl = await uploadToCloudinary(aiReportFile.buffer, "consultations/ai-reports");
    }

    const consultation = await Consultation.create({
        patient: patientId,
        submittedBy: workerId,
        symptoms,
        notes,
        attachments: attachmentUrls,
        aiReport: aiReportUrl,
        status: "pending",
    });

    return consultation;
};

// Worker gets all consultations from their organization (same admin)
const getConsultationsByWorker = async (workerId) => {
    const worker = await Worker.findById(workerId);
    if (!worker) return [];

    return await getAllConsultationsForAdmin(worker.addedBy);
};

// Admin gets all consultations from their organization
const getAllConsultationsForAdmin = async (adminId) => {
    // Find all workers under this admin
    const workers = await Worker.find({ addedBy: adminId }).select("_id");
    const workerIds = workers.map(w => w._id);

    return await Consultation.find({ submittedBy: { $in: workerIds } })
        .populate("patient", "name age gender")
        .populate("assignedDoctor", "name specialization")
        .sort({ createdAt: -1 });
};

// Get a single consultation by ID
const getConsultationById = async (consultationId) => {
    return await Consultation.findById(consultationId)
        .populate("patient")
        .populate("submittedBy", "name email")
        .populate("assignedDoctor", "name specialization email");
};

// Worker escalates to doctor (second opinion)
const escalateToDoctor = async (consultationId, doctorId, workerId, reason = "") => {
    const consultation = await Consultation.findById(consultationId);

    if (!consultation) {
        throw new Error("Consultation not found");
    }

    // Verify worker belongs to same admin organization as the consultation's original submitter
    const [worker, submitter] = await Promise.all([
        Worker.findById(workerId),
        Worker.findById(consultation.submittedBy)
    ]);

    if (!worker || !submitter || worker.addedBy.toString() !== submitter.addedBy.toString()) {
        throw new Error("Unauthorized to escalate this consultation");
    }

    consultation.assignedDoctor = doctorId;
    consultation.escalationReason = reason;
    consultation.workerDecision = "escalated";
    consultation.status = "pending";
    await consultation.save();

    return consultation;
};

// Worker closes a consultation
const acceptAiResult = async (consultationId, workerId) => {
    const consultation = await Consultation.findOne({
        _id: consultationId,
        submittedBy: workerId,
    });

    if (!consultation) {
        throw new Error("Consultation not found or unauthorized");
    }

    if (consultation.status === "closed") {
        throw new Error("Consultation is already closed");
    }

    consultation.workerDecision = "accepted";
    consultation.status = "closed";
    await consultation.save();

    return consultation;
};

// Doctor gets all pending consultations assigned to them
const getPendingConsultationsForDoctor = async (doctorId) => {
    return await Consultation.find({
        assignedDoctor: doctorId,
        workerDecision: "escalated",
        status: "pending",
    })
        .populate("patient", "name age gender medicalHistory")
        .populate("submittedBy", "name email")
        .sort({ createdAt: -1 });
};

// Doctor submits second opinion
const submitSecondOpinion = async (consultationId, doctorId, { diagnosis, recommendation }) => {
    const consultation = await Consultation.findOne({
        _id: consultationId,
        assignedDoctor: doctorId,
    });

    if (!consultation) {
        throw new Error("Consultation not found or not assigned to you");
    }

    if (consultation.status === "closed") {
        throw new Error("This consultation is already closed");
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

// Doctor gets ALL consultations assigned to them (pending + reviewed)
const getAllConsultationsForDoctor = async (doctorId) => {
    return await Consultation.find({
        assignedDoctor: doctorId,
    })
        .populate("patient", "name age gender medicalHistory")
        .populate("submittedBy", "name email")
        .sort({ createdAt: -1 });
};

// Store ML analysis result
const storeMlAnalysis = async (consultationId, mlResult) => {
    const consultation = await Consultation.findById(consultationId);
    if (!consultation) throw new Error("Consultation not found");

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
const storeLlmAnalysis = async (consultationId, llmResult) => {
    const consultation = await Consultation.findById(consultationId);
    if (!consultation) throw new Error("Consultation not found");

    consultation.llmAnalysis = {
        summary: llmResult.summary,
        recommendations: llmResult.recommendations,
        riskLevel: llmResult.riskLevel,
        analyzedAt: new Date(),
    };
    await consultation.save();
    return consultation;
};

// Store final verdict from combined analysis
const storeFinalVerdict = async (consultationId, verdict) => {
    const consultation = await Consultation.findById(consultationId);
    if (!consultation) throw new Error("Consultation not found");

    consultation.finalVerdict = {
        conclusion: verdict,
        generatedAt: new Date(),
    };
    await consultation.save();
    return consultation;
};

// Store analysis report PDF — uploads buffer to Cloudinary, saves URL
const storeAnalysisReport = async (consultationId, pdfBuffer) => {
    const consultation = await Consultation.findById(consultationId);
    if (!consultation) throw new Error("Consultation not found");

    // Use "auto" so Cloudinary detects it's a PDF
    const reportUrl = await uploadToCloudinary(pdfBuffer, "consultations/analysis-reports", "auto");
    consultation.analysisReport = reportUrl;
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
    getAllConsultationsForAdmin,
};
