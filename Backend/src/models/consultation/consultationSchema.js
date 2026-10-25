import mongoose from "mongoose";

const consultationSchema = new mongoose.Schema({
    patient: {
        type: mongoose.Schema.Types.ObjectId,
        ref: "Patient",
        required: true,
    },
    submittedBy: {
        type: mongoose.Schema.Types.ObjectId,
        ref: "Worker",
        required: true,
    },
    assignedDoctor: {
        type: mongoose.Schema.Types.ObjectId,
        ref: "Doctor",
    },
    symptoms: {
        type: [String],
        required: true,
    }, // e.g. ["fever", "cough", "chest pain"]
    notes: {
        type: String,
    }, // additional observations by the worker
    attachments: {
        type: [String],
    }, // Cloudinary URLs for patient reports/images
    aiReport: {
        type: String,
    }, // optional: Cloudinary URL of the AI-generated report uploaded by worker
    analysisReport: {
        type: String,
    }, // URL/path to the full AI-generated PDF report (ML + LLM + verdict)
    mlAnalysis: {
        disease: String,
        confidence: Number,
        precautions: [String],
        analyzedAt: Date,
    },
    llmAnalysis: {
        summary: String,
        recommendations: [String],
        riskLevel: { type: String, enum: ['low', 'moderate', 'high'] },
        analyzedAt: Date,
    },
    finalVerdict: {
        conclusion: String,
        generatedAt: Date,
    },
    status: {
        type: String,
        enum: ["pending", "reviewed", "closed"],
        default: "pending",
    },
    workerDecision: {
        type: String,
        enum: ["accepted", "escalated"],
    }, // accepted = satisfied with AI, escalated = wants doctor's second opinion
    escalationReason: {
        type: String,
    }, // reason for escalation provided by worker
    secondOpinion: {
        diagnosis: {
            type: String,
        },
        recommendation: {
            type: String,
        },
        respondedAt: {
            type: Date,
        },
    }, // filled by the doctor
}, { timestamps: true });

export default mongoose.model("Consultation", consultationSchema);
