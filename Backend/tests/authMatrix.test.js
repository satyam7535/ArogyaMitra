import { describe, it, expect, vi, beforeEach } from "vitest";
import request from "supertest";
import jwt from "jsonwebtoken";
import mongoose from "mongoose";
import app from "../src/index.js";
import ROLES from "../src/config/roles.js";
import serverConfig from "../src/config/serverConfig.js";

import Consultation from "../src/models/consultation/consultationSchema.js";
import Worker from "../src/models/worker/workerSchema.js";
import Patient from "../src/models/patient/patientSchema.js";

// Helper to extract all registered routes dynamically from Express 5 router
export function extractRegisteredRoutes(appInstance) {
  const routes = [];
  const prefixes = [
    "/api/v1/admin",
    "/api/v1/worker",
    "/api/v1/doctor",
    "/api/v1/patient",
    "/api/v1/consultation",
  ];

  for (const layer of appInstance.router.stack) {
    if (layer.route) {
      const methods = Object.keys(layer.route.methods).map((m) => m.toUpperCase());
      for (const method of methods) {
        routes.push({
          method,
          path: layer.route.path,
        });
      }
    } else if (layer.name === "router" && layer.handle?.stack) {
      for (const p of prefixes) {
        const matchRes = layer.matchers[0](p);
        if (matchRes) {
          for (const subLayer of layer.handle.stack) {
            if (subLayer.route) {
              const methods = Object.keys(subLayer.route.methods).map((m) => m.toUpperCase());
              for (const method of methods) {
                const fullPath = (p + subLayer.route.path).replace(/\/+/g, "/");
                routes.push({
                  method,
                  path: fullPath,
                });
              }
            }
          }
        }
      }
    }
  }
  return routes;
}

// Canonical Authorization Matrix Definition covering 100% of routes
export const ROUTE_AUTH_MATRIX = [
  // Top-Level Public Routes
  { method: "GET", path: "/", access: "public" },
  { method: "GET", path: "/health", access: "public" },

  // Admin Router (8 routes)
  { method: "POST", path: "/api/v1/admin/register", access: "public_disabled" },
  { method: "POST", path: "/api/v1/admin/login", access: "public" },
  { method: "POST", path: "/api/v1/admin/refresh-token", access: "public" },
  { method: "POST", path: "/api/v1/admin/forgot-password", access: "public" },
  { method: "POST", path: "/api/v1/admin/reset-password", access: "public" },
  { method: "POST", path: "/api/v1/admin/logout", access: "protected", allowedRoles: [ROLES.ADMIN] },
  { method: "GET", path: "/api/v1/admin/profile", access: "protected", allowedRoles: [ROLES.ADMIN] },
  { method: "GET", path: "/api/v1/admin/audit-logs", access: "protected", allowedRoles: [ROLES.ADMIN] },

  // Worker Router (10 routes)
  { method: "POST", path: "/api/v1/worker/login", access: "public" },
  { method: "POST", path: "/api/v1/worker/refresh-token", access: "public" },
  { method: "POST", path: "/api/v1/worker/forgot-password", access: "public" },
  { method: "POST", path: "/api/v1/worker/reset-password", access: "public" },
  { method: "POST", path: "/api/v1/worker/logout", access: "protected", allowedRoles: [ROLES.WORKER] },
  { method: "POST", path: "/api/v1/worker/", access: "protected", allowedRoles: [ROLES.ADMIN] },
  { method: "GET", path: "/api/v1/worker/", access: "protected", allowedRoles: [ROLES.ADMIN] },
  { method: "DELETE", path: "/api/v1/worker/:id", access: "protected", allowedRoles: [ROLES.ADMIN] },
  { method: "PATCH", path: "/api/v1/worker/:id/deactivate", access: "protected", allowedRoles: [ROLES.ADMIN] },
  { method: "PATCH", path: "/api/v1/worker/:id/reactivate", access: "protected", allowedRoles: [ROLES.ADMIN] },

  // Doctor Router (11 routes)
  { method: "POST", path: "/api/v1/doctor/login", access: "public" },
  { method: "POST", path: "/api/v1/doctor/refresh-token", access: "public" },
  { method: "POST", path: "/api/v1/doctor/forgot-password", access: "public" },
  { method: "POST", path: "/api/v1/doctor/reset-password", access: "public" },
  { method: "POST", path: "/api/v1/doctor/logout", access: "protected", allowedRoles: [ROLES.DOCTOR] },
  { method: "POST", path: "/api/v1/doctor/", access: "protected", allowedRoles: [ROLES.ADMIN] },
  { method: "GET", path: "/api/v1/doctor/", access: "protected", allowedRoles: [ROLES.ADMIN] },
  { method: "DELETE", path: "/api/v1/doctor/:id", access: "protected", allowedRoles: [ROLES.ADMIN] },
  { method: "PATCH", path: "/api/v1/doctor/:id/deactivate", access: "protected", allowedRoles: [ROLES.ADMIN] },
  { method: "PATCH", path: "/api/v1/doctor/:id/reactivate", access: "protected", allowedRoles: [ROLES.ADMIN] },
  { method: "GET", path: "/api/v1/doctor/list", access: "protected", allowedRoles: [ROLES.WORKER, ROLES.ADMIN] },

  // Patient Router (8 routes)
  { method: "POST", path: "/api/v1/patient/", access: "protected", allowedRoles: [ROLES.WORKER] },
  { method: "GET", path: "/api/v1/patient/", access: "protected", allowedRoles: [ROLES.WORKER] },
  { method: "GET", path: "/api/v1/patient/:id/export", access: "protected", allowedRoles: [ROLES.WORKER, ROLES.DOCTOR, ROLES.ADMIN] },
  { method: "GET", path: "/api/v1/patient/:id", access: "protected", allowedRoles: [ROLES.WORKER] },
  { method: "DELETE", path: "/api/v1/patient/:id", access: "protected", allowedRoles: [ROLES.WORKER, ROLES.ADMIN] },
  { method: "POST", path: "/api/v1/patient/:id/withdraw-consent", access: "protected", allowedRoles: [ROLES.WORKER, ROLES.ADMIN] },
  { method: "POST", path: "/api/v1/patient/:id/approve-export", access: "protected", allowedRoles: [ROLES.ADMIN] },
  { method: "POST", path: "/api/v1/patient/:id/approve-delete", access: "protected", allowedRoles: [ROLES.ADMIN] },

  // Consultation Router (17 routes)
  { method: "POST", path: "/api/v1/consultation/", access: "protected", allowedRoles: [ROLES.WORKER] },
  { method: "GET", path: "/api/v1/consultation/my", access: "protected", allowedRoles: [ROLES.WORKER] },
  { method: "PATCH", path: "/api/v1/consultation/:id/accept", access: "protected", allowedRoles: [ROLES.WORKER] },
  { method: "PATCH", path: "/api/v1/consultation/:id/escalate", access: "protected", allowedRoles: [ROLES.WORKER] },
  { method: "GET", path: "/api/v1/consultation/admin/all", access: "protected", allowedRoles: [ROLES.ADMIN] },
  { method: "GET", path: "/api/v1/consultation/doctor/all", access: "protected", allowedRoles: [ROLES.DOCTOR] },
  { method: "GET", path: "/api/v1/consultation/pending", access: "protected", allowedRoles: [ROLES.DOCTOR] },
  { method: "PATCH", path: "/api/v1/consultation/:id/respond", access: "protected", allowedRoles: [ROLES.DOCTOR] },
  { method: "GET", path: "/api/v1/consultation/:id", access: "protected", allowedRoles: [ROLES.WORKER, ROLES.DOCTOR] },
  { method: "POST", path: "/api/v1/consultation/:id/analyze", access: "protected", allowedRoles: [ROLES.WORKER, ROLES.DOCTOR] },
  { method: "POST", path: "/api/v1/consultation/:id/analyze/async", access: "protected", allowedRoles: [ROLES.WORKER, ROLES.DOCTOR] },
  { method: "GET", path: "/api/v1/consultation/:id/analyze/status/:jobId", access: "protected", allowedRoles: [ROLES.WORKER, ROLES.DOCTOR] },
  { method: "GET", path: "/api/v1/consultation/queue/metrics", access: "protected", allowedRoles: [ROLES.ADMIN, ROLES.DOCTOR] },
  { method: "POST", path: "/api/v1/consultation/:id/analysis/ml", access: "protected", allowedRoles: [ROLES.WORKER] },
  { method: "POST", path: "/api/v1/consultation/:id/analysis/llm", access: "protected", allowedRoles: [ROLES.WORKER] },
  { method: "POST", path: "/api/v1/consultation/:id/analysis/verdict", access: "protected", allowedRoles: [ROLES.WORKER] },
  { method: "POST", path: "/api/v1/consultation/:id/analysis/report", access: "protected", allowedRoles: [ROLES.WORKER] },
];

describe("1.1 Dynamic Authorization Matrix & Route Table Verification", () => {
  const actualRoutes = extractRegisteredRoutes(app);

  it("should cover 100% of registered Express routes in the authorization matrix", () => {
    expect(actualRoutes.length).toBeGreaterThan(0);

    const missingInMatrix = [];
    for (const route of actualRoutes) {
      const match = ROUTE_AUTH_MATRIX.find(
        (m) => m.method === route.method && m.path === route.path
      );
      if (!match) {
        missingInMatrix.push(`${route.method} ${route.path}`);
      }
    }

    // Must be empty: if a route exists in Express but not in the matrix, test fails immediately!
    expect(missingInMatrix).toEqual([]);
    expect(actualRoutes.length).toBe(ROUTE_AUTH_MATRIX.length);
  });

  describe("Anonymous Probes (Unauthenticated Request Rejection)", () => {
    const protectedRoutes = ROUTE_AUTH_MATRIX.filter((r) => r.access === "protected");

    it.each(protectedRoutes)(
      "rejects anonymous request with 401 for $method $path",
      async ({ method, path }) => {
        const testPath = path
          .replace(":id", new mongoose.Types.ObjectId().toString())
          .replace(":jobId", "job_test_123");

        const res = await request(app)[method.toLowerCase()](testPath);

        expect(res.status).toBe(401);
        expect(res.body.message).toContain("No authentication token provided");
      }
    );
  });

  describe("Wrong Role Probes (Unauthorized Role Rejection)", () => {
    const protectedRoutes = ROUTE_AUTH_MATRIX.filter((r) => r.access === "protected");

    it.each(protectedRoutes)(
      "rejects unauthorized role with 403 for $method $path",
      async ({ method, path, allowedRoles }) => {
        const allRoles = [ROLES.ADMIN, ROLES.WORKER, ROLES.DOCTOR];
        const unauthorizedRole = allRoles.find((role) => !allowedRoles.includes(role));

        if (!unauthorizedRole) return;

        const wrongRoleToken = jwt.sign(
          {
            id: new mongoose.Types.ObjectId().toString(),
            role: unauthorizedRole,
            organization: new mongoose.Types.ObjectId().toString(),
          },
          serverConfig.JWT_SECRET,
          { expiresIn: "5m" }
        );

        const testPath = path
          .replace(":id", new mongoose.Types.ObjectId().toString())
          .replace(":jobId", "job_test_123");

        const res = await request(app)
          [method.toLowerCase()](testPath)
          .set("Authorization", `Bearer ${wrongRoleToken}`);

        expect(res.status).toBe(403);
        expect(res.body.message).toContain("Insufficient role permissions");
      }
    );
  });

  describe("Cross-Organization & Positive Control Write Probes", () => {
    const orgAlpha = new mongoose.Types.ObjectId();
    const orgBeta = new mongoose.Types.ObjectId();
    const doctorId = new mongoose.Types.ObjectId();

    beforeEach(() => {
      vi.restoreAllMocks();
    });

    it("should reject cross-org consultation escalation with 404 and allow same-org with 200", async () => {
      const consultationId = new mongoose.Types.ObjectId();
      const mockDocOrgAlpha = {
        _id: consultationId,
        organization: orgAlpha,
        status: "pending",
        save: vi.fn().mockResolvedValue(true),
      };

      vi.spyOn(Consultation, "findOne").mockImplementation((query) => {
        if (
          query._id?.toString() === consultationId.toString() &&
          query.organization?.toString() === orgAlpha.toString()
        ) {
          return Promise.resolve(mockDocOrgAlpha);
        }
        return Promise.resolve(null);
      });

      // Probe 1: Cross-org write from Org Beta -> 404
      const tokenBeta = jwt.sign(
        { id: new mongoose.Types.ObjectId().toString(), role: ROLES.WORKER, organization: orgBeta.toString() },
        serverConfig.JWT_SECRET
      );

      const crossRes = await request(app)
        .patch(`/api/v1/consultation/${consultationId}/escalate`)
        .set("Authorization", `Bearer ${tokenBeta}`)
        .send({ doctorId: doctorId.toString(), reason: "Patient showing severe cardiac symptoms" });

      expect(crossRes.status).toBe(404);
      expect(crossRes.body.message).toContain("not found");

      // Probe 2: Positive control from Org Alpha (Right Role, Right Org) -> 200
      const tokenAlpha = jwt.sign(
        { id: new mongoose.Types.ObjectId().toString(), role: ROLES.WORKER, organization: orgAlpha.toString() },
        serverConfig.JWT_SECRET
      );

      const posRes = await request(app)
        .patch(`/api/v1/consultation/${consultationId}/escalate`)
        .set("Authorization", `Bearer ${tokenAlpha}`)
        .send({ doctorId: doctorId.toString(), reason: "Patient showing severe cardiac symptoms" });

      expect(posRes.status).toBe(200);
      expect(posRes.body.consultation.workerDecision).toBe("escalated");
    });

    it("should reject cross-org consultation doctor response with 404 and allow same-org with 200", async () => {
      const consultationId = new mongoose.Types.ObjectId();
      const doctorAlphaId = new mongoose.Types.ObjectId();
      const mockDocOrgAlpha = {
        _id: consultationId,
        organization: orgAlpha,
        assignedDoctor: doctorAlphaId,
        status: "escalated",
        __v: 0,
        save: vi.fn().mockResolvedValue(true),
      };

      vi.spyOn(Consultation, "findOne").mockImplementation((query) => {
        if (
          query._id?.toString() === consultationId.toString() &&
          query.organization?.toString() === orgAlpha.toString() &&
          query.assignedDoctor?.toString() === doctorAlphaId.toString()
        ) {
          return Promise.resolve(mockDocOrgAlpha);
        }
        return Promise.resolve(null);
      });

      // Cross-org write from Doctor in Org Beta -> 404
      const tokenDoctorBeta = jwt.sign(
        { id: new mongoose.Types.ObjectId().toString(), role: ROLES.DOCTOR, organization: orgBeta.toString() },
        serverConfig.JWT_SECRET
      );

      const crossRes = await request(app)
        .patch(`/api/v1/consultation/${consultationId}/respond`)
        .set("Authorization", `Bearer ${tokenDoctorBeta}`)
        .send({ diagnosis: "Viral Bronchitis", recommendation: "Prescribing bronchodilators." });

      expect(crossRes.status).toBe(404);

      // Positive control from Doctor in Org Alpha -> 200
      const tokenDoctorAlpha = jwt.sign(
        { id: doctorAlphaId.toString(), role: ROLES.DOCTOR, organization: orgAlpha.toString() },
        serverConfig.JWT_SECRET
      );

      const posRes = await request(app)
        .patch(`/api/v1/consultation/${consultationId}/respond`)
        .set("Authorization", `Bearer ${tokenDoctorAlpha}`)
        .send({ diagnosis: "Viral Bronchitis", recommendation: "Prescribing bronchodilators." });

      expect(posRes.status).toBe(200);
      expect(posRes.body.consultation.secondOpinion.diagnosis).toBe("Viral Bronchitis");
    });

    it("should reject cross-org worker deactivation with 404 and allow same-org with 200", async () => {
      const targetWorkerId = new mongoose.Types.ObjectId();
      const mockWorkerOrgAlpha = {
        _id: targetWorkerId,
        name: "Asha Devi",
        organization: orgAlpha,
        isActive: true,
      };

      vi.spyOn(Worker, "findOneAndUpdate").mockImplementation((query, update) => {
        if (
          query._id?.toString() === targetWorkerId.toString() &&
          query.organization?.toString() === orgAlpha.toString()
        ) {
          return Promise.resolve({ ...mockWorkerOrgAlpha, ...update });
        }
        return Promise.resolve(null);
      });

      // Cross-org Admin from Org Beta -> 404
      const tokenAdminBeta = jwt.sign(
        { id: new mongoose.Types.ObjectId().toString(), role: ROLES.ADMIN, organization: orgBeta.toString() },
        serverConfig.JWT_SECRET
      );

      const crossRes = await request(app)
        .delete(`/api/v1/worker/${targetWorkerId}`)
        .set("Authorization", `Bearer ${tokenAdminBeta}`);

      expect(crossRes.status).toBe(404);

      // Positive control Admin from Org Alpha -> 200
      const tokenAdminAlpha = jwt.sign(
        { id: new mongoose.Types.ObjectId().toString(), role: ROLES.ADMIN, organization: orgAlpha.toString() },
        serverConfig.JWT_SECRET
      );

      const posRes = await request(app)
        .delete(`/api/v1/worker/${targetWorkerId}`)
        .set("Authorization", `Bearer ${tokenAdminAlpha}`);

      expect(posRes.status).toBe(200);
      expect(posRes.body.message).toContain("deactivated successfully");
    });

    it("should reject cross-org patient deletion with 404 and allow same-org with 200", async () => {
      const patientId = new mongoose.Types.ObjectId();
      const mockPatientOrgAlpha = {
        _id: patientId,
        name: "Ramesh Pawar",
        organization: orgAlpha,
        isDeleted: false,
        save: vi.fn().mockResolvedValue(true),
      };

      vi.spyOn(Patient, "findOne").mockImplementation((query) => {
        if (
          query._id?.toString() === patientId.toString() &&
          query.organization?.toString() === orgAlpha.toString() &&
          query.isDeleted?.$ne === true
        ) {
          return Promise.resolve(mockPatientOrgAlpha);
        }
        return Promise.resolve(null);
      });

      // Cross-org Worker from Org Beta -> 404
      const tokenWorkerBeta = jwt.sign(
        { id: new mongoose.Types.ObjectId().toString(), role: ROLES.WORKER, organization: orgBeta.toString() },
        serverConfig.JWT_SECRET
      );

      const crossRes = await request(app)
        .delete(`/api/v1/patient/${patientId}`)
        .set("Authorization", `Bearer ${tokenWorkerBeta}`);

      expect(crossRes.status).toBe(404);
      expect(crossRes.body.message).toContain("Patient not found");

      // Positive control Worker from Org Alpha -> 200
      const tokenWorkerAlpha = jwt.sign(
        { id: new mongoose.Types.ObjectId().toString(), role: ROLES.WORKER, organization: orgAlpha.toString() },
        serverConfig.JWT_SECRET
      );

      const posRes = await request(app)
        .delete(`/api/v1/patient/${patientId}`)
        .set("Authorization", `Bearer ${tokenWorkerAlpha}`);

      expect(posRes.status).toBe(200);
      expect(posRes.body.message).toContain("anonymized");
      expect(mockPatientOrgAlpha.consentGiven).toBe(false);
      expect(mockPatientOrgAlpha.name).toBe("[ANONYMIZED]");
    });
  });
});
