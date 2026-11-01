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
      redFlag: { type: Boolean, default: false },
      redFlagDetails: mongoose.Schema.Types.Mixed,
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
      enum: ["pending", "analyzed", "escalated", "reviewed", "closed"],
      default: "pending",
    },
    workerDecision: {
      type: String,
      enum: ["accepted", "escalated", "referred_to_hospital"],
    },
    decisionOutcome: {
      type: String,
      enum: ["accepted", "escalated", "referred_to_hospital"],
    },
    decisionNote: {
      type: String,
    },
    overrideReason: {
      type: String,
      enum: [
        "patient_improved",
        "referred_in_person",
        "doctor_unreachable",
        "patient_declined_referral",
        "other",
      ],
    },
    overrideDetails: {
      reason: String,
      note: String,
      byUser: { type: mongoose.Schema.Types.ObjectId, ref: "Worker" },
      at: Date,
    },
    escalationReason: {
      type: String,
    },
    escalatedAt: {
      type: Date,
    },
    secondOpinion: {
      diagnosis: {
        type: String,
      },
      recommendation: {
        type: String,
      },
      prescription: {
        type: String,
      },
      respondedAt: {
        type: Date,
      },
      respondedBy: {
        type: mongoose.Schema.Types.ObjectId,
        ref: "Doctor",
      },
    },
    aiDoctorAgreement: {
      agreement: { type: Boolean, default: null },
      normalizedAiDiagnosis: String,
      normalizedDoctorDiagnosis: String,
      computedAt: Date,
    },
    notifications: [
      {
        recipientRole: { type: String, enum: ["worker", "doctor", "admin"] },
        recipientId: mongoose.Schema.Types.ObjectId,
        type: { type: String, enum: ["ESCALATED_CASE", "REVIEWED_CASE", "RED_FLAG_ALERT"] },
        message: String,
        read: { type: Boolean, default: false },
        createdAt: { type: Date, default: Date.now },
      },
    ],
  },
  { timestamps: true, optimisticConcurrency: true }
);

export default mongoose.model("Consultation", consultationSchema);
