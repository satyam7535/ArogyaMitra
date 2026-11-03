/**
 * ArogyaMitra — Asynchronous AI Analysis Job Queue Service
 * Handles concurrent background orchestration of ML inference, Safe LLM, and PDF generation
 * with atomic findOneAndUpdate job claims, lease timeouts, exponential backoff retries,
 * dead-letter queue, status polling, and durable MongoDB persistence.
 */

import { randomUUID } from "crypto";
import mongoose from "mongoose";
import { triggerConsultationAnalysis } from "./consultation.service.js";
import AnalysisJob from "../models/job/jobSchema.js";

// In-memory cache with 1-hour automatic pruning for fast lookups
const jobs = new Map();
const idempotencyIndex = new Map();
const JOB_EXPIRY_MS = 60 * 60 * 1000; // 1 hour
const MAX_CONCURRENT_JOBS = 5;
const DEFAULT_LEASE_DURATION_MS = 5 * 60 * 1000; // 5-minute lease timeout

let activeWorkerCount = 0;
const waitingQueue = [];

/**
 * Clean up old completed/failed jobs periodically from in-memory cache
 */
setInterval(() => {
  const now = Date.now();
  for (const [id, job] of jobs.entries()) {
    if (now - job.createdAt > JOB_EXPIRY_MS) {
      jobs.delete(id);
    }
  }
}, 5 * 60 * 1000).unref();

/**
 * Atomic Job Claim via findOneAndUpdate
 * Mutually exclusive claim: matches queued jobs or abandoned processing jobs whose lease expired.
 * Increments attempts and assigns lock lease to the worker.
 */
const claimNextJob = async (workerId = randomUUID(), leaseDurationMs = DEFAULT_LEASE_DURATION_MS) => {
  const now = new Date();
  const leaseExpiresAt = new Date(now.getTime() + leaseDurationMs);

  const claimed = await AnalysisJob.findOneAndUpdate(
    {
      $or: [
        {
          status: "queued",
          attempts: { $lt: 3 },
          $or: [{ nextRetryAt: null }, { nextRetryAt: { $lte: now } }],
        },
        {
          status: "processing",
          leaseExpiresAt: { $lt: now },
          attempts: { $lt: 3 },
        },
      ],
    },
    {
      $set: {
        status: "processing",
        lockedAt: now,
        lockedBy: workerId,
        leaseExpiresAt,
        startedAt: now,
      },
      $inc: { attempts: 1 },
    },
    { new: true, sort: { createdAt: 1 } }
  );

  return claimed;
};

/**
 * Handle job failure with exponential backoff retry or transition to dead-letter
 */
const releaseOrRetryJob = async (jobId, error = {}) => {
  const job = await AnalysisJob.findOne({ jobId });
  if (!job) return null;

  if (job.attempts >= job.maxAttempts) {
    job.status = "dead_letter";
    job.deadLetterReason = error?.message || "Exceeded maximum retry attempts (3/3)";
    job.failedAt = new Date();
    job.lockedAt = null;
    job.lockedBy = null;
    job.leaseExpiresAt = null;
    job.error = {
      message: error?.message || "Job moved to dead-letter queue",
      code: error?.code || "DEAD_LETTER_EXHAUSTED",
    };
  } else {
    job.status = "queued";
    const backoffMs = Math.pow(2, job.attempts) * 1000; // 2s, 4s, 8s
    job.nextRetryAt = new Date(Date.now() + backoffMs);
    job.lockedAt = null;
    job.lockedBy = null;
    job.leaseExpiresAt = null;
    job.error = {
      message: error?.message || "Transient processing failure, scheduled for retry",
      code: error?.code || "RETRYABLE_ERROR",
    };
  }

  await job.save();
  return job;
};

/**
 * Complete a successfully processed job
 */
const completeJob = async (jobId, result = {}) => {
  return await AnalysisJob.findOneAndUpdate(
    { jobId },
    {
      $set: {
        status: "completed",
        completedAt: new Date(),
        result,
        lockedAt: null,
        lockedBy: null,
        leaseExpiresAt: null,
      },
    },
    { new: true }
  );
};

/**
 * Worker pump: executes waiting jobs up to MAX_CONCURRENT_JOBS
 */
const pumpQueue = async () => {
  if (activeWorkerCount >= MAX_CONCURRENT_JOBS || waitingQueue.length === 0) {
    return;
  }

  const { jobId, consultationId, organization, requestingUser, options } = waitingQueue.shift();
  const job = jobs.get(jobId);
  if (!job) return;

  activeWorkerCount++;
  job.status = "processing";
  job.startedAt = Date.now();
  job.attempts = (job.attempts || 0) + 1;

  // Update MongoDB document if connected
  if (mongoose.connection?.readyState === 1) {
    try {
      await AnalysisJob.updateOne(
        { jobId },
        {
          $set: {
            status: "processing",
            startedAt: new Date(job.startedAt),
            lockedAt: new Date(job.startedAt),
            lockedBy: "in-memory-worker",
            leaseExpiresAt: new Date(job.startedAt + DEFAULT_LEASE_DURATION_MS),
          },
          $inc: { attempts: 1 },
        }
      );
    } catch (dbErr) {
      console.error("[Queue] Failed to update job to processing in MongoDB:", jobId, dbErr.message);
    }
  }

  try {
    const consultation = await triggerConsultationAnalysis(
      consultationId,
      organization,
      requestingUser,
      options
    );

    job.status = "completed";
    job.completedAt = Date.now();
    job.result = {
      consultationId: consultation._id,
      status: consultation.status,
      disease: consultation.mlAnalysis?.disease,
      confidence: consultation.mlAnalysis?.confidence,
      llmFallback: consultation.llmAnalysis?.llmFallback,
    };

    if (mongoose.connection?.readyState === 1) {
      await completeJob(jobId, job.result);
    }
  } catch (error) {
    job.status = (job.attempts >= 3) ? "dead_letter" : "failed";
    job.failedAt = Date.now();
    job.error = {
      message: error.message,
      code: error.code || "JOB_EXECUTION_FAILED",
    };

    if (mongoose.connection?.readyState === 1) {
      try {
        await releaseOrRetryJob(jobId, error);
      } catch (dbErr) {
        console.error(`[Queue] Failed to record job failure in MongoDB:`, dbErr.message);
      }
    }
  } finally {
    activeWorkerCount--;
    setImmediate(pumpQueue);
  }
};

/**
 * Enqueue an asynchronous consultation analysis job
 * Persists to MongoDB when database is active, and pushes to processing pump
 */
const enqueueAnalysisJob = ({ consultationId, organization, requestingUser, options = {}, idempotencyKey }) => {
  const orgStr = organization.toString();
  if (idempotencyKey) {
    const dedupeKey = `${orgStr}:${idempotencyKey}`;
    if (idempotencyIndex.has(dedupeKey)) {
      const existingJobId = idempotencyIndex.get(dedupeKey);
      const existing = jobs.get(existingJobId);
      return {
        jobId: existingJobId,
        status: existing ? existing.status : "queued",
        createdAt: existing ? new Date(existing.createdAt).toISOString() : new Date().toISOString(),
        isDuplicate: true,
        message: "Analysis job already enqueued with this idempotency key",
      };
    }
  }

  const jobId = randomUUID();
  if (idempotencyKey) {
    idempotencyIndex.set(`${orgStr}:${idempotencyKey}`, jobId);
  }

  const jobRecord = {
    jobId,
    consultationId: consultationId.toString(),
    organization: organization.toString(),
    status: "queued",
    attempts: 0,
    maxAttempts: 3,
    createdAt: Date.now(),
    startedAt: null,
    completedAt: null,
    failedAt: null,
    result: null,
    error: null,
  };

  jobs.set(jobId, jobRecord);

  // Durable MongoDB persistence
  if (mongoose.connection?.readyState === 1) {
    AnalysisJob.create({
      jobId,
      consultationId,
      organization,
      requestingUserId: requestingUser._id || requestingUser.id,
      idempotencyKey: idempotencyKey || null,
      status: "queued",
      attempts: 0,
      maxAttempts: 3,
      options: { language: options.language || "en" },
    }).catch((dbErr) => {
      console.error("[Queue] Failed to persist job to MongoDB:", jobId, dbErr.message);
    });
  }

  waitingQueue.push({
    jobId,
    consultationId,
    organization,
    requestingUser,
    options,
  });

  setImmediate(pumpQueue);

  return {
    jobId,
    status: "queued",
    createdAt: new Date(jobRecord.createdAt).toISOString(),
    message: "Analysis job accepted for asynchronous processing",
  };
};

/**
 * Get job status by ID (strictly tenant-scoped)
 * Checks in-memory cache first, falls back to MongoDB for durable query
 */
const getJobStatus = (jobId, organization) => {
  const job = jobs.get(jobId);
  if (job) {
    // Multi-tenant check: never leak jobs across organizations
    if (job.organization !== organization.toString()) {
      return null;
    }

    return {
      jobId: job.jobId,
      consultationId: job.consultationId,
      status: job.status,
      createdAt: new Date(job.createdAt).toISOString(),
      startedAt: job.startedAt ? new Date(job.startedAt).toISOString() : null,
      completedAt: job.completedAt ? new Date(job.completedAt).toISOString() : null,
      result: job.result,
      error: job.error,
    };
  }

  return null;
};

/**
 * Get durable job status from MongoDB (for cross-restart or historical lookups)
 */
const getJobStatusFromDb = async (jobId, organization) => {
  // First check in-memory cache
  const cached = getJobStatus(jobId, organization);
  if (cached) return cached;

  if (mongoose.connection?.readyState === 1) {
    const doc = await AnalysisJob.findOne({ jobId, organization });
    if (!doc) return null;
    return {
      jobId: doc.jobId,
      consultationId: doc.consultationId.toString(),
      status: doc.status,
      createdAt: doc.createdAt ? doc.createdAt.toISOString() : null,
      startedAt: doc.startedAt ? doc.startedAt.toISOString() : null,
      completedAt: doc.completedAt ? doc.completedAt.toISOString() : null,
      result: doc.result,
      error: doc.error,
    };
  }
  return null;
};

/**
 * Get queue metrics for diagnostics and load monitoring
 */
const getQueueMetrics = () => {
  return {
    totalTrackedJobs: jobs.size,
    waitingInQueue: waitingQueue.length,
    activeWorkers: activeWorkerCount,
    maxConcurrency: MAX_CONCURRENT_JOBS,
  };
};

export {
  enqueueAnalysisJob,
  getJobStatus,
  getJobStatusFromDb,
  getQueueMetrics,
  claimNextJob,
  releaseOrRetryJob,
  completeJob,
};
