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
      severityScore: Number,
      topPredictions: Array,
      matchedSymptoms: [String],
      precautions: [String],
      description: String,
      shapExplanation: Array,
      needsEscalation: Boolean,
      uncertaintyReason: String,
      analyzedAt: Date,
    },
    llmAnalysis: {
      summary: String,
      confidenceInterpretation: String,
      severityAssessment: String,
      keyFactors: String,
      recommendations: mongoose.Schema.Types.Mixed,
      referral: String,
      riskLevel: { type: String, enum: ["low", "moderate", "high"] },
      llmFallback: { type: Boolean, default: false },
      analyzedAt: Date,
    },
    finalVerdict: {
      conclusion: String,
      generatedAt: Date,
    },
    status: {
      type: String,
      enum: ["pending", "analyzed", "reviewed", "closed"],
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
