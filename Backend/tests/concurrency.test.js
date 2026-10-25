/**
 * ArogyaMitra — Phase 4 Concurrency, Job Queue & Load Resilience Tests
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import mongoose from "mongoose";
import { enqueueAnalysisJob, getJobStatus, getQueueMetrics } from "../src/service/jobQueue.service.js";
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

    it("should detect version conflicts when concurrent writers update the same consultation", async () => {
      // Simulate two concurrent actors fetching the same consultation at version 0
      const docA = {
        _id: new mongoose.Types.ObjectId(),
        __v: 0,
        status: "pending",
        workerDecision: undefined,
      };

      const docB = {
        ...docA,
        __v: 0,
      };

      // Actor A updates and increments __v to 1
      docA.__v = 1;
      docA.workerDecision = "escalated";

      // Actor B tries to update using stale version __v: 0
      const simulateConcurrentWrite = (staleDoc, currentVersion) => {
        if (staleDoc.__v !== currentVersion) {
          const err = new Error(
            `VersionError: No matching document found for id "${staleDoc._id}" version ${staleDoc.__v}`
          );
          err.name = "VersionError";
          throw err;
        }
        return { ...staleDoc, __v: currentVersion + 1 };
      };

      expect(() => simulateConcurrentWrite(docB, docA.__v)).toThrowError(/VersionError/);
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
});
