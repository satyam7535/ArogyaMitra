import { describe, it, expect, vi, beforeEach } from "vitest";
import request from "supertest";
import mongoose from "mongoose";
import app from "../src/index.js";
import { Patient, Consultation } from "../src/models/index.js";
import jwt from "jsonwebtoken";
import { ROLES } from "../src/config/roles.js";

const JWT_SECRET = process.env.JWT_SECRET || "mock_jwt_secret_for_test_runs_must_be_over_32_characters!";

describe("Phase P3.4: DPDP Admin-Approved Export & Erasure Protocol", () => {
  let workerToken, doctorToken, adminToken;
  let testPatientId;
  const orgId = new mongoose.Types.ObjectId().toString();
  const workerId = new mongoose.Types.ObjectId().toString();
  const doctorId = new mongoose.Types.ObjectId().toString();
  const adminId = new mongoose.Types.ObjectId().toString();

  let mockPatient;

  beforeEach(() => {
    vi.restoreAllMocks();

    workerToken = jwt.sign({ id: workerId, role: ROLES.WORKER, organization: orgId }, JWT_SECRET, { expiresIn: "1h" });
    doctorToken = jwt.sign({ id: doctorId, role: ROLES.DOCTOR, organization: orgId }, JWT_SECRET, { expiresIn: "1h" });
    adminToken = jwt.sign({ id: adminId, role: ROLES.ADMIN, organization: orgId }, JWT_SECRET, { expiresIn: "1h" });

    testPatientId = new mongoose.Types.ObjectId().toString();

    mockPatient = {
      _id: testPatientId,
      name: "DPDP Test Subject",
      age: 45,
      gender: "Male",
      phoneNumber: "9876500001",
      address: "Village Test, Ward 1",
      organization: orgId,
      registeredBy: workerId,
      consentGiven: true,
      exportApproved: false,
      deletionApproved: false,
      isDeleted: false,
      save: vi.fn().mockResolvedValue(true),
      getDecrypted: vi.fn().mockReturnValue({
        name: "DPDP Test Subject",
        phoneNumber: "9876500001",
        address: "Village Test, Ward 1",
        emergencyContact: null,
      }),
    };

    vi.spyOn(Patient, "findOne").mockImplementation(() => Promise.resolve(mockPatient));
    vi.spyOn(Consultation, "find").mockImplementation(() => ({
      sort: vi.fn().mockResolvedValue([]),
    }));
  });

  it("1. Worker attempting POST approve-export should be strictly rejected with HTTP 403 Forbidden", async () => {
    const res = await request(app)
      .post(`/api/v1/patient/${testPatientId}/approve-export`)
      .set("Authorization", `Bearer ${workerToken}`);

    expect(res.status).toBe(403);
  });

  it("2. Doctor attempting POST approve-delete should be strictly rejected with HTTP 403 Forbidden", async () => {
    const res = await request(app)
      .post(`/api/v1/patient/${testPatientId}/approve-delete`)
      .set("Authorization", `Bearer ${doctorToken}`);

    expect(res.status).toBe(403);
  });

  it("3. Worker attempting GET export on unapproved patient should be rejected with HTTP 403", async () => {
    mockPatient.exportApproved = false;
    const res = await request(app)
      .get(`/api/v1/patient/${testPatientId}/export`)
      .set("Authorization", `Bearer ${workerToken}`);

    expect(res.status).toBe(403);
    expect(res.body.code).toBe("ADMIN_APPROVAL_REQUIRED");
  });

  it("4. Worker attempting DELETE erasure on unapproved patient should be rejected with HTTP 403", async () => {
    mockPatient.deletionApproved = false;
    const res = await request(app)
      .delete(`/api/v1/patient/${testPatientId}`)
      .set("Authorization", `Bearer ${workerToken}`);

    expect(res.status).toBe(403);
    expect(res.body.code).toBe("ADMIN_APPROVAL_REQUIRED");
  });

  it("5. Admin successfully approves data export with HTTP 200", async () => {
    const res = await request(app)
      .post(`/api/v1/patient/${testPatientId}/approve-export`)
      .set("Authorization", `Bearer ${adminToken}`);

    expect(res.status).toBe(200);
    expect(res.body.result.success).toBe(true);
    expect(mockPatient.exportApproved).toBe(true);
  });

  it("6. Worker attempting GET export AFTER Admin approval succeeds with HTTP 200", async () => {
    mockPatient.exportApproved = true;
    const res = await request(app)
      .get(`/api/v1/patient/${testPatientId}/export`)
      .set("Authorization", `Bearer ${workerToken}`);

    expect(res.status).toBe(200);
    expect(res.body.data.patient.name).toBe("DPDP Test Subject");
  });

  it("7. Admin successfully approves erasure with HTTP 200", async () => {
    const res = await request(app)
      .post(`/api/v1/patient/${testPatientId}/approve-delete`)
      .set("Authorization", `Bearer ${adminToken}`);

    expect(res.status).toBe(200);
    expect(res.body.result.success).toBe(true);
    expect(mockPatient.deletionApproved).toBe(true);
  });

  it("8. Worker attempting DELETE erasure AFTER Admin approval succeeds with HTTP 200 & anonymization", async () => {
    mockPatient.deletionApproved = true;
    const res = await request(app)
      .delete(`/api/v1/patient/${testPatientId}`)
      .set("Authorization", `Bearer ${workerToken}`);

    expect(res.status).toBe(200);
    expect(mockPatient.name).toBe("[ANONYMIZED]");
    expect(mockPatient.isDeleted).toBe(true);
  });
});
