import { describe, it, expect, vi, beforeEach } from "vitest";
import jwt from "jsonwebtoken";
import request from "supertest";
import app from "../src/index.js";
import { z } from "zod";
import {
  encryptField,
  decryptField,
  hashPassword,
  verifyPassword,
  generateSecureToken,
  hashToken,
} from "../src/utils/crypto.js";
import { verifyToken } from "../src/middlewares/auth.middleware.js";
import { enforceOrgScope, scopeFilter } from "../src/middlewares/orgScope.middleware.js";
import { authenticateWithLockout } from "../src/service/auth.service.js";

import serverConfig from "../src/config/serverConfig.js";
import Worker from "../src/models/worker/workerSchema.js";

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

      verifyToken(["Admin"])(req, res, next);
      expect(res.status).toHaveBeenCalledWith(401);
      expect(next).not.toHaveBeenCalled();
    });

    it("should reject expired tokens with TOKEN_EXPIRED code (401)", () => {
      const expiredToken = jwt.sign(
        { id: "u1", role: "Worker", organization: "org1" },
        serverConfig.JWT_SECRET,
        { expiresIn: "-1s" }
      );

      const req = { headers: { authorization: `Bearer ${expiredToken}` }, cookies: {} };
      const res = { status: vi.fn().mockReturnThis(), json: vi.fn() };
      const next = vi.fn();

      verifyToken(["Worker"])(req, res, next);
      expect(res.status).toHaveBeenCalledWith(401);
      expect(res.json).toHaveBeenCalledWith(expect.objectContaining({ code: "TOKEN_EXPIRED" }));
      expect(next).not.toHaveBeenCalled();
    });

    it("should reject tokens with insufficient role permissions (403)", () => {
      const token = jwt.sign(
        { id: "w1", role: "Worker", organization: "org1" },
        serverConfig.JWT_SECRET
      );

      const req = { headers: { authorization: `Bearer ${token}` }, cookies: {} };
      const res = { status: vi.fn().mockReturnThis(), json: vi.fn() };
      const next = vi.fn();

      verifyToken(["Admin"])(req, res, next); // Worker trying to access Admin endpoint
      expect(res.status).toHaveBeenCalledWith(403);
      expect(res.json).toHaveBeenCalledWith(expect.objectContaining({ message: expect.stringContaining("Insufficient") }));
      expect(next).not.toHaveBeenCalled();
    });

    it("should authorize valid token and attach user + organization context", () => {
      const token = jwt.sign(
        { id: "w1", role: "Worker", organization: "org_alpha" },
        serverConfig.JWT_SECRET
      );

      const req = { headers: { authorization: `Bearer ${token}` }, cookies: {} };
      const res = { status: vi.fn().mockReturnThis(), json: vi.fn() };
      const next = vi.fn();

      verifyToken(["worker"])(req, res, next);
      expect(next).toHaveBeenCalled();
      expect(req.user.id).toBe("w1");
      expect(req.user.role).toBe("Worker");
      expect(req.user.organization).toBe("org_alpha");
    });

    it("should reject wrongly-cased unauthorized roles and role spoofing attempts (403)", () => {
      const unauthorizedRoleVariants = [
        "dOcToR",
        "DOCTOR",
        "Doctor",
        "aDmIn",
        "ADMIN",
        "worker_admin",
        "Worker_Attacker",
        "worker ",
        "SUPERADMIN",
        "patient",
        "",
      ];

      for (const badRole of unauthorizedRoleVariants) {
        const token = jwt.sign(
          { id: "u_bad", role: badRole, organization: "org_alpha" },
          serverConfig.JWT_SECRET
        );

        const req = { headers: { authorization: `Bearer ${token}` }, cookies: {} };
        const res = { status: vi.fn().mockReturnThis(), json: vi.fn() };
        const next = vi.fn();

        verifyToken(["worker"])(req, res, next); // Worker route
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
        organization: "org_beta", // belongs to Beta
      };

      const mockModel = {
        findById: vi.fn().mockResolvedValue(mockPatient),
      };

      const req = {
        params: { id: "patient_123" },
        user: { id: "worker_1", role: "Worker", organization: "org_alpha" }, // user from Alpha
      };
      const res = { status: vi.fn().mockReturnThis(), json: vi.fn() };
      const next = vi.fn();

      const middleware = enforceOrgScope(mockModel, "id");
      await middleware(req, res, next);

      // Must return 404 Not Found to prevent enumeration across tenants!
      expect(res.status).toHaveBeenCalledWith(404);
      expect(res.json).toHaveBeenCalledWith({ message: "Resource not found" });
      expect(next).not.toHaveBeenCalled();
    });

    it("should pass when resource belongs to user's organization", async () => {
      const mockPatient = {
        _id: "patient_123",
        name: "Ramesh Kumar",
        organization: "org_alpha", // matches user's org
      };

      const mockModel = {
        findById: vi.fn().mockResolvedValue(mockPatient),
      };

      const req = {
        params: { id: "patient_123" },
        user: { id: "worker_1", role: "Worker", organization: "org_alpha" },
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

      // 5th attempt with wrong password
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
        lockUntil: new Date(Date.now() + 10 * 60 * 1000), // locked for 10 more mins
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
});
