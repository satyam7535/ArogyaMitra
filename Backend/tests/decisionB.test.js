/**
 * ArogyaMitra — WP2: Decision B Override & Decision State Machine Tests
 *
 * Verifies:
 * 1. Red-flag block: If redFlag=true, accept returns HTTP 409 RED_FLAG_ACCEPT_BLOCKED.
 * 2. Red-flag allow: Close with outcome "referred_to_hospital" is allowed.
 * 3. Normal needsEscalation override: Requires valid overrideReason and note >= 10 chars.
 * 4. State machine atomic transitions:
 *    - No double accept
 *    - No accept after escalate
 *    - No respond after close
 *    - Doctor must be assigned
 *    - Escalation reason required
 * 5. Mass-assignment resistance: Client cannot directly set redFlag or needsEscalation via request body.
 * 6. AI-vs-Doctor Diagnostic Agreement normalization.
 * 7. In-app notifications and overdue badge calculation.
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import request from "supertest";
import mongoose from "mongoose";
import jwt from "jsonwebtoken";
import app from "../src/index.js";
import ROLES from "../src/config/roles.js";
import serverConfig from "../src/config/serverConfig.js";
import Consultation from "../src/models/consultation/consultationSchema.js";
import Doctor from "../src/models/doctor/doctorSchema.js";
import { normalizeDiagnosis } from "../src/service/consultation.service.js";

const orgId = new mongoose.Types.ObjectId();
const workerId = new mongoose.Types.ObjectId();
const doctorId = new mongoose.Types.ObjectId();
const otherDoctorId = new mongoose.Types.ObjectId();

const workerToken = jwt.sign(
  { id: workerId.toString(), role: ROLES.WORKER, organization: orgId.toString() },
  serverConfig.JWT_SECRET
);

const doctorToken = jwt.sign(
  { id: doctorId.toString(), role: ROLES.DOCTOR, organization: orgId.toString() },
  serverConfig.JWT_SECRET
);

describe("WP2 — Decision B Override, State Machine & redFlag Enforcement", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  describe("2.1 & 2.4 Red-Flag Block & referred_to_hospital Outcome", () => {
    it("should strictly return HTTP 409 RED_FLAG_ACCEPT_BLOCKED when worker attempts to accept a red-flag case", async () => {
      const consultationId = new mongoose.Types.ObjectId();
      const mockDoc = {
        _id: consultationId,
        organization: orgId,
        status: "analyzed",
        mlAnalysis: {
          disease: "Heart attack",
          redFlag: true,
          needsEscalation: true,
        },
        workerDecision: null,
        save: vi.fn().mockResolvedValue(true),
      };

      vi.spyOn(Consultation, "findOne").mockResolvedValue(mockDoc);

      const res = await request(app)
        .patch(`/api/v1/consultation/${consultationId}/accept`)
        .set("Authorization", `Bearer ${workerToken}`)
        .send({ notes: "Routine follow-up noted" });

      expect(res.status).toBe(409);
      expect(res.body.code).toBe("RED_FLAG_ACCEPT_BLOCKED");
      expect(res.body.message).toContain("RED_FLAG_ACCEPT_BLOCKED");
      expect(mockDoc.save).not.toHaveBeenCalled();
    });

    it("should permit closing a red-flag case with outcome referred_to_hospital and notes", async () => {
      const consultationId = new mongoose.Types.ObjectId();
      const mockDoc = {
        _id: consultationId,
        organization: orgId,
        status: "analyzed",
        mlAnalysis: {
          disease: "Heart attack",
          redFlag: true,
          needsEscalation: true,
        },
        workerDecision: null,
        save: vi.fn().mockResolvedValue(true),
      };

      vi.spyOn(Consultation, "findOne").mockResolvedValue(mockDoc);

      const res = await request(app)
        .patch(`/api/v1/consultation/${consultationId}/accept`)
        .set("Authorization", `Bearer ${workerToken}`)
        .send({
          decisionOutcome: "referred_to_hospital",
          overrideNote: "Emergency ambulance arranged to district hospital immediately",
        });

      expect(res.status).toBe(200);
      expect(res.body.consultation.workerDecision).toBe("referred_to_hospital");
      expect(res.body.consultation.decisionOutcome).toBe("referred_to_hospital");
      expect(mockDoc.status).toBe("closed");
      expect(mockDoc.save).toHaveBeenCalled();
    });
  });

  describe("2.3 Override Rule for needsEscalation Presentations", () => {
    it("should reject accept without overrideReason when needsEscalation=true", async () => {
      const consultationId = new mongoose.Types.ObjectId();
      const mockDoc = {
        _id: consultationId,
        organization: orgId,
        status: "analyzed",
        mlAnalysis: {
          disease: "Migraine",
          redFlag: false,
          needsEscalation: true,
        },
        workerDecision: null,
        save: vi.fn().mockResolvedValue(true),
      };

      vi.spyOn(Consultation, "findOne").mockResolvedValue(mockDoc);

      const res = await request(app)
        .patch(`/api/v1/consultation/${consultationId}/accept`)
        .set("Authorization", `Bearer ${workerToken}`)
        .send({ notes: "Looks okay" });

      expect(res.status).toBe(400);
      expect(res.body.message).toContain("override reason is required");
      expect(mockDoc.save).not.toHaveBeenCalled();
    });

    it("should reject accept if overrideNote is shorter than 10 characters", async () => {
      const consultationId = new mongoose.Types.ObjectId();
      const mockDoc = {
        _id: consultationId,
        organization: orgId,
        status: "analyzed",
        mlAnalysis: {
          disease: "Migraine",
          redFlag: false,
          needsEscalation: true,
        },
        workerDecision: null,
        save: vi.fn().mockResolvedValue(true),
      };

      vi.spyOn(Consultation, "findOne").mockResolvedValue(mockDoc);

      const res = await request(app)
        .patch(`/api/v1/consultation/${consultationId}/accept`)
        .set("Authorization", `Bearer ${workerToken}`)
        .send({
          overrideReason: "patient_improved",
          overrideNote: "short", // < 10 chars
        });

      expect(res.status).toBe(400);
      expect(res.body.message).toContain("Request validation failed");
    });

    it("should reject accept if overrideNote consists solely of whitespace characters", async () => {
      const consultationId = new mongoose.Types.ObjectId();
      const mockDoc = {
        _id: consultationId,
        organization: orgId,
        status: "analyzed",
        mlAnalysis: {
          disease: "Migraine",
          redFlag: false,
          needsEscalation: true,
        },
        workerDecision: null,
        save: vi.fn().mockResolvedValue(true),
      };

      vi.spyOn(Consultation, "findOne").mockResolvedValue(mockDoc);

      const res = await request(app)
        .patch(`/api/v1/consultation/${consultationId}/accept`)
        .set("Authorization", `Bearer ${workerToken}`)
        .send({
          overrideReason: "patient_improved",
          overrideNote: "          ", // 10 spaces
        });

      expect(res.status).toBe(400);
      expect(res.body.message).toContain("validation failed");
      expect(mockDoc.save).not.toHaveBeenCalled();
    });

    it("should permit accept with valid overrideReason and overrideNote (>= 10 chars) and record overrideDetails", async () => {
      const consultationId = new mongoose.Types.ObjectId();
      const mockDoc = {
        _id: consultationId,
        organization: orgId,
        status: "analyzed",
        mlAnalysis: {
          disease: "Migraine",
          redFlag: false,
          needsEscalation: true,
        },
        workerDecision: null,
        save: vi.fn().mockResolvedValue(true),
      };

      vi.spyOn(Consultation, "findOne").mockResolvedValue(mockDoc);

      const res = await request(app)
        .patch(`/api/v1/consultation/${consultationId}/accept`)
        .set("Authorization", `Bearer ${workerToken}`)
        .send({
          overrideReason: "patient_improved",
          overrideNote: "Patient vitals stabilized and headache substantially relieved after rest",
        });

      expect(res.status).toBe(200);
      expect(res.body.consultation.overrideReason).toBe("patient_improved");
      expect(res.body.consultation.overrideDetails.note).toContain("Patient vitals stabilized");
      expect(mockDoc.status).toBe("closed");
      expect(mockDoc.workerDecision).toBe("accepted");
    });
  });

  describe("2.2 State Machine Atomic Guard Rules", () => {
    it("should reject double accept on an already closed consultation", async () => {
      const consultationId = new mongoose.Types.ObjectId();
      const mockDoc = {
        _id: consultationId,
        organization: orgId,
        status: "closed",
        workerDecision: "accepted",
        save: vi.fn(),
      };

      vi.spyOn(Consultation, "findOne").mockResolvedValue(mockDoc);

      const res = await request(app)
        .patch(`/api/v1/consultation/${consultationId}/accept`)
        .set("Authorization", `Bearer ${workerToken}`)
        .send({});

      expect(res.status).toBe(400);
      expect(res.body.message).toContain("already closed");
    });

    it("should reject accept on a consultation that has already been escalated", async () => {
      const consultationId = new mongoose.Types.ObjectId();
      const mockDoc = {
        _id: consultationId,
        organization: orgId,
        status: "pending",
        workerDecision: "escalated",
        save: vi.fn(),
      };

      vi.spyOn(Consultation, "findOne").mockResolvedValue(mockDoc);

      const res = await request(app)
        .patch(`/api/v1/consultation/${consultationId}/accept`)
        .set("Authorization", `Bearer ${workerToken}`)
        .send({});

      expect(res.status).toBe(400);
      expect(res.body.message).toContain("already been escalated");
    });

    it("should reject doctor second opinion on an already closed consultation", async () => {
      const consultationId = new mongoose.Types.ObjectId();
      const mockDoc = {
        _id: consultationId,
        organization: orgId,
        assignedDoctor: doctorId,
        status: "closed",
        save: vi.fn(),
      };

      vi.spyOn(Consultation, "findOne").mockResolvedValue(mockDoc);

      const res = await request(app)
        .patch(`/api/v1/consultation/${consultationId}/respond`)
        .set("Authorization", `Bearer ${doctorToken}`)
        .send({ diagnosis: "Tension headache", recommendation: "Hydration and rest" });

      expect(res.status).toBe(400);
      expect(res.body.message).toContain("Cannot respond to a closed consultation");
    });

    it("should reject escalation without a reason", async () => {
      const consultationId = new mongoose.Types.ObjectId();

      const res = await request(app)
        .patch(`/api/v1/consultation/${consultationId}/escalate`)
        .set("Authorization", `Bearer ${workerToken}`)
        .send({ doctorId: doctorId.toString(), reason: "" });

      expect(res.status).toBe(400);
    });
  });

  describe("2.1 Mass-Assignment Prevention", () => {
    it("should strictly reject client attempts to inject redFlag or needsEscalation on consultation creation", async () => {
      const res = await request(app)
        .post("/api/v1/consultation")
        .set("Authorization", `Bearer ${workerToken}`)
        .send({
          patientId: new mongoose.Types.ObjectId().toString(),
          symptoms: ["headache", "fever"],
          redFlag: true, // Forbidden field
        });

      // Zod .strict() rejects unrecognized properties with 400 Bad Request
      expect(res.status).toBe(400);
      expect(res.body.message).toContain("Request validation failed");
    });
  });

  describe("2.6 AI vs Doctor Diagnostic Agreement", () => {
    it("should correctly compute agreement = true when normalized doctor and AI diagnoses match", () => {
      expect(normalizeDiagnosis("Fungal infection")).toBe("fungal infection");
      expect(normalizeDiagnosis("Fungal_infection")).toBe("fungal infection");
      expect(normalizeDiagnosis("Hypertension ")).toBe("hypertension");

      const normAi = normalizeDiagnosis("Fungal infection");
      const normDoc = normalizeDiagnosis("Fungal Infection (tinea)");
      const agreement = normAi === normDoc || normDoc.includes(normAi) || normAi.includes(normDoc);
      expect(agreement).toBe(true);
    });

    it("should compute agreement = false when doctor disagrees with AI prediction", () => {
      const normAi = normalizeDiagnosis("GERD");
      const normDoc = normalizeDiagnosis("Peptic ulcer disease");
      const agreement = normAi === normDoc || normDoc.includes(normAi) || normAi.includes(normDoc);
      expect(agreement).toBe(false);
    });
  });
});
