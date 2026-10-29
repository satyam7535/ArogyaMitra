import mongoose from "mongoose";

const analysisJobSchema = new mongoose.Schema(
  {
    jobId: {
      type: String,
      required: true,
      unique: true,
      index: true,
    },
    consultationId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: "Consultation",
      required: true,
      index: true,
    },
    organization: {
      type: mongoose.Schema.Types.ObjectId,
      ref: "Organization",
      required: true,
      index: true,
    },
    requestingUserId: {
      type: mongoose.Schema.Types.ObjectId,
      required: true,
    },
    status: {
      type: String,
      enum: ["queued", "processing", "completed", "failed", "dead_letter"],
      default: "queued",
      index: true,
    },
    options: {
      language: { type: String, enum: ["en", "hi", "mr"], default: "en" },
    },
    result: {
      type: mongoose.Schema.Types.Mixed,
      default: null,
    },
    error: {
      message: { type: String, default: null },
      code: { type: String, default: null },
    },
    lockedAt: {
      type: Date,
      default: null,
      index: true,
    },
    lockedBy: {
      type: String,
      default: null,
    },
    leaseExpiresAt: {
      type: Date,
      default: null,
      index: true,
    },
    attempts: {
      type: Number,
      default: 0,
    },
    maxAttempts: {
      type: Number,
      default: 3,
    },
    nextRetryAt: {
      type: Date,
      default: null,
      index: true,
    },
    deadLetterReason: {
      type: String,
      default: null,
    },
    startedAt: {
      type: Date,
      default: null,
    },
    completedAt: {
      type: Date,
      default: null,
    },
    failedAt: {
      type: Date,
      default: null,
    },
  },
  {
    timestamps: true,
  }
);

// Compound index for tenant-scoped job lookup
analysisJobSchema.index({ jobId: 1, organization: 1 });
// Compound index for atomic queue polling & lease recovery
analysisJobSchema.index({ status: 1, leaseExpiresAt: 1, attempts: 1 });

const AnalysisJob = mongoose.model("AnalysisJob", analysisJobSchema);
export default AnalysisJob;
