/**
 * ArogyaMitra — Consultation My Endpoint Pagination & Worker Isolation Tests
 *
 * Verifies:
 * 1. Pagination parameters (page, limit, total, totalPages).
 * 2. Sanitization of invalid/malformed pagination values (negative, non-numeric, oversized limit).
 * 3. Scoping isolation: Worker only receives consultations submitted by themselves (other worker's data excluded).
 * 4. Role-based access control: Worker role required (401 unauth, 403 doctor/admin).
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import request from "supertest";
import mongoose from "mongoose";
import jwt from "jsonwebtoken";
import app from "../src/index.js";
import ROLES from "../src/config/roles.js";
import serverConfig from "../src/config/serverConfig.js";
import Consultation from "../src/models/consultation/consultationSchema.js";
import { getConsultationsByWorker } from "../src/service/consultation.service.js";

const orgId = new mongoose.Types.ObjectId();
const worker1Id = new mongoose.Types.ObjectId();
const worker2Id = new mongoose.Types.ObjectId();
const doctorId = new mongoose.Types.ObjectId();

const worker1Token = jwt.sign(
  { id: worker1Id.toString(), role: ROLES.WORKER, organization: orgId.toString() },
  serverConfig.JWT_SECRET
);

const doctorToken = jwt.sign(
  { id: doctorId.toString(), role: ROLES.DOCTOR, organization: orgId.toString() },
  serverConfig.JWT_SECRET
);

describe("WP5 — Consultation Pagination & Worker Scoping Tests", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  describe("Service Layer: getConsultationsByWorker", () => {
    it("should correctly apply page, limit, skip and return total and totalPages", async () => {
      const mockChain = {
        select: vi.fn().mockReturnThis(),
        populate: vi.fn().mockReturnThis(),
        sort: vi.fn().mockReturnThis(),
        skip: vi.fn().mockReturnThis(),
        limit: vi.fn().mockResolvedValue([
          { _id: new mongoose.Types.ObjectId(), symptoms: ["fever"], submittedBy: worker1Id },
          { _id: new mongoose.Types.ObjectId(), symptoms: ["cough"], submittedBy: worker1Id },
        ]),
      };

      const findSpy = vi.spyOn(Consultation, "find").mockReturnValue(mockChain);
      const countSpy = vi.spyOn(Consultation, "countDocuments").mockResolvedValue(25);

      const result = await getConsultationsByWorker(worker1Id, orgId, { page: 2, limit: 10 });

      expect(findSpy).toHaveBeenCalledWith({ organization: orgId, submittedBy: worker1Id });
      expect(countSpy).toHaveBeenCalledWith({ organization: orgId, submittedBy: worker1Id });
      expect(mockChain.skip).toHaveBeenCalledWith(10);
      expect(mockChain.limit).toHaveBeenCalledWith(10);

      expect(result.page).toBe(2);
      expect(result.limit).toBe(10);
      expect(result.total).toBe(25);
      expect(result.totalPages).toBe(3);
      expect(result.consultations).toHaveLength(2);
    });

    it("should sanitize invalid and out-of-bounds pagination parameters", async () => {
      const mockChain = {
        select: vi.fn().mockReturnThis(),
        populate: vi.fn().mockReturnThis(),
        sort: vi.fn().mockReturnThis(),
        skip: vi.fn().mockReturnThis(),
        limit: vi.fn().mockResolvedValue([]),
      };

      vi.spyOn(Consultation, "find").mockReturnValue(mockChain);
      vi.spyOn(Consultation, "countDocuments").mockResolvedValue(0);

      // Negative page and non-numeric limit -> clamps to page 1, limit 20
      const res1 = await getConsultationsByWorker(worker1Id, orgId, { page: -5, limit: "invalid" });
      expect(mockChain.skip).toHaveBeenCalledWith(0);
      expect(mockChain.limit).toHaveBeenCalledWith(20);
      expect(res1.page).toBe(1);
      expect(res1.limit).toBe(20);

      // Oversized limit (e.g. 500) -> clamps to max limit 100
      const res2 = await getConsultationsByWorker(worker1Id, orgId, { page: 1, limit: 500 });
      expect(mockChain.limit).toHaveBeenCalledWith(100);
      expect(res2.limit).toBe(100);
    });

    it("should strictly scope query so other worker's data is never returned", async () => {
      let capturedQuery = null;
      const mockChain = {
        select: vi.fn().mockReturnThis(),
        populate: vi.fn().mockReturnThis(),
        sort: vi.fn().mockReturnThis(),
        skip: vi.fn().mockReturnThis(),
        limit: vi.fn().mockImplementation(() => {
          // If query submittedBy is worker1Id, worker2's data will never be matched
          if (capturedQuery.submittedBy.toString() === worker2Id.toString()) {
            return Promise.resolve([{ _id: new mongoose.Types.ObjectId(), submittedBy: worker2Id }]);
          }
          return Promise.resolve([{ _id: new mongoose.Types.ObjectId(), submittedBy: worker1Id }]);
        }),
      };

      vi.spyOn(Consultation, "find").mockImplementation((query) => {
        capturedQuery = query;
        return mockChain;
      });
      vi.spyOn(Consultation, "countDocuments").mockResolvedValue(1);

      // Query as worker1
      const resWorker1 = await getConsultationsByWorker(worker1Id, orgId, {});
      expect(capturedQuery.submittedBy).toEqual(worker1Id);
      expect(resWorker1.consultations[0].submittedBy).toEqual(worker1Id);
      expect(capturedQuery.submittedBy).not.toEqual(worker2Id);
    });
  });

  describe("HTTP API Layer: GET /api/v1/consultation/my", () => {
    it("should return HTTP 200 with paginated structure when requested by authorized worker", async () => {
      const mockChain = {
        select: vi.fn().mockReturnThis(),
        populate: vi.fn().mockReturnThis(),
        sort: vi.fn().mockReturnThis(),
        skip: vi.fn().mockReturnThis(),
        limit: vi.fn().mockResolvedValue([
          { _id: new mongoose.Types.ObjectId(), symptoms: ["chills"], submittedBy: worker1Id },
        ]),
      };

      vi.spyOn(Consultation, "find").mockReturnValue(mockChain);
      vi.spyOn(Consultation, "countDocuments").mockResolvedValue(1);

      const res = await request(app)
        .get("/api/v1/consultation/my?page=1&limit=5")
        .set("Authorization", `Bearer ${worker1Token}`);

      expect(res.status).toBe(200);
      expect(res.body).toHaveProperty("consultations");
      expect(res.body).toHaveProperty("page", 1);
      expect(res.body).toHaveProperty("limit", 5);
      expect(res.body).toHaveProperty("total", 1);
      expect(res.body).toHaveProperty("totalPages", 1);
      expect(Array.isArray(res.body.consultations)).toBe(true);
    });

    it("should return HTTP 401 when no token is provided", async () => {
      const res = await request(app).get("/api/v1/consultation/my");
      expect(res.status).toBe(401);
    });

    it("should return HTTP 403 when requested by unauthorized role (Doctor)", async () => {
      const res = await request(app)
        .get("/api/v1/consultation/my")
        .set("Authorization", `Bearer ${doctorToken}`);
      expect(res.status).toBe(403);
    });
  });
});
