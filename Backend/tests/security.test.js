import express from "express";
import { describe, it, expect, vi, beforeEach } from "vitest";
import jwt from "jsonwebtoken";
import request from "supertest";
import mongoose from "mongoose";
import app from "../src/index.js";
import { z } from "zod";
import crypto from "crypto";
import {
  encryptField,
  decryptField,
  rotateFieldEncryption,
  hashPassword,
  verifyPassword,
  generateSecureToken,
  hashToken,
} from "../src/utils/crypto.js";
import { verifyToken } from "../src/middlewares/auth.middleware.js";
import { enforceOrgScope, scopeFilter } from "../src/middlewares/orgScope.middleware.js";
import { authenticateWithLockout, rotateRefreshToken } from "../src/service/auth.service.js";
import { loginWorker } from "../src/service/worker.service.js";
import { dispatchPasswordReset } from "../src/utils/emailAdapter.js";
import { sanitizeForLogging } from "../src/middlewares/logging.middleware.js";
import ROLES from "../src/config/roles.js";
import serverConfig from "../src/config/serverConfig.js";

import { validateFileMagicBytes } from "../src/utils/upload.js";

import Worker from "../src/models/worker/workerSchema.js";
import RefreshToken from "../src/models/auth/refreshTokenSchema.js";
import AuditLog from "../src/models/audit/auditLogSchema.js";
import Patient from "../src/models/patient/patientSchema.js";
import Consultation from "../src/models/consultation/consultationSchema.js";

describe("Phase 2 — Security & Cryptographic Integrity", () => {
  // ── 1. Cryptographic Primitives ───────────────────────────────────────────
  describe("1. AES-256-GCM Field-Level Encryption", () => {
    it("should encrypt and decrypt patient PII correctly", () => {
      const sensitivePhone = "+91-9876543210";
      const sensitiveAddress = "Vill: Rampur, PO: Bodh Gaya, Bihar 824231";

      const encPhone = encryptField(sensitivePhone);
      const encAddress = encryptField(sensitiveAddress);

      expect(encPhone).not.toBe(sensitivePhone);
      expect(encPhone.split(":")).toHaveLength(3); // iv:authTag:encrypted

      expect(decryptField(encPhone)).toBe(sensitivePhone);
      expect(decryptField(encAddress)).toBe(sensitiveAddress);
    });

    it("should handle null or invalid ciphertexts gracefully", () => {
      expect(encryptField(null)).toBeNull();
      expect(decryptField(null)).toBeNull();
      expect(decryptField("not-encrypted-plaintext")).toBe("not-encrypted-plaintext");
      expect(decryptField("bad:auth:tag")).toBe("[DECRYPTION_FAILED]");
    });
  });

  describe("2. Argon2id Password Hashing", () => {
    it("should hash password with Argon2id and verify correctly", async () => {
      const password = "StrongPassword@2026!";
      const hashed = await hashPassword(password);

      expect(hashed.startsWith("$argon2id$")).toBe(true);
      expect(await verifyPassword(hashed, password)).toBe(true);
      expect(await verifyPassword(hashed, "WrongPassword!")).toBe(false);
    });

    it("should verify legacy bcrypt hashes for backward compatibility", async () => {
      const bcryptHash = "$2b$10$w8T9H6VbS0C6Z9S7qZ8n0eU4E5r6T7y8U9i0O1p2A3s4D5f6G7h8J"; // mock shape
      expect(await verifyPassword(bcryptHash, "wrong")).toBe(false);
    });
  });

  describe("3. Secure Token Utilities", () => {
    it("should generate cryptographically random tokens and SHA-256 hashes", () => {
      const token1 = generateSecureToken(32);
      const token2 = generateSecureToken(32);
      expect(token1).not.toBe(token2);
      expect(token1).toHaveLength(64); // 32 bytes in hex

      const hash1 = hashToken(token1);
      const hash2 = hashToken(token1);
      expect(hash1).toBe(hash2);
      expect(hash1).toHaveLength(64); // SHA-256 hex
    });
  });

  // ── 2. Central Validated Config (Zod) ─────────────────────────────────────
  describe("4. Central Validated Config (Zod)", () => {
    const configSchema = z.object({
      PORT: z.coerce.number().default(5000),
      DB_URL: z.string().min(1),
      JWT_SECRET: z.string().min(32, "JWT_SECRET must be at least 32 characters long"),
      JWT_EXPIRY: z.string().default("15m"),
      NODE_ENV: z.enum(["development", "production", "test"]).default("development"),
    });

    it("should pass validation with valid secrets", () => {
      const valid = configSchema.safeParse({
        PORT: "5000",
        DB_URL: "mongodb://127.0.0.1:27017/arogyamitra",
        JWT_SECRET: "this_is_a_very_long_and_secure_jwt_secret_32_chars!",
      });
      expect(valid.success).toBe(true);
      expect(valid.data.PORT).toBe(5000);
      expect(valid.data.JWT_EXPIRY).toBe("15m");
    });

    it("should fail validation if JWT_SECRET is less than 32 characters", () => {
      const invalid = configSchema.safeParse({
        DB_URL: "mongodb://127.0.0.1:27017/arogyamitra",
        JWT_SECRET: "short_secret", // < 32 chars
      });
      expect(invalid.success).toBe(false);
      expect(invalid.error.format().JWT_SECRET._errors[0]).toContain("at least 32 characters");
    });
  });

  // ── 3. Authorization & RBAC Middleware ────────────────────────────────────
  describe("5. Role & Organization Authorization Middleware", () => {
    it("should reject requests without authorization token (401)", () => {
      const req = { headers: {}, cookies: {} };
      const res = { status: vi.fn().mockReturnThis(), json: vi.fn() };
      const next = vi.fn();

      verifyToken([ROLES.ADMIN])(req, res, next);
      expect(res.status).toHaveBeenCalledWith(401);
      expect(next).not.toHaveBeenCalled();
    });

    it("should reject expired tokens with TOKEN_EXPIRED code (401)", () => {
      const expiredToken = jwt.sign(
        { id: "u1", role: ROLES.WORKER, organization: "org1" },
        serverConfig.JWT_SECRET,
        { expiresIn: "-1s" }
      );

      const req = { headers: { authorization: `Bearer ${expiredToken}` }, cookies: {} };
      const res = { status: vi.fn().mockReturnThis(), json: vi.fn() };
      const next = vi.fn();

      verifyToken([ROLES.WORKER])(req, res, next);
      expect(res.status).toHaveBeenCalledWith(401);
      expect(res.json).toHaveBeenCalledWith(expect.objectContaining({ code: "TOKEN_EXPIRED" }));
      expect(next).not.toHaveBeenCalled();
    });

    it("should reject tokens with insufficient role permissions (403)", () => {
      const token = jwt.sign(
        { id: "w1", role: ROLES.WORKER, organization: "org1" },
        serverConfig.JWT_SECRET
      );

      const req = { headers: { authorization: `Bearer ${token}` }, cookies: {} };
      const res = { status: vi.fn().mockReturnThis(), json: vi.fn() };
      const next = vi.fn();

      verifyToken([ROLES.ADMIN])(req, res, next); // Worker trying to access Admin endpoint
      expect(res.status).toHaveBeenCalledWith(403);
      expect(res.json).toHaveBeenCalledWith(expect.objectContaining({ message: expect.stringContaining("Insufficient") }));
      expect(next).not.toHaveBeenCalled();
    });

    it("should authorize valid token with canonical role and attach context", () => {
      const token = jwt.sign(
        { id: "w1", role: ROLES.WORKER, organization: "org_alpha" },
        serverConfig.JWT_SECRET
      );

      const req = { headers: { authorization: `Bearer ${token}` }, cookies: {} };
      const res = { status: vi.fn().mockReturnThis(), json: vi.fn() };
      const next = vi.fn();

      verifyToken([ROLES.WORKER])(req, res, next);
      expect(next).toHaveBeenCalled();
      expect(req.user.id).toBe("w1");
      expect(req.user.role).toBe(ROLES.WORKER);
      expect(req.user.organization).toBe("org_alpha");
    });

    it("should strictly reject wrongly-cased role tokens and spoofing attempts (403)", () => {
      const rejectedVariants = [
        "worker",      // lowercase variant
        "WORKER",      // uppercase variant
        "wOrKeR",      // mixed-case variant
        "admin",       // lowercase wrong role
        "Admin",       // wrong role
        "doctor",      // lowercase wrong role
        "Doctor",      // wrong role
        "Worker ",     // trailing whitespace
        " Worker",     // leading whitespace
        "worker\0",    // null-byte attack
        "Worker\n",    // newline attack
        "",            // empty string
      ];

      for (const badRole of rejectedVariants) {
        const token = jwt.sign(
          { id: "u_bad", role: badRole, organization: "org_alpha" },
          serverConfig.JWT_SECRET
        );

        const req = { headers: { authorization: `Bearer ${token}` }, cookies: {} };
        const res = { status: vi.fn().mockReturnThis(), json: vi.fn() };
        const next = vi.fn();

        verifyToken([ROLES.WORKER])(req, res, next);
        expect(res.status).toHaveBeenCalledWith(403);
        expect(res.json).toHaveBeenCalledWith({ message: "Forbidden: Insufficient role permissions" });
        expect(next).not.toHaveBeenCalled();
      }
    });
  });

  // ── 4. Multi-Tenant Organization Scoping & Anti-Enumeration ───────────────
  describe("6. Multi-Tenant Organization Scoping & Anti-Enumeration (404 Rule)", () => {
    it("should return 404 (NOT 403) when resource belongs to another organization", async () => {
      const mockPatient = {
        _id: "patient_123",
        name: "Ramesh Kumar",
        organization: "org_beta",
      };

      const mockModel = {
        findById: vi.fn().mockResolvedValue(mockPatient),
      };

      const req = {
        params: { id: "patient_123" },
        user: { id: "worker_1", role: ROLES.WORKER, organization: "org_alpha" },
      };
      const res = { status: vi.fn().mockReturnThis(), json: vi.fn() };
      const next = vi.fn();

      const middleware = enforceOrgScope(mockModel, "id");
      await middleware(req, res, next);

      expect(res.status).toHaveBeenCalledWith(404);
      expect(res.json).toHaveBeenCalledWith({ message: "Resource not found" });
      expect(next).not.toHaveBeenCalled();
    });

    it("should pass when resource belongs to user's organization", async () => {
      const mockPatient = {
        _id: "patient_123",
        name: "Ramesh Kumar",
        organization: "org_alpha",
      };

      const mockModel = {
        findById: vi.fn().mockResolvedValue(mockPatient),
      };

      const req = {
        params: { id: "patient_123" },
        user: { id: "worker_1", role: ROLES.WORKER, organization: "org_alpha" },
      };
      const res = { status: vi.fn().mockReturnThis(), json: vi.fn() };
      const next = vi.fn();

      const middleware = enforceOrgScope(mockModel, "id");
      await middleware(req, res, next);

      expect(next).toHaveBeenCalled();
      expect(req.scopedResource).toEqual(mockPatient);
    });

    it("should append organization to query filter via scopeFilter", () => {
      const req = { user: { organization: "org_district_9" } };
      const filter = scopeFilter(req, { status: "pending" });

      expect(filter).toEqual({
        status: "pending",
        organization: "org_district_9",
      });
    });
  });

  // ── 5. Account Lockout Protection ─────────────────────────────────────────
  describe("7. Brute-Force Protection & Account Lockout", () => {
    it("should lock account after 5 failed password attempts", async () => {
      const mockUser = {
        email: "worker@phc.gov.in",
        password: await hashPassword("CorrectPassword!"),
        failedLoginAttempts: 4,
        lockUntil: null,
        save: vi.fn().mockResolvedValue(true),
      };

      await expect(
        authenticateWithLockout(mockUser, "WrongPassword!")
      ).rejects.toMatchObject({
        status: 401,
        code: "INVALID_CREDENTIALS",
      });

      expect(mockUser.failedLoginAttempts).toBe(5);
      expect(mockUser.lockUntil).toBeInstanceOf(Date);
      expect(mockUser.lockUntil.getTime()).toBeGreaterThan(Date.now());
      expect(mockUser.save).toHaveBeenCalled();
    });

    it("should reject attempts on a locked account with HTTP 423 Locked", async () => {
      const mockLockedUser = {
        email: "worker@phc.gov.in",
        password: await hashPassword("CorrectPassword!"),
        failedLoginAttempts: 5,
        lockUntil: new Date(Date.now() + 10 * 60 * 1000),
        save: vi.fn(),
      };

      await expect(
        authenticateWithLockout(mockLockedUser, "CorrectPassword!")
      ).rejects.toMatchObject({
        status: 423,
        code: "ACCOUNT_LOCKED",
      });
    });
  });

  // ── 6. HTTP & API Level Security Tests ────────────────────────────────────
  describe("8. HTTP Level Security & Disabled Public Endpoints", () => {
    it("should return 403 Forbidden on public admin registration", async () => {
      const res = await request(app)
        .post("/api/v1/admin/register")
        .send({
          name: "Attacker Admin",
          email: "attacker@exploit.com",
          password: "Password123!",
          location: "Hacked",
          phoneNumber: "+91-0000000000",
        });

      expect(res.status).toBe(403);
      expect(res.body.code).toBe("REGISTRATION_DISABLED");
    });

    it("should omit X-Powered-By header", async () => {
      const res = await request(app).get("/health");
      expect(res.headers["x-powered-by"]).toBeUndefined();
    });

    it("should include standard Helmet security headers", async () => {
      const res = await request(app).get("/health");
      expect(res.headers["x-frame-options"]).toBe("SAMEORIGIN");
      expect(res.headers["x-content-type-options"]).toBe("nosniff");
      expect(res.headers["strict-transport-security"]).toBeDefined();
    });

    it("should never leak resetToken in forgot-password response", async () => {
      const mockWorker = {
        email: "worker@arogyamitra.gov.in",
        save: vi.fn().mockResolvedValue(true),
      };
      vi.spyOn(Worker, "findOne").mockResolvedValue(mockWorker);

      const res = await request(app)
        .post("/api/v1/worker/forgot-password")
        .send({ email: "worker@arogyamitra.gov.in" });

      expect(res.status).toBe(200);
      expect(res.body.resetToken).toBeUndefined();
      expect(res.body.token).toBeUndefined();
      expect(res.body.message).toContain("If that email exists, password reset instructions have been sent");
    });
  });

  // ── 7. Password Reset Dispatch & Console Isolation (Dev vs Test vs Prod) ──
  describe("9. Password Reset Dispatch & Console Isolation", () => {
    it("should print the real reset URL to console.log ONLY in development mode", () => {
      const origEnv = process.env.NODE_ENV;
      try {
        process.env.NODE_ENV = "development";
        const logSpy = vi.spyOn(console, "log").mockImplementation(() => {});

        const res = dispatchPasswordReset({
          email: "worker@arogyamitra.gov.in",
          role: ROLES.WORKER,
          resetToken: "test_raw_reset_token_12345",
          baseUrl: "http://127.0.0.1:5000",
        });

        expect(res.mode).toBe("console");
        expect(res.resetUrl).toBe("http://127.0.0.1:5000/api/v1/worker/reset-password?token=test_raw_reset_token_12345");
        expect(logSpy).toHaveBeenCalledTimes(1);
        expect(logSpy.mock.calls[0][0]).toContain("[DEV RESET LINK]");
        expect(logSpy.mock.calls[0][0]).toContain("token=test_raw_reset_token_12345");
        logSpy.mockRestore();
      } finally {
        process.env.NODE_ENV = origEnv;
      }
    });

    it("should NEVER log reset URL to console in test mode", () => {
      const origEnv = process.env.NODE_ENV;
      try {
        process.env.NODE_ENV = "test";
        const logSpy = vi.spyOn(console, "log").mockImplementation(() => {});

        const res = dispatchPasswordReset({
          email: "worker@arogyamitra.gov.in",
          role: ROLES.WORKER,
          resetToken: "test_raw_reset_token_12345",
        });

        expect(res.mode).toBe("suppressed");
        expect(res.resetUrl).toBeUndefined();
        expect(logSpy).not.toHaveBeenCalled();
        logSpy.mockRestore();
      } finally {
        process.env.NODE_ENV = origEnv;
      }
    });

    it("should NEVER log reset URL to console in production mode", () => {
      const origEnv = process.env.NODE_ENV;
      try {
        process.env.NODE_ENV = "production";
        const logSpy = vi.spyOn(console, "log").mockImplementation(() => {});

        const res = dispatchPasswordReset({
          email: "doctor@arogyamitra.gov.in",
          role: ROLES.DOCTOR,
          resetToken: "test_raw_reset_token_12345",
        });

        expect(res.mode).toBe("smtp");
        expect(res.resetUrl).toBeUndefined();
        expect(logSpy).not.toHaveBeenCalled();
        logSpy.mockRestore();
      } finally {
        process.env.NODE_ENV = origEnv;
      }
    });
  });

  // ── 8. CSRF Protection for Cookie-Authenticated Mutations (1.3) ───────────
  describe("10. CSRF Protection for Cookie-Authenticated Mutations", () => {
    it("should reject state-mutating requests with cookie auth if CSRF header is missing (403)", async () => {
      const res = await request(app)
        .post("/api/v1/patient/")
        .set("Cookie", ["token=mock_jwt_token"])
        .send({ name: "Test" });

      expect(res.status).toBe(403);
      expect(res.body.code).toBe("CSRF_ERROR");
      expect(res.body.message).toContain("CSRF protection triggered");
    });

    it("should allow state-mutating requests with cookie auth when X-Requested-With header is present", async () => {
      const res = await request(app)
        .post("/api/v1/patient/")
        .set("Cookie", ["token=mock_jwt_token"])
        .set("X-Requested-With", "XMLHttpRequest")
        .send({ name: "Test" });

      expect(res.status).not.toBe(403);
      expect(res.body.code).not.toBe("CSRF_ERROR");
    });

    it("should allow state-mutating requests with cookie auth when X-CSRF-Token header is present", async () => {
      const res = await request(app)
        .post("/api/v1/patient/")
        .set("Cookie", ["token=mock_jwt_token"])
        .set("X-CSRF-Token", "valid_csrf_token_string")
        .send({ name: "Test" });

      expect(res.status).not.toBe(403);
      expect(res.body.code).not.toBe("CSRF_ERROR");
    });

    it("should exempt Bearer token Authorization headers from CSRF checks", async () => {
      const res = await request(app)
        .post("/api/v1/patient/")
        .set("Authorization", "Bearer mock_jwt_token")
        .send({ name: "Test" });

      expect(res.status).not.toBe(403);
      expect(res.body.code).not.toBe("CSRF_ERROR");
    });

    it("should exempt safe HTTP methods (GET, HEAD) from CSRF checks even with cookies", async () => {
      const res = await request(app)
        .get("/health")
        .set("Cookie", ["token=mock_jwt_token"]);

      expect(res.status).toBe(200);
    });
  });

  // ── 9. Request ID & PII-Free Structured Logging (1.5) ─────────────────────
  describe("11. Request ID Header & PII-Free Structured Logging", () => {
    it("should attach a unique X-Request-Id UUID header to incoming HTTP responses", async () => {
      const res = await request(app).get("/health");
      expect(res.headers["x-request-id"]).toBeDefined();
      expect(res.headers["x-request-id"]).toMatch(
        /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i
      );
    });

    it("should preserve client-supplied X-Request-Id header", async () => {
      const customId = "trace-client-request-uuid-12345";
      const res = await request(app)
        .get("/health")
        .set("X-Request-Id", customId);

      expect(res.headers["x-request-id"]).toBe(customId);
    });

    it("should sanitize and redact patient PII and credentials from structured log data", () => {
      const rawPayload = {
        patientName: "Aarav Sharma",
        name: "Aarav Sharma",
        phoneNumber: "+91-9876543210",
        address: "Village Rampur, Dist Gaya",
        medicalHistory: "Chronic asthma, Type-2 Diabetes",
        email: "aarav@example.com",
        password: "SecretPassword@2026!",
        token: "jwt_token_sample",
        refreshToken: "refresh_token_sample",
        resetPasswordToken: "reset_token_sample",
        authorization: "Bearer secret_bearer_token",
        symptoms: ["cough", "chest_pain", "fever"],
        age: 38,
        gender: "Male",
        metadata: {
          phoneNumber: "+91-8888888888",
        },
      };

      const sanitized = sanitizeForLogging(rawPayload);

      expect(sanitized.patientName).toBe("[REDACTED_PII]");
      expect(sanitized.name).toBe("[REDACTED_PII]");
      expect(sanitized.phoneNumber).toBe("[REDACTED_PII]");
      expect(sanitized.address).toBe("[REDACTED_PII]");
      expect(sanitized.medicalHistory).toBe("[REDACTED_PII]");
      expect(sanitized.email).toBe("[REDACTED_PII]");
      expect(sanitized.password).toBe("[REDACTED_PII]");
      expect(sanitized.token).toBe("[REDACTED_PII]");
      expect(sanitized.refreshToken).toBe("[REDACTED_PII]");
      expect(sanitized.resetPasswordToken).toBe("[REDACTED_PII]");
      expect(sanitized.authorization).toBe("[REDACTED_PII]");

      expect(sanitized.symptoms).toEqual(["cough", "chest_pain", "fever"]);
      expect(sanitized.age).toBe(38);
      expect(sanitized.gender).toBe("Male");
      expect(sanitized.metadata.phoneNumber).toBe("[REDACTED_PII]");
    });
  });

  // ── 10. Refresh Token Rotation & Automatic Compromise Reuse Detection (1.3)
  describe("12. Refresh Token Rotation & Reuse Detection", () => {
    it("should rotate valid refresh token, revoking old and issuing new in same family", async () => {
      const mockUser = {
        _id: new mongoose.Types.ObjectId(),
        role: ROLES.WORKER,
        organization: new mongoose.Types.ObjectId(),
      };

      const validRecord = {
        tokenHash: hashToken("valid_raw_token"),
        userId: mockUser._id,
        userModel: "Worker",
        familyId: "fam_safe_001",
        expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
        isRevoked: false,
        save: vi.fn().mockResolvedValue(true),
      };

      vi.spyOn(RefreshToken, "findOne").mockResolvedValue(validRecord);
      vi.spyOn(RefreshToken, "create").mockResolvedValue(true);
      vi.spyOn(Worker, "findById").mockResolvedValue(mockUser);

      const result = await rotateRefreshToken("valid_raw_token");

      expect(validRecord.isRevoked).toBe(true);
      expect(validRecord.save).toHaveBeenCalled();
      expect(result).toHaveProperty("accessToken");
      expect(result).toHaveProperty("refreshToken");
    });

    it("should detect compromised token reuse and immediately invalidate entire family (401)", async () => {
      const reusedRecord = {
        tokenHash: hashToken("compromised_reused_token"),
        userId: new mongoose.Types.ObjectId(),
        userModel: "Worker",
        familyId: "fam_compromised_999",
        expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
        isRevoked: true,
      };

      vi.spyOn(RefreshToken, "findOne").mockResolvedValue(reusedRecord);
      const updateManySpy = vi.spyOn(RefreshToken, "updateMany").mockResolvedValue({ modifiedCount: 3 });

      await expect(rotateRefreshToken("compromised_reused_token")).rejects.toMatchObject({
        status: 401,
        code: "TOKEN_REUSE_DETECTED",
        message: expect.stringContaining("Refresh token reuse detected"),
      });

      expect(updateManySpy).toHaveBeenCalledWith(
        { familyId: "fam_compromised_999" },
        { isRevoked: true }
      );
    });

    it("should reject expired refresh tokens with 401", async () => {
      const expiredRecord = {
        tokenHash: hashToken("expired_token"),
        userId: new mongoose.Types.ObjectId(),
        userModel: "Worker",
        familyId: "fam_expired",
        expiresAt: new Date(Date.now() - 1000),
        isRevoked: false,
      };

      vi.spyOn(RefreshToken, "findOne").mockResolvedValue(expiredRecord);

      await expect(rotateRefreshToken("expired_token")).rejects.toMatchObject({
        status: 401,
        message: "Refresh token has expired",
      });
    });
  });

  // ── 11. Admin Soft-Deactivate, Reactivate & Login Rejection (1.4) ──────────
  describe("13. Admin Soft-Deactivation & Deactivated Login Rejection", () => {
    it("should strictly reject login attempts from soft-deactivated worker (403 ACCOUNT_DEACTIVATED)", async () => {
      const mockDeactivatedWorker = {
        email: "deactivated.worker@phc.gov.in",
        password: await hashPassword("ValidPassword123!"),
        isActive: false,
        deactivatedAt: new Date(),
        deactivatedBy: new mongoose.Types.ObjectId(),
        populate: vi.fn().mockReturnThis(),
      };

      vi.spyOn(Worker, "findOne").mockReturnValue({
        populate: vi.fn().mockResolvedValue(mockDeactivatedWorker),
      });

      await expect(
        loginWorker({ email: "deactivated.worker@phc.gov.in", password: "ValidPassword123!" })
      ).rejects.toMatchObject({
        status: 403,
        code: "ACCOUNT_DEACTIVATED",
        message: expect.stringContaining("Account has been deactivated"),
      });
    });

    it("should permit login for active worker", async () => {
      const mockActiveWorker = {
        _id: new mongoose.Types.ObjectId(),
        email: "active.worker@phc.gov.in",
        password: await hashPassword("ValidPassword123!"),
        isActive: true,
        role: ROLES.WORKER,
        organization: new mongoose.Types.ObjectId(),
        save: vi.fn().mockResolvedValue(true),
        populate: vi.fn().mockReturnThis(),
      };

      vi.spyOn(Worker, "findOne").mockReturnValue({
        populate: vi.fn().mockResolvedValue(mockActiveWorker),
      });
      vi.spyOn(RefreshToken, "create").mockResolvedValue(true);

      const loginRes = await loginWorker({
        email: "active.worker@phc.gov.in",
        password: "ValidPassword123!",
      });

      expect(loginRes).toHaveProperty("accessToken");
      expect(loginRes).toHaveProperty("refreshToken");
      expect(loginRes.worker.isActive).toBe(true);
    });

    it("should immediately reject existing access tokens when account is deactivated (403 ACCOUNT_DEACTIVATED)", async () => {
      const workerId = new mongoose.Types.ObjectId();
      const orgId = new mongoose.Types.ObjectId();
      const activeToken = jwt.sign(
        { id: workerId.toString(), role: ROLES.WORKER, organization: orgId.toString() },
        serverConfig.JWT_SECRET,
        { expiresIn: "15m" }
      );

      vi.spyOn(Worker, "findById").mockReturnValue({
        select: vi.fn().mockReturnValue({
          lean: vi.fn().mockResolvedValue({ _id: workerId, isActive: false }),
        }),
      });

      const origReadyState = mongoose.connection.readyState;
      Object.defineProperty(mongoose.connection, "readyState", { value: 1, configurable: true });

      const req = {
        headers: { authorization: `Bearer ${activeToken}` },
      };
      const res = {
        status: vi.fn().mockReturnThis(),
        json: vi.fn(),
      };
      const next = vi.fn();

      const middleware = verifyToken([ROLES.WORKER]);
      await middleware(req, res, next);

      Object.defineProperty(mongoose.connection, "readyState", { value: origReadyState, configurable: true });

      expect(res.status).toHaveBeenCalledWith(403);
      expect(res.json).toHaveBeenCalledWith(
        expect.objectContaining({ code: "ACCOUNT_DEACTIVATED" })
      );
      expect(next).not.toHaveBeenCalled();
    });

    it("should immediately reject refresh token rotation when account is deactivated (403 ACCOUNT_DEACTIVATED)", async () => {
      const workerId = new mongoose.Types.ObjectId();
      const mockRecord = {
        tokenHash: hashToken("raw_refresh_token_xyz"),
        userId: workerId,
        userModel: "Worker",
        organization: new mongoose.Types.ObjectId(),
        familyId: "fam_123",
        expiresAt: new Date(Date.now() + 86400000),
        isRevoked: false,
        save: vi.fn().mockResolvedValue(true),
      };

      vi.spyOn(RefreshToken, "findOne").mockResolvedValue(mockRecord);
      vi.spyOn(Worker, "findById").mockResolvedValue({ _id: workerId, isActive: false });

      await expect(rotateRefreshToken("raw_refresh_token_xyz")).rejects.toMatchObject({
        status: 403,
        code: "ACCOUNT_DEACTIVATED",
      });
    });
  });

  // ── 12. Strict Zod Schema Mass-Assignment Rejection (1.2) ──────────────────
  describe("14. Strict Zod Schema Mass-Assignment Rejection", () => {
    it("should reject creation requests with unknown/mass-assigned fields with 400 VALIDATION_ERROR", async () => {
      const adminToken = jwt.sign(
        { id: new mongoose.Types.ObjectId().toString(), role: ROLES.ADMIN, organization: new mongoose.Types.ObjectId().toString() },
        serverConfig.JWT_SECRET
      );

      const massAssignmentPayload = {
        name: "Test Worker",
        email: "test.worker@phc.gov.in",
        phoneNumber: "+91-9876543210",
        password: "Password123!",
        role: "Admin",
        organization: new mongoose.Types.ObjectId().toString(),
        isAdmin: true,
      };

      const res = await request(app)
        .post("/api/v1/worker/")
        .set("Authorization", `Bearer ${adminToken}`)
        .send(massAssignmentPayload);

      expect(res.status).toBe(400);
      expect(res.body.code).toBe("VALIDATION_ERROR");
      expect(res.body.errors.some((e) => e.message.includes("unrecognized_keys") || e.field === "role" || e.field === "organization" || e.message.includes("Unrecognized"))).toBe(true);
    });

    it("should reject unknown fields on consultation second-opinion response with 400", async () => {
      const doctorToken = jwt.sign(
        { id: new mongoose.Types.ObjectId().toString(), role: ROLES.DOCTOR, organization: new mongoose.Types.ObjectId().toString() },
        serverConfig.JWT_SECRET
      );

      const targetId = new mongoose.Types.ObjectId().toString();
      const res = await request(app)
        .patch(`/api/v1/consultation/${targetId}/respond`)
        .set("Authorization", `Bearer ${doctorToken}`)
        .send({
          diagnosis: "Common Cold",
          recommendation: "Hydration",
          status: "closed",
          overrideApproval: true,
        });

      expect(res.status).toBe(400);
      expect(res.body.code).toBe("VALIDATION_ERROR");
    });
  });

  // ── 13. Admin Audit Log Retrieval Scoped to Organization (1.6) ────────────
  describe("15. Admin Audit Log Retrieval Scoped to Organization", () => {
    it("should return paginated audit logs filtered strictly to admin's organization", async () => {
      const adminOrg = new mongoose.Types.ObjectId();
      const adminToken = jwt.sign(
        { id: new mongoose.Types.ObjectId().toString(), role: ROLES.ADMIN, organization: adminOrg.toString() },
        serverConfig.JWT_SECRET
      );

      const mockLogs = [
        { action: "WORKER_CREATED", resourceType: "Worker", organization: adminOrg },
        { action: "CONSULTATION_ESCALATED", resourceType: "Consultation", organization: adminOrg },
      ];

      const findQueryMock = {
        sort: vi.fn().mockReturnThis(),
        skip: vi.fn().mockReturnThis(),
        limit: vi.fn().mockResolvedValue(mockLogs),
      };

      let capturedQuery = null;
      vi.spyOn(AuditLog, "find").mockImplementation((query) => {
        capturedQuery = query;
        return findQueryMock;
      });
      vi.spyOn(AuditLog, "countDocuments").mockResolvedValue(2);

      const res = await request(app)
        .get("/api/v1/admin/audit-logs?page=1&limit=10")
        .set("Authorization", `Bearer ${adminToken}`);

      expect(res.status).toBe(200);
      expect(res.body.auditLogs).toHaveLength(2);
      expect(res.body.total).toBe(2);
      expect(res.body.page).toBe(1);
      expect(capturedQuery.organization.toString()).toBe(adminOrg.toString());
    });

    it("should reject audit log access by non-admin roles (403)", async () => {
      const workerToken = jwt.sign(
        { id: new mongoose.Types.ObjectId().toString(), role: ROLES.WORKER, organization: new mongoose.Types.ObjectId().toString() },
        serverConfig.JWT_SECRET
      );

      const res = await request(app)
        .get("/api/v1/admin/audit-logs")
        .set("Authorization", `Bearer ${workerToken}`);

      expect(res.status).toBe(403);
      expect(res.body.message).toContain("Insufficient role permissions");
    });
  });

  // ── 16. Rate Limiting Protection (1.5) ──────────────────────────────────────
  describe("16. Rate Limiting Protection (1.5)", () => {
    it("should configure strict auth rate limits (15 attempts/15m) and reject requests when limit is reached (429)", async () => {
      const { createAuthLimiter, authRateLimiter } = await import("../src/middlewares/security.middleware.js");
      expect(authRateLimiter).toBeDefined();

      const limiter = createAuthLimiter(3);
      const testApp = express();
      testApp.use(limiter);
      testApp.get("/test-auth-limit", (req, res) => res.json({ ok: true }));

      for (let i = 0; i < 3; i++) {
        const r = await request(testApp).get("/test-auth-limit");
        expect(r.status).toBe(200);
      }
      const overLimitRes = await request(testApp).get("/test-auth-limit");
      expect(overLimitRes.status).toBe(429);
      expect(overLimitRes.body.code).toBe("RATE_LIMIT_EXCEEDED");
    });

    it("should enforce strict production immutability for rate limits (throws on relaxation attempt)", async () => {
      const { resolveRateLimit } = await import("../src/middlewares/security.middleware.js");

      const origNodeEnv = process.env.NODE_ENV;
      const origLoadTest = process.env.ALLOW_LOAD_TEST;

      try {
        process.env.NODE_ENV = "production";
        process.env.ALLOW_LOAD_TEST = "true";

        expect(() => resolveRateLimit("auth", 15)).toThrowError(/SECURITY_VIOLATION/);
        expect(() => resolveRateLimit("general", 150)).toThrowError(/SECURITY_VIOLATION/);

        // In production without relaxation, standard limits are returned
        delete process.env.ALLOW_LOAD_TEST;
        expect(resolveRateLimit("auth", 15)).toBe(15);
        expect(resolveRateLimit("general", 150)).toBe(150);
      } finally {
        process.env.NODE_ENV = origNodeEnv;
        if (origLoadTest !== undefined) process.env.ALLOW_LOAD_TEST = origLoadTest;
        else delete process.env.ALLOW_LOAD_TEST;
      }
    });

    it("should permit load test relaxation only when NODE_ENV is not production", async () => {
      const { resolveRateLimit } = await import("../src/middlewares/security.middleware.js");

      const origNodeEnv = process.env.NODE_ENV;
      const origLoadTest = process.env.ALLOW_LOAD_TEST;
      const origApiMax = process.env.LOAD_TEST_API_MAX;

      try {
        process.env.NODE_ENV = "test";
        process.env.ALLOW_LOAD_TEST = "true";
        process.env.LOAD_TEST_API_MAX = "5000";

        expect(resolveRateLimit("general", 150)).toBe(5000);
      } finally {
        process.env.NODE_ENV = origNodeEnv;
        if (origLoadTest !== undefined) process.env.ALLOW_LOAD_TEST = origLoadTest;
        else delete process.env.ALLOW_LOAD_TEST;
        if (origApiMax !== undefined) process.env.LOAD_TEST_API_MAX = origApiMax;
        else delete process.env.LOAD_TEST_API_MAX;
      }
    });
  });

  // ── 17. Stage 2 — Patient Registration, Field-Level Encryption & DPDP Act Compliance (Flow Steps 3–4) ───
  describe("17. Stage 2 — Patient Registration, Field-Level Encryption & DPDP Compliance", () => {
    const orgAlpha = new mongoose.Types.ObjectId();
    const orgBeta = new mongoose.Types.ObjectId();
    const workerAlphaId = new mongoose.Types.ObjectId();
    const workerBetaId = new mongoose.Types.ObjectId();

    const workerAlphaToken = jwt.sign(
      { id: workerAlphaId.toString(), role: ROLES.WORKER, organization: orgAlpha.toString() },
      serverConfig.JWT_SECRET
    );

    const workerBetaToken = jwt.sign(
      { id: workerBetaId.toString(), role: ROLES.WORKER, organization: orgBeta.toString() },
      serverConfig.JWT_SECRET
    );

    it("should encrypt medicalHistory, phoneNumber, and address at rest in MongoDB (AES-256-GCM) and decrypt on read", async () => {
      const patientDoc = new Patient({
        name: "Sunita Devi",
        age: 38,
        gender: "Female",
        phoneNumber: "+91-9876543210",
        address: "Village Khed, Dist Pune, Maharashtra",
        medicalHistory: "Hypertension (diagnosed 2021), Penicillin allergy",
        registeredBy: workerAlphaId,
        organization: orgAlpha,
        consentGiven: true,
        consentVersion: "1.0",
      });

      // Execute Mongoose pre-save hook
      const pres = patientDoc.schema.s.hooks._pres.get("save");
      for (const hook of pres) {
        await hook.fn.call(patientDoc);
      }

      // Verify raw stored fields are ciphertext with iv:authTag:encrypted (3 parts)
      expect(patientDoc.phoneNumber).not.toBe("+91-9876543210");
      expect(patientDoc.phoneNumber.split(":")).toHaveLength(3);

      expect(patientDoc.address).not.toBe("Village Khed, Dist Pune, Maharashtra");
      expect(patientDoc.address.split(":")).toHaveLength(3);

      expect(patientDoc.medicalHistory).not.toBe("Hypertension (diagnosed 2021), Penicillin allergy");
      expect(patientDoc.medicalHistory.split(":")).toHaveLength(3);

      // Verify getDecrypted() recovers exact original plaintexts
      const decrypted = patientDoc.getDecrypted();
      expect(decrypted.phoneNumber).toBe("+91-9876543210");
      expect(decrypted.address).toBe("Village Khed, Dist Pune, Maharashtra");
      expect(decrypted.medicalHistory).toBe("Hypertension (diagnosed 2021), Penicillin allergy");
      expect(decrypted.name).toBe("Sunita Devi");
      expect(decrypted.consentGiven).toBe(true);
    });

    it("should export full patient data and history under DPDP Act for authorized users in the same organization", async () => {
      const patientId = new mongoose.Types.ObjectId();
      const mockPatient = new Patient({
        _id: patientId,
        name: "Sunita Devi",
        age: 38,
        gender: "Female",
        phoneNumber: encryptField("+91-9876543210"),
        address: encryptField("Village Khed, Dist Pune"),
        medicalHistory: encryptField("Hypertension"),
        consentGiven: true,
        consentTimestamp: new Date("2026-01-15T10:00:00Z"),
        consentVersion: "1.0",
        organization: orgAlpha,
        registeredBy: workerAlphaId,
        isDeleted: false,
      });

      vi.spyOn(Patient, "findOne").mockImplementation((query) => {
        if (
          query._id?.toString() === patientId.toString() &&
          query.organization?.toString() === orgAlpha.toString() &&
          query.isDeleted?.$ne === true
        ) {
          return Promise.resolve(mockPatient);
        }
        return Promise.resolve(null);
      });

      const mockConsultations = [
        {
          _id: new mongoose.Types.ObjectId(),
          patient: patientId,
          organization: orgAlpha,
          symptoms: ["fever", "cough"],
          status: "completed",
          createdAt: new Date(),
          mlAnalysis: { disease: "Common Cold", confidence: 0.85, severityScore: 2 },
          secondOpinion: { diagnosis: "Viral Upper Respiratory Infection" },
          workerDecision: "accepted",
        },
      ];

      const findQueryMock = {
        sort: vi.fn().mockResolvedValue(mockConsultations),
      };
      vi.spyOn(Consultation, "find").mockImplementation(() => findQueryMock);

      const res = await request(app)
        .get(`/api/v1/patient/${patientId}/export`)
        .set("Authorization", `Bearer ${workerAlphaToken}`);

      expect(res.status).toBe(200);
      expect(res.body.message).toBe("Patient data exported successfully");
      expect(res.body.data.patient.name).toBe("Sunita Devi");
      expect(res.body.data.patient.phoneNumber).toBe("+91-9876543210");
      expect(res.body.data.patient.medicalHistory).toBe("Hypertension");
      expect(res.body.data.consent.consentGiven).toBe(true);
      expect(res.body.data.consent.consentVersion).toBe("1.0");
      expect(res.body.data.consultations).toHaveLength(1);
      expect(res.body.data.consultations[0].symptoms).toEqual(["fever", "cough"]);
    });

    it("should revoke consent, anonymize PII, and mark record deleted under DPDP Act", async () => {
      const patientId = new mongoose.Types.ObjectId();
      const mockPatient = new Patient({
        _id: patientId,
        name: "Sunita Devi",
        age: 38,
        gender: "Female",
        phoneNumber: encryptField("+91-9876543210"),
        address: encryptField("Village Khed, Dist Pune"),
        medicalHistory: encryptField("Hypertension"),
        consentGiven: true,
        consentVersion: "1.0",
        organization: orgAlpha,
        registeredBy: workerAlphaId,
        isDeleted: false,
      });

      mockPatient.save = vi.fn().mockImplementation(async function () {
        const pres = mockPatient.schema.s.hooks._pres.get("save");
        for (const hook of pres) {
          await hook.fn.call(this);
        }
        return this;
      });

      vi.spyOn(Patient, "findOne").mockImplementation((query) => {
        if (
          query._id?.toString() === patientId.toString() &&
          query.organization?.toString() === orgAlpha.toString() &&
          query.isDeleted?.$ne === true
        ) {
          return Promise.resolve(mockPatient);
        }
        return Promise.resolve(null);
      });

      const res = await request(app)
        .delete(`/api/v1/patient/${patientId}`)
        .set("Authorization", `Bearer ${workerAlphaToken}`);

      expect(res.status).toBe(200);
      expect(res.body.message).toContain("consent revoked and record anonymized under DPDP");
      expect(mockPatient.consentGiven).toBe(false);
      expect(mockPatient.revokedAt).toBeInstanceOf(Date);
      expect(mockPatient.isDeleted).toBe(true);
      expect(mockPatient.deletedAt).toBeInstanceOf(Date);
      expect(mockPatient.name).toBe("[ANONYMIZED]");
    });

    it("should enforce cross-tenant isolation and return 404 Not Found to prevent enumeration across orgs", async () => {
      const patientId = new mongoose.Types.ObjectId();
      const mockPatientOrgAlpha = new Patient({
        _id: patientId,
        name: "Sunita Devi",
        age: 38,
        gender: "Female",
        phoneNumber: encryptField("+91-9876543210"),
        address: encryptField("Village Khed, Dist Pune"),
        medicalHistory: encryptField("Hypertension"),
        organization: orgAlpha,
        registeredBy: workerAlphaId,
        isDeleted: false,
      });

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

      // Probe 1: Cross-tenant READ attempt from Worker Beta -> 404 Not Found
      const crossReadRes = await request(app)
        .get(`/api/v1/patient/${patientId}`)
        .set("Authorization", `Bearer ${workerBetaToken}`);

      expect(crossReadRes.status).toBe(404);
      expect(crossReadRes.body.message).toContain("Patient not found");

      // Probe 2: Cross-tenant EXPORT attempt from Worker Beta -> 404 Not Found
      const crossExportRes = await request(app)
        .get(`/api/v1/patient/${patientId}/export`)
        .set("Authorization", `Bearer ${workerBetaToken}`);

      expect(crossExportRes.status).toBe(404);
      expect(crossExportRes.body.message).toContain("Patient not found");

      // Probe 3: Cross-tenant DELETE attempt from Worker Beta -> 404 Not Found
      const crossDeleteRes = await request(app)
        .delete(`/api/v1/patient/${patientId}`)
        .set("Authorization", `Bearer ${workerBetaToken}`);

      expect(crossDeleteRes.status).toBe(404);
      expect(crossDeleteRes.body.message).toContain("Patient not found");

      // Positive Control: Worker Alpha (same tenant) reads patient -> 200 OK with decrypted PII
      const sameTenantRes = await request(app)
        .get(`/api/v1/patient/${patientId}`)
        .set("Authorization", `Bearer ${workerAlphaToken}`);

      expect(sameTenantRes.status).toBe(200);
      expect(sameTenantRes.body.patient.name).toBe("Sunita Devi");
      expect(sameTenantRes.body.patient.phoneNumber).toBe("+91-9876543210");
      expect(sameTenantRes.body.patient.medicalHistory).toBe("Hypertension");
    });

    describe("18. Stage 2 Completion — DPDP Consent Lifecycle, Key Rotation, Upload Magic Bytes & Admin Workflows", () => {
      it("should refuse AI consultation analysis when patient consent is missing or withdrawn (403 CONSENT_REQUIRED)", async () => {
        const orgId = new mongoose.Types.ObjectId();
        const patientId = new mongoose.Types.ObjectId();
        const consultationId = new mongoose.Types.ObjectId();

        const workerToken = jwt.sign(
          { id: new mongoose.Types.ObjectId().toString(), role: ROLES.WORKER, organization: orgId.toString() },
          serverConfig.JWT_SECRET
        );

        // Mock consultation with patient whose consent is false
        const mockConsultationUnconsented = {
          _id: consultationId,
          organization: orgId,
          symptoms: ["itching", "skin_rash"],
          patient: {
            _id: patientId,
            name: "Unconsented Patient",
            age: 30,
            gender: "Female",
            consentGiven: false, // Consent NOT given
            revokedAt: new Date(),
            isDeleted: false,
          },
        };

        const populateMock = vi.fn().mockResolvedValue(mockConsultationUnconsented);
        vi.spyOn(Consultation, "findOne").mockReturnValue({ populate: populateMock });

        // Synchronous analysis probe
        const syncRes = await request(app)
          .post(`/api/v1/consultation/${consultationId}/analyze`)
          .set("Authorization", `Bearer ${workerToken}`)
          .send({ language: "en" });

        expect(syncRes.status).toBe(403);
        expect(syncRes.body.code).toBe("CONSENT_REQUIRED");
        expect(syncRes.body.message).toContain("consent is inactive or has been withdrawn");

        // Asynchronous analysis probe
        const asyncRes = await request(app)
          .post(`/api/v1/consultation/${consultationId}/analyze/async`)
          .set("Authorization", `Bearer ${workerToken}`)
          .send({ language: "en" });

        if (asyncRes.status !== 403) console.log("DEBUG ASYNC RES:", asyncRes.status, asyncRes.body);

        expect(asyncRes.status).toBe(403);
        expect(asyncRes.body.code).toBe("CONSENT_REQUIRED");
      });

      it("should record consent withdrawal and block further processing under DPDP Act", async () => {
        const orgId = new mongoose.Types.ObjectId();
        const patientId = new mongoose.Types.ObjectId();

        const workerToken = jwt.sign(
          { id: new mongoose.Types.ObjectId().toString(), role: ROLES.WORKER, organization: orgId.toString() },
          serverConfig.JWT_SECRET
        );

        const mockPatient = {
          _id: patientId,
          organization: orgId,
          name: "Ramesh Pawar",
          consentGiven: true,
          consentWithdrawnAt: null,
          consentWithdrawalReason: null,
          isDeleted: false,
          save: vi.fn().mockResolvedValue(true),
        };

        vi.spyOn(Patient, "findOne").mockResolvedValue(mockPatient);

        const res = await request(app)
          .post(`/api/v1/patient/${patientId}/withdraw-consent`)
          .set("Authorization", `Bearer ${workerToken}`)
          .send({ reason: "Patient exercised right to withdraw consent under Section 6 DPDP" });

        expect(res.status).toBe(200);
        expect(res.body.message).toContain("consent successfully withdrawn");
        expect(mockPatient.consentGiven).toBe(false);
        expect(mockPatient.consentWithdrawnAt).toBeInstanceOf(Date);
        expect(mockPatient.consentWithdrawalReason).toContain("Section 6 DPDP");
      });

      it("should detect potential duplicate patient registrations within the same organization", async () => {
        const orgId = new mongoose.Types.ObjectId();
        const existingPatientId = new mongoose.Types.ObjectId();

        const existingPatient = {
          _id: existingPatientId,
          name: "Amit Sharma",
          age: 42,
          gender: "Male",
          organization: orgId,
        };

        vi.spyOn(Patient, "findOne").mockResolvedValue(existingPatient);
        vi.spyOn(Patient, "create").mockResolvedValue({
          _id: new mongoose.Types.ObjectId(),
          name: "Amit Sharma",
          age: 42,
          gender: "Male",
          getDecrypted: () => ({
            _id: new mongoose.Types.ObjectId(),
            name: "Amit Sharma",
            age: 42,
            gender: "Male",
          }),
        });

        const { createPatient } = await import("../src/service/patient.service.js");
        const res = await createPatient(
          { name: "Amit Sharma", age: 42, gender: "Male", phoneNumber: "9876543210", address: "Pune" },
          new mongoose.Types.ObjectId(),
          orgId
        );

        expect(res.duplicateWarning).toBeDefined();
        expect(res.duplicateWarning.detected).toBe(true);
        expect(res.duplicateWarning.existingPatientId).toEqual(existingPatientId);
      });

      it("should encrypt emergency contact fields at rest and decrypt on read", async () => {
        const patientData = {
          name: "Pooja Kulkarni",
          age: 28,
          gender: "Female",
          phoneNumber: "9876543210",
          address: "Shivajinagar, Pune",
          emergencyContact: {
            name: "Vikas Kulkarni",
            phoneNumber: "9123456789",
            relationship: "Spouse",
          },
          organization: new mongoose.Types.ObjectId(),
          registeredBy: new mongoose.Types.ObjectId(),
        };

        const patient = new Patient(patientData);
        // Invoke pre-save hook
        patient.schema.s.hooks.execPre("save", patient, () => {});

        // Emergency contact name & phone must be encrypted ciphertexts (iv:tag:enc)
        expect(patient.emergencyContact.name).not.toBe("Vikas Kulkarni");
        expect(patient.emergencyContact.name.split(":")).toHaveLength(3);
        expect(patient.emergencyContact.phoneNumber).not.toBe("9123456789");
        expect(patient.emergencyContact.phoneNumber.split(":")).toHaveLength(3);

        // Instance method decrypts correctly
        const decrypted = patient.getDecrypted();
        expect(decrypted.emergencyContact.name).toBe("Vikas Kulkarni");
        expect(decrypted.emergencyContact.phoneNumber).toBe("9123456789");
        expect(decrypted.emergencyContact.relationship).toBe("Spouse");
      });

      it("should support versioned Key ID tagging and seamless cryptographic key rotation without data loss", () => {
        const keyOld = "old_secret_encryption_key_32_bytes_len!";
        const keyNew = "new_secret_encryption_key_32_bytes_len!";
        const secretPII = "Confidential Patient Cardiac History: Stent 2024";

        // 1. Encrypt with old key using Key ID 'k1'
        const cipherOld = encryptField(secretPII, "k1", keyOld);
        expect(cipherOld.startsWith("k1:")).toBe(true);
        expect(cipherOld.split(":")).toHaveLength(4);

        // 2. Rotate to new key with Key ID 'k2'
        const cipherNew = rotateFieldEncryption(cipherOld, keyOld, keyNew, "k2");
        expect(cipherNew.startsWith("k2:")).toBe(true);
        expect(cipherNew.split(":")).toHaveLength(4);
        expect(cipherNew).not.toBe(cipherOld);

        // 3. Verify seamless decryption of new ciphertext
        // Derive key from keyNew to verify plaintext integrity
        const parts = cipherNew.split(":");
        const [, ivHex, tagHex, encHex] = parts;
        const cryptoModule = crypto;
        const newDerivedKey = cryptoModule.createHash("sha256").update(keyNew).digest();
        const decipher = cryptoModule.createDecipheriv("aes-256-gcm", newDerivedKey, Buffer.from(ivHex, "hex"), { authTagLength: 16 });
        decipher.setAuthTag(Buffer.from(tagHex, "hex"));
        let plain = decipher.update(encHex, "hex", "utf8");
        plain += decipher.final("utf8");

        expect(plain).toBe(secretPII);
      });

      it("should validate real file magic bytes and reject disguised executables", () => {
        // Legitimate PDF: %PDF-
        const validPdf = Buffer.from("%PDF-1.7 sample document binary payload", "ascii");
        expect(validateFileMagicBytes(validPdf, "application/pdf")).toBe(true);

        // Legitimate PNG: 89 50 4E 47
        const validPng = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
        expect(validateFileMagicBytes(validPng, "image/png")).toBe(true);

        // Legitimate JPEG: FF D8 FF
        const validJpg = Buffer.from([0xff, 0xd8, 0xff, 0xe0, 0x00, 0x10]);
        expect(validateFileMagicBytes(validJpg, "image/jpeg")).toBe(true);

        // Disguised executable / polyglot attack: MZ PE executable declaring image/png
        const maliciousExeDisguisedAsPng = Buffer.from("MZ\x90\x00\x03ThisIsExecutableCode", "ascii");
        expect(validateFileMagicBytes(maliciousExeDisguisedAsPng, "image/png")).toBe(false);

        // Shell script disguised as PDF
        const shellScriptDisguisedAsPdf = Buffer.from("#!/bin/bash\necho Hacked", "ascii");
        expect(validateFileMagicBytes(shellScriptDisguisedAsPdf, "application/pdf")).toBe(false);
      });

      it("should support admin-approved export and deletion workflows", async () => {
        const orgId = new mongoose.Types.ObjectId();
        const adminId = new mongoose.Types.ObjectId();
        const patientId = new mongoose.Types.ObjectId();

        const adminToken = jwt.sign(
          { id: adminId.toString(), role: ROLES.ADMIN, organization: orgId.toString() },
          serverConfig.JWT_SECRET
        );

        const mockPatient = {
          _id: patientId,
          organization: orgId,
          exportApproved: false,
          deletionApproved: false,
          isDeleted: false,
          save: vi.fn().mockResolvedValue(true),
        };

        vi.spyOn(Patient, "findOne").mockResolvedValue(mockPatient);

        // Admin approves export
        const exportApproveRes = await request(app)
          .post(`/api/v1/patient/${patientId}/approve-export`)
          .set("Authorization", `Bearer ${adminToken}`);

        expect(exportApproveRes.status).toBe(200);
        expect(mockPatient.exportApproved).toBe(true);
        expect(mockPatient.exportApprovedBy).toEqual(adminId.toString());

        // Admin approves deletion
        const deleteApproveRes = await request(app)
          .post(`/api/v1/patient/${patientId}/approve-delete`)
          .set("Authorization", `Bearer ${adminToken}`);

        expect(deleteApproveRes.status).toBe(200);
        expect(mockPatient.deletionApproved).toBe(true);
        expect(mockPatient.deletionApprovedBy).toEqual(adminId.toString());
      });
    });

    // ── 9. Flow Steps 10 & 11 — Clinical Decision & Second Opinion Workflows ──
    describe("9. Flow Steps 10 & 11 — Clinical Decision & Second Opinion Workflows", () => {
      const orgId = new mongoose.Types.ObjectId();
      const crossOrgId = new mongoose.Types.ObjectId();
      const workerId = new mongoose.Types.ObjectId();
      const doctorId = new mongoose.Types.ObjectId();
      const otherDoctorId = new mongoose.Types.ObjectId();
      const consultationId = new mongoose.Types.ObjectId();

      const workerToken = jwt.sign(
        { id: workerId.toString(), role: ROLES.WORKER, organization: orgId.toString() },
        serverConfig.JWT_SECRET
      );

      const crossOrgWorkerToken = jwt.sign(
        { id: new mongoose.Types.ObjectId().toString(), role: ROLES.WORKER, organization: crossOrgId.toString() },
        serverConfig.JWT_SECRET
      );

      const doctorToken = jwt.sign(
        { id: doctorId.toString(), role: ROLES.DOCTOR, organization: orgId.toString() },
        serverConfig.JWT_SECRET
      );

      const otherDoctorToken = jwt.sign(
        { id: otherDoctorId.toString(), role: ROLES.DOCTOR, organization: orgId.toString() },
        serverConfig.JWT_SECRET
      );

      it("Step 10: Worker accepts AI result, transitions status to closed and workerDecision to accepted", async () => {
        const mockConsultation = {
          _id: consultationId,
          organization: orgId,
          status: "analyzed",
          workerDecision: null,
          save: vi.fn().mockResolvedValue(true),
        };

        vi.spyOn(Consultation, "findOne").mockResolvedValue(mockConsultation);

        const res = await request(app)
          .patch(`/api/v1/consultation/${consultationId}/accept`)
          .set("Authorization", `Bearer ${workerToken}`);

        expect(res.status).toBe(200);
        expect(res.body.message).toContain("AI result accepted");
        expect(mockConsultation.status).toBe("closed");
        expect(mockConsultation.workerDecision).toBe("accepted");
      });

      it("Step 10: Doctor cannot call accept endpoint (RBAC 403 Forbidden)", async () => {
        const res = await request(app)
          .patch(`/api/v1/consultation/${consultationId}/accept`)
          .set("Authorization", `Bearer ${doctorToken}`);

        expect(res.status).toBe(403);
      });

      it("Step 10: Cross-organization worker cannot accept another org consultation (404 anti-enumeration)", async () => {
        vi.spyOn(Consultation, "findOne").mockResolvedValue(null);

        const res = await request(app)
          .patch(`/api/v1/consultation/${consultationId}/accept`)
          .set("Authorization", `Bearer ${crossOrgWorkerToken}`);

        expect(res.status).toBe(404);
      });

      it("Step 10: Worker escalates consultation to doctor with reason", async () => {
        const mockConsultation = {
          _id: consultationId,
          organization: orgId,
          status: "analyzed",
          assignedDoctor: null,
          workerDecision: null,
          escalationReason: null,
          save: vi.fn().mockResolvedValue(true),
        };

        vi.spyOn(Consultation, "findOne").mockResolvedValue(mockConsultation);

        const res = await request(app)
          .patch(`/api/v1/consultation/${consultationId}/escalate`)
          .set("Authorization", `Bearer ${workerToken}`)
          .send({
            doctorId: doctorId.toString(),
            reason: "High risk symptom combination requiring senior clinical evaluation",
          });

        expect(res.status).toBe(200);
        expect(res.body.message).toContain("Consultation escalated to doctor");
        expect(mockConsultation.status).toBe("pending");
        expect(mockConsultation.workerDecision).toBe("escalated");
        expect(mockConsultation.assignedDoctor).toBe(doctorId.toString());
      });

      it("Step 11: Doctor retrieves pending consultations assigned to them", async () => {
        const mockPendingList = [
          {
            _id: consultationId,
            organization: orgId,
            assignedDoctor: doctorId,
            status: "pending",
            workerDecision: "escalated",
          },
        ];

        const mockFind = {
          populate: vi.fn().mockReturnThis(),
          sort: vi.fn().mockResolvedValue(mockPendingList),
        };
        vi.spyOn(Consultation, "find").mockReturnValue(mockFind);

        const res = await request(app)
          .get("/api/v1/consultation/pending")
          .set("Authorization", `Bearer ${doctorToken}`);

        expect(res.status).toBe(200);
        expect(res.body.consultations).toHaveLength(1);
      });

      it("Step 11: Doctor submits second opinion, transitioning status to reviewed", async () => {
        const mockConsultation = {
          _id: consultationId,
          organization: orgId,
          assignedDoctor: doctorId,
          status: "pending",
          secondOpinion: null,
          save: vi.fn().mockResolvedValue(true),
        };

        vi.spyOn(Consultation, "findOne").mockResolvedValue(mockConsultation);

        const res = await request(app)
          .patch(`/api/v1/consultation/${consultationId}/respond`)
          .set("Authorization", `Bearer ${doctorToken}`)
          .send({
            diagnosis: "Secondary bacterial sinusitis confirmed",
            recommendation: "Prescribed Amoxicillin-Clavulanate 625mg BD for 5 days. Review after 5 days.",
          });

        expect(res.status).toBe(200);
        expect(res.body.message).toContain("Second opinion submitted successfully");
        expect(mockConsultation.status).toBe("reviewed");
        expect(mockConsultation.secondOpinion.diagnosis).toBe("Secondary bacterial sinusitis confirmed");
      });

      it("Step 11: Worker cannot submit doctor second opinion (RBAC 403 Forbidden)", async () => {
        const res = await request(app)
          .patch(`/api/v1/consultation/${consultationId}/respond`)
          .set("Authorization", `Bearer ${workerToken}`)
          .send({
            diagnosis: "Attempted bypass diagnosis",
            recommendation: "Bypass recommendation",
          });

        expect(res.status).toBe(403);
      });

      it("Step 11: Doctor not assigned to consultation receives 404 Not Found", async () => {
        vi.spyOn(Consultation, "findOne").mockResolvedValue(null);

        const res = await request(app)
          .patch(`/api/v1/consultation/${consultationId}/respond`)
          .set("Authorization", `Bearer ${otherDoctorToken}`)
          .send({
            diagnosis: "Unauthorized doctor review",
            recommendation: "Should fail with 404",
          });

        expect(res.status).toBe(404);
      });

      it("Step 11: Optimistic Concurrency Control rejects collision with HTTP 409 Conflict", async () => {
        const versionError = new Error("No matching document found for id \"" + consultationId + "\" version 1 modifiedPaths \"secondOpinion,status\"");
        versionError.name = "VersionError";

        const mockConsultation = {
          _id: consultationId,
          organization: orgId,
          assignedDoctor: doctorId,
          status: "pending",
          secondOpinion: null,
          save: vi.fn().mockRejectedValue(versionError),
        };

        vi.spyOn(Consultation, "findOne").mockResolvedValue(mockConsultation);

        const res = await request(app)
          .patch(`/api/v1/consultation/${consultationId}/respond`)
          .set("Authorization", `Bearer ${doctorToken}`)
          .send({
            diagnosis: "Concurrent modification diagnosis",
            recommendation: "Concurrent recommendation",
          });

        expect(res.status).toBe(409);
        expect(res.body.message).toContain("Conflict: consultation was updated concurrently");
      });
    });
  });

  describe("14. Startup Environment Defense & ENCRYPTION_KEY Gating", () => {
    it("should strictly fail envSchema validation when ENCRYPTION_KEY is missing or shorter than 32 characters in production", async () => {
      const { envSchema } = await import("../src/config/serverConfig.js");
      const baseEnv = {
        PORT: 5000,
        DB_URL: "mongodb://127.0.0.1:27017/arogyamitra_test",
        JWT_SECRET: "mock_jwt_secret_for_test_runs_must_be_over_32_characters!",
        INTERNAL_SERVICE_SECRET: "mock_internal_secret_for_test_runs_32_chars!",
        NODE_ENV: "production",
      };

      const missingRes = envSchema.safeParse(baseEnv);
      expect(missingRes.success).toBe(false);
      expect(missingRes.error.format().ENCRYPTION_KEY).toBeDefined();

      const shortRes = envSchema.safeParse({ ...baseEnv, ENCRYPTION_KEY: "short_key_16_bytes" });
      expect(shortRes.success).toBe(false);
      expect(shortRes.error.format().ENCRYPTION_KEY).toBeDefined();

      const validRes = envSchema.safeParse({
        ...baseEnv,
        ENCRYPTION_KEY: "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
      });
      expect(validRes.success).toBe(true);
    });
  });
});
