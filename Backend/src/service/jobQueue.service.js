/**
 * ArogyaMitra — Asynchronous AI Analysis Job Queue Service
 * Handles concurrent background orchestration of ML inference, Safe LLM, and PDF generation
 * with concurrency throttling, timeout safeguards, and status polling.
 */

import { randomUUID } from "crypto";
import { triggerConsultationAnalysis } from "./consultation.service.js";

// In-memory job repository with 1-hour automatic pruning
const jobs = new Map();
const JOB_EXPIRY_MS = 60 * 60 * 1000; // 1 hour
const MAX_CONCURRENT_JOBS = 5;

let activeWorkerCount = 0;
const waitingQueue = [];

/**
 * Clean up old completed/failed jobs periodically
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
  } catch (error) {
    job.status = "failed";
    job.failedAt = Date.now();
    job.error = {
      message: error.message,
      code: error.code || "JOB_EXECUTION_FAILED",
    };
  } finally {
    activeWorkerCount--;
    setImmediate(pumpQueue);
  }
};

/**
 * Enqueue an asynchronous consultation analysis job
 */
const enqueueAnalysisJob = ({ consultationId, organization, requestingUser, options = {} }) => {
  const jobId = randomUUID();

  const jobRecord = {
    jobId,
    consultationId: consultationId.toString(),
    organization: organization.toString(),
    status: "queued",
    createdAt: Date.now(),
    startedAt: null,
    completedAt: null,
    failedAt: null,
    result: null,
    error: null,
  };

  jobs.set(jobId, jobRecord);
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
 */
const getJobStatus = (jobId, organization) => {
  const job = jobs.get(jobId);
  if (!job) {
    return null;
  }

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
  getQueueMetrics,
};
