import { describe, it, expect, vi, beforeEach } from "vitest";
import request from "supertest";
import mongoose from "mongoose";
import app from "../src/index.js";
import { Consultation, Patient } from "../src/models/index.js";
import jwt from "jsonwebtoken";
import { ROLES } from "../src/config/roles.js";
import { validateFileMagicBytes } from "../src/utils/upload.js";
import { v2 as cloudinary } from "cloudinary";
import { Writable } from "stream";

const JWT_SECRET = process.env.JWT_SECRET || "mock_jwt_secret_for_test_runs_must_be_over_32_characters!";

describe("Phase P3.5: Upload Storage Adapter & Magic-Byte Defense Suite", () => {
  let workerToken;
  const orgId = new mongoose.Types.ObjectId().toString();
  const workerId = new mongoose.Types.ObjectId().toString();
  const patientId = new mongoose.Types.ObjectId().toString();

  beforeEach(() => {
    vi.restoreAllMocks();
    workerToken = jwt.sign({ id: workerId, role: ROLES.WORKER, organization: orgId }, JWT_SECRET, { expiresIn: "1h" });

    // Mock patient lookup
    vi.spyOn(Patient, "findOne").mockResolvedValue({
      _id: patientId,
      organization: orgId,
      consentGiven: true,
      isDeleted: false,
    });

    // Mock consultation creation
    vi.spyOn(Consultation, "create").mockImplementation(async (data) => ({
      _id: new mongoose.Types.ObjectId(),
      ...data,
      save: vi.fn().mockResolvedValue(true),
    }));

    // Mock Cloudinary upload stream
    vi.spyOn(cloudinary.uploader, "upload_stream").mockImplementation((options, callback) => {
      const stream = new Writable({
        write(chunk, encoding, next) {
          next();
        },
      });
      stream.on("finish", () => {
        if (callback) {
          callback(null, {
            secure_url: "https://res.cloudinary.com/test/raw/upload/v12345/authentic.pdf",
          });
        }
      });
      return stream;
    });
  });

  describe("1. Binary Magic Bytes Validation Unit Tests", () => {
    it("should accept valid PDF magic bytes (%PDF-)", () => {
      const validPdf = Buffer.from([0x25, 0x50, 0x44, 0x46, 0x2d, 0x31, 0x2e, 0x34]);
      expect(validateFileMagicBytes(validPdf, "application/pdf")).toBe(true);
    });

    it("should accept valid PNG magic bytes", () => {
      const validPng = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
      expect(validateFileMagicBytes(validPng, "image/png")).toBe(true);
    });

    it("should accept valid JPEG magic bytes", () => {
      const validJpg = Buffer.from([0xff, 0xd8, 0xff, 0xe0, 0x00, 0x10]);
      expect(validateFileMagicBytes(validJpg, "image/jpeg")).toBe(true);
    });

    it("should reject Windows MZ executable masquerading as PNG", () => {
      const fakeExeAsPng = Buffer.from([0x4d, 0x5a, 0x90, 0x00, 0x03, 0x00]);
      expect(validateFileMagicBytes(fakeExeAsPng, "image/png")).toBe(false);
    });

    it("should reject ELF Linux binary masquerading as PDF", () => {
      const elfAsPdf = Buffer.from([0x7f, 0x45, 0x4c, 0x46, 0x02, 0x01]);
      expect(validateFileMagicBytes(elfAsPdf, "application/pdf")).toBe(false);
    });

    it("should reject HTML/script polyglot masquerading as PDF", () => {
      const htmlAsPdf = Buffer.from("<script>alert('xss')</script>");
      expect(validateFileMagicBytes(htmlAsPdf, "application/pdf")).toBe(false);
    });
  });

  describe("2. HTTP Route Level Enforcement (POST /api/v1/consultation)", () => {
    it("should reject unauthenticated upload attempt with HTTP 401 Unauthorized", async () => {
      const validPdf = Buffer.from([0x25, 0x50, 0x44, 0x46, 0x2d, 0x31, 0x2e, 0x34]);
      const res = await request(app)
        .post("/api/v1/consultation")
        .field("patientId", patientId)
        .field("symptoms", JSON.stringify(["itching", "skin_rash"]))
        .attach("attachments", validPdf, "test.pdf");

      expect(res.status).toBe(401);
    });

    it("should strictly reject disguised executable (MZ header) with HTTP 400 Bad Request", async () => {
      const disguisedExe = Buffer.from([0x4d, 0x5a, 0x90, 0x00, 0x03, 0x00, 0x00, 0x00]);

      const res = await request(app)
        .post("/api/v1/consultation")
        .set("Authorization", `Bearer ${workerToken}`)
        .field("patientId", patientId)
        .field("symptoms", JSON.stringify(["itching", "skin_rash"]))
        .attach("attachments", disguisedExe, { filename: "report.pdf", contentType: "application/pdf" });

      expect(res.status).toBe(400);
      expect(res.body.message).toContain("binary magic bytes do not match declared MIME type");
    });

    it("should accept authentic PDF document with correct magic bytes and worker auth", async () => {
      const authenticPdf = Buffer.from("%PDF-1.4 sample content with valid header bytes");

      const res = await request(app)
        .post("/api/v1/consultation")
        .set("Authorization", `Bearer ${workerToken}`)
        .field("patientId", patientId)
        .field("symptoms", JSON.stringify(["itching", "skin_rash"]))
        .attach("attachments", authenticPdf, { filename: "authentic.pdf", contentType: "application/pdf" });

      expect(res.status).toBe(201);
      expect(res.body.message).toContain("successfully");
    });
  });
});
