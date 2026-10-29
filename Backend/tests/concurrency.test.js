/**
 * ArogyaMitra — Phase 4 Concurrency, Job Queue & Load Resilience Tests
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import mongoose from "mongoose";
import {
  enqueueAnalysisJob,
  getJobStatus,
  getQueueMetrics,
  claimNextJob,
  releaseOrRetryJob,
  completeJob,
} from "../src/service/jobQueue.service.js";
import AnalysisJob from "../src/models/job/jobSchema.js";
import Consultation from "../src/models/consultation/consultationSchema.js";
import serverConfig from "../src/config/serverConfig.js";

describe("Phase 4 — Concurrency & Asynchronous Job Pipeline", () => {
  const org1 = new mongoose.Types.ObjectId();
  const org2 = new mongoose.Types.ObjectId();
  const workerUser = { id: new mongoose.Types.ObjectId().toString(), role: "worker", name: "Rani Worker" };

  beforeEach(() => {
    vi.restoreAllMocks();
  });

  describe("1. Asynchronous Job Queue Lifecycle", () => {
    it("should enqueue a background analysis job and return HTTP 202 payload with unique jobId", () => {
      const consultationId = new mongoose.Types.ObjectId();
      const job = enqueueAnalysisJob({
        consultationId,
        organization: org1,
        requestingUser: workerUser,
        options: { language: "en" },
      });

      expect(job).toHaveProperty("jobId");
      expect(job.status).toBe("queued");
      expect(job.message).toContain("accepted for asynchronous processing");
    });

    it("should retrieve status of queued or processing job", () => {
      const consultationId = new mongoose.Types.ObjectId();
      const job = enqueueAnalysisJob({
        consultationId,
        organization: org1,
        requestingUser: workerUser,
      });

      const status = getJobStatus(job.jobId, org1);
      expect(status).not.toBeNull();
      expect(status.jobId).toBe(job.jobId);
      expect(status.consultationId).toBe(consultationId.toString());
      expect(["queued", "processing", "completed", "failed"]).toContain(status.status);
    });

    it("should prevent cross-tenant job status enumeration (returns null for different organization)", () => {
      const consultationId = new mongoose.Types.ObjectId();
      const job = enqueueAnalysisJob({
        consultationId,
        organization: org1,
        requestingUser: workerUser,
      });

      // Tenant 2 attempts to query Tenant 1's job
      const leakAttempt = getJobStatus(job.jobId, org2);
      expect(leakAttempt).toBeNull();
    });

    it("should expose accurate queue diagnostics and metrics", () => {
      const metrics = getQueueMetrics();
      expect(metrics).toHaveProperty("totalTrackedJobs");
      expect(metrics).toHaveProperty("waitingInQueue");
      expect(metrics).toHaveProperty("activeWorkers");
      expect(metrics).toHaveProperty("maxConcurrency");
      expect(metrics.maxConcurrency).toBe(5);
    });
  });

  describe("2. Optimistic Concurrency Control (Lost-Update Prevention)", () => {
    it("should have optimisticConcurrency enabled on Consultation schema", () => {
      expect(Consultation.schema.options.optimisticConcurrency).toBe(true);
    });

  });

  describe("3. High-Concurrency Job Throughput Simulation", () => {
    it("should handle 50 concurrent job enqueues without throwing or dropping requests", async () => {
      const totalJobs = 50;
      const jobIds = [];

      for (let i = 0; i < totalJobs; i++) {
        const cId = new mongoose.Types.ObjectId();
        const res = enqueueAnalysisJob({
          consultationId: cId,
          organization: org1,
          requestingUser: workerUser,
        });
        jobIds.push(res.jobId);
      }

      expect(jobIds.length).toBe(totalJobs);

      // Verify all jobs can be polled
      for (const id of jobIds) {
        const poll = getJobStatus(id, org1);
        expect(poll).not.toBeNull();
      }
    });
  });

  describe("4. Atomic findOneAndUpdate Job Claims, Lease Expiry & Dead-Letter Queue", () => {
    it("should simulate 50 parallel concurrent worker claim requests with mutually exclusive atomic locking", async () => {
      // Create a pool of 10 available queued jobs
      const mockDbQueue = [];
      for (let i = 0; i < 10; i++) {
        mockDbQueue.push({
          jobId: `job-uuid-${i}`,
          status: "queued",
          attempts: 0,
          maxAttempts: 3,
          lockedAt: null,
          lockedBy: null,
          leaseExpiresAt: null,
          nextRetryAt: null,
          createdAt: new Date(Date.now() + i * 1000),
        });
      }

      // Simulate atomic findOneAndUpdate with lock-free atomic semantics
      let lockCounter = 0;
      vi.spyOn(AnalysisJob, "findOneAndUpdate").mockImplementation(async (filter, update, options) => {
        // Atomic compare-and-swap on simulated in-memory store
        const now = new Date();
        const candidate = mockDbQueue.find((j) => {
          if (j.status === "queued" && j.attempts < 3) return true;
          if (j.status === "processing" && j.leaseExpiresAt && j.leaseExpiresAt < now && j.attempts < 3) return true;
          return false;
        });

        if (!candidate) return null;

        // Mutate document atomically
        candidate.status = update.$set.status;
        candidate.lockedAt = update.$set.lockedAt;
        candidate.lockedBy = update.$set.lockedBy;
        candidate.leaseExpiresAt = update.$set.leaseExpiresAt;
        candidate.startedAt = update.$set.startedAt;
        candidate.attempts = (candidate.attempts || 0) + (update.$inc?.attempts || 1);

        return { ...candidate };
      });

      // 50 parallel workers simultaneously execute claimNextJob
      const workerPromises = [];
      for (let w = 0; w < 50; w++) {
        workerPromises.push(claimNextJob(`worker-${w}`, 300000));
      }

      const results = await Promise.all(workerPromises);

      // Verify outcomes:
      // Exactly 10 workers must succeed in claiming a job
      const claimedJobs = results.filter((j) => j !== null);
      expect(claimedJobs.length).toBe(10);

      // Exactly 40 workers receive null (no jobs left, graceful backoff)
      const emptyClaims = results.filter((j) => j === null);
      expect(emptyClaims.length).toBe(40);

      // 0 duplicate claims: every claimed jobId must be distinct
      const claimedIds = claimedJobs.map((j) => j.jobId);
      const uniqueIds = new Set(claimedIds);
      expect(uniqueIds.size).toBe(10);

      // 0 lost updates: all 10 jobs in mockDbQueue are in 'processing' status
      expect(mockDbQueue.every((j) => j.status === "processing")).toBe(true);
      expect(mockDbQueue.every((j) => j.attempts === 1)).toBe(true);
    });

    it("should recover abandoned jobs after worker lease expires", async () => {
      const abandonedJob = {
        jobId: "abandoned-job-1",
        status: "processing",
        lockedAt: new Date(Date.now() - 600000), // 10 minutes ago
        leaseExpiresAt: new Date(Date.now() - 300000), // expired 5 minutes ago
        attempts: 1,
        maxAttempts: 3,
        save: vi.fn().mockResolvedValue(true),
      };

      vi.spyOn(AnalysisJob, "findOneAndUpdate").mockImplementation(async (filter, update) => {
        abandonedJob.status = update.$set.status;
        abandonedJob.lockedBy = update.$set.lockedBy;
        abandonedJob.leaseExpiresAt = update.$set.leaseExpiresAt;
        abandonedJob.attempts += 1;
        return abandonedJob;
      });

      const recovered = await claimNextJob("worker-recovery-node", 300000);
      expect(recovered).not.toBeNull();
      expect(recovered.status).toBe("processing");
      expect(recovered.lockedBy).toBe("worker-recovery-node");
      expect(recovered.attempts).toBe(2);
    });

    it("should retry transient failures with exponential backoff and transition to dead_letter after 3 attempts", async () => {
      const mockJobDoc = {
        jobId: "retry-job-99",
        status: "processing",
        attempts: 1,
        maxAttempts: 3,
        error: null,
        nextRetryAt: null,
        save: vi.fn().mockResolvedValue(true),
      };

      vi.spyOn(AnalysisJob, "findOne").mockResolvedValue(mockJobDoc);

      // Attempt 1 failure -> retry with backoff
      const retry1 = await releaseOrRetryJob("retry-job-99", { message: "AI pipeline network timeout" });
      expect(retry1.status).toBe("queued");
      expect(retry1.nextRetryAt).toBeInstanceOf(Date);
      expect(retry1.error.code).toBe("RETRYABLE_ERROR");

      // Simulate attempt 3 reaching maxAttempts
      mockJobDoc.attempts = 3;
      const deadLetterJob = await releaseOrRetryJob("retry-job-99", { message: "Persistent model inference failure" });
      expect(deadLetterJob.status).toBe("dead_letter");
      expect(deadLetterJob.deadLetterReason).toContain("Persistent model inference failure");
      expect(deadLetterJob.error.code).toBe("DEAD_LETTER_EXHAUSTED");
      expect(deadLetterJob.failedAt).toBeInstanceOf(Date);
    });
  });
});
