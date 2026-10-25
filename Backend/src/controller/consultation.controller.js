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
    getAllConsultationsForAdmin,
} from "../service/consultation.service.js";

// Worker submits a new consultation
// Accepts: multipart/form-data
// Fields: patientId, symptoms (comma-separated or JSON array), notes
// Files: attachments (multiple), aiReport (single, optional)
const submitConsultation = async (req, res) => {
    try {
        const { patientId, symptoms, notes } = req.body;

        if (!patientId || !symptoms) {
            return res.status(400).json({ message: "patientId and symptoms are required" });
        }

        // symptoms can be sent as JSON array string or comma-separated
        let symptomsArray = symptoms;
        if (typeof symptoms === "string") {
            try {
                symptomsArray = JSON.parse(symptoms);
            } catch {
                symptomsArray = symptoms.split(",").map(s => s.trim());
            }
        }

        const attachmentFiles = req.files?.attachments || [];
        const aiReportFile = req.files?.aiReport?.[0] || null;

        const consultation = await createConsultation(
            { patientId, symptoms: symptomsArray, notes, attachmentFiles, aiReportFile },
            req.user.id
        );

        return res.status(201).json({ message: "Consultation submitted successfully", consultation });
    } catch (error) {
        return res.status(500).json({ message: error.message });
    }
};

// Worker views all their consultations
const getMyConsultations = async (req, res) => {
    try {
        const consultations = await getConsultationsByWorker(req.user.id);
        return res.status(200).json({ consultations });
    } catch (error) {
        return res.status(500).json({ message: error.message });
    }
};

// Admin views all consultations in their organization
const getAdminConsultations = async (req, res) => {
    try {
        const consultations = await getAllConsultationsForAdmin(req.user.id);
        return res.status(200).json({ consultations });
    } catch (error) {
        return res.status(500).json({ message: error.message });
    }
};

// Get a single consultation (worker or doctor)
const getConsultation = async (req, res) => {
    try {
        const consultation = await getConsultationById(req.params.id);
        if (!consultation) return res.status(404).json({ message: "Consultation not found" });
        return res.status(200).json({ consultation });
    } catch (error) {
        return res.status(500).json({ message: error.message });
    }
};

// Worker accepts AI result — closes consultation
const acceptAI = async (req, res) => {
    try {
        const consultation = await acceptAiResult(req.params.id, req.user.id);
        return res.status(200).json({ message: "AI result accepted. Consultation closed.", consultation });
    } catch (error) {
        return res.status(400).json({ message: error.message });
    }
};

// Worker escalates to doctor for second opinion
const escalate = async (req, res) => {
    try {
        const { doctorId, reason } = req.body;
        console.log(`[ESCALATE] Request for consultation ${req.params.id} to doctor ${doctorId} from worker ${req.user.id}`);
        if (!doctorId) return res.status(400).json({ message: "doctorId is required" });

        const consultation = await escalateToDoctor(req.params.id, doctorId, req.user.id, reason);
        console.log(`[ESCALATE] Success for consultation ${req.params.id}`);
        return res.status(200).json({ message: "Consultation escalated to doctor", consultation });
    } catch (error) {
        console.error(`[ESCALATE] Error: ${error.message}`);
        return res.status(400).json({ message: error.message });
    }
};

// Doctor views all pending consultations assigned to them
const getPendingForDoctor = async (req, res) => {
    try {
        const consultations = await getPendingConsultationsForDoctor(req.user.id);
        return res.status(200).json({ consultations });
    } catch (error) {
        return res.status(500).json({ message: error.message });
    }
};

// Doctor views ALL consultations assigned to them (pending + reviewed)
const getAllForDoctor = async (req, res) => {
    try {
        const consultations = await getAllConsultationsForDoctor(req.user.id);
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
            req.user.id,
            { diagnosis, recommendation }
        );

        return res.status(200).json({ message: "Second opinion submitted successfully", consultation });
    } catch (error) {
        return res.status(400).json({ message: error.message });
    }
};

// Store ML analysis
const storeMlAnalysisResult = async (req, res) => {
    try {
        const { mlResult } = req.body;
        if (!mlResult) {
            return res.status(400).json({ message: "ML result is required" });
        }

        const consultation = await storeMlAnalysis(req.params.id, mlResult);
        return res.status(200).json({ message: "ML analysis stored", consultation });
    } catch (error) {
        return res.status(400).json({ message: error.message });
    }
};

// Store LLM analysis
const storeLlmAnalysisResult = async (req, res) => {
    try {
        const { llmResult } = req.body;
        if (!llmResult) {
            return res.status(400).json({ message: "LLM result is required" });
        }

        const consultation = await storeLlmAnalysis(req.params.id, llmResult);
        return res.status(200).json({ message: "LLM analysis stored", consultation });
    } catch (error) {
        return res.status(400).json({ message: error.message });
    }
};

// Store final verdict
const storeFinalVerdictResult = async (req, res) => {
    try {
        const { verdict } = req.body;
        if (!verdict) {
            return res.status(400).json({ message: "Verdict is required" });
        }

        const consultation = await storeFinalVerdict(req.params.id, verdict);
        return res.status(200).json({ message: "Final verdict stored", consultation });
    } catch (error) {
        return res.status(400).json({ message: error.message });
    }
};

// Store AI analysis PDF report — receives base64 PDF, uploads to Cloudinary
const storeAnalysisReportResult = async (req, res) => {
    try {
        const { pdfBase64 } = req.body;
        if (!pdfBase64) {
            return res.status(400).json({ message: "pdfBase64 is required" });
        }

        const pdfBuffer = Buffer.from(pdfBase64, "base64");
        const consultation = await storeAnalysisReport(req.params.id, pdfBuffer);
        return res.status(200).json({
            message: "Analysis report stored",
            reportUrl: consultation.analysisReport,
            consultation,
        });
    } catch (error) {
        return res.status(400).json({ message: error.message });
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
    storeMlAnalysisResult,
    storeLlmAnalysisResult,
    storeFinalVerdictResult,
    storeAnalysisReportResult,
    getAdminConsultations,
};
