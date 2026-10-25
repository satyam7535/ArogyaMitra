import mongoose from "mongoose";

const consultationSchema = new mongoose.Schema(
  {
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
    organization: {
      type: mongoose.Schema.Types.ObjectId,
      ref: "Organization",
      required: true,
      index: true,
    },
    symptoms: {
      type: [String],
      required: true,
    },
    notes: {
      type: String,
    },
    attachments: {
      type: [String],
    },
    aiReport: {
      type: String,
    },
    analysisReport: {
      type: String,
    },
    mlAnalysis: {
      disease: String,
      confidence: Number,
      precautions: [String],
      analyzedAt: Date,
    },
    llmAnalysis: {
      summary: String,
      recommendations: [String],
      riskLevel: { type: String, enum: ["low", "moderate", "high"] },
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
    },
    escalationReason: {
      type: String,
    },
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
    },
  },
  { timestamps: true, optimisticConcurrency: true }
);

export default mongoose.model("Consultation", consultationSchema);
