import express from "express";
import {
  register,
  login,
  refreshSession,
  forgotPassword,
  resetPassword,
  logout,
  getProfile,
  getAuditLogs,
  downloadConsultationsCsv,
  getActiveSessions,
  revokeSession,
} from "../controller/admin.controller.js";
import verifyToken from "../middlewares/auth.middleware.js";
import { authRateLimiter } from "../middlewares/security.middleware.js";
import { validate } from "../middlewares/validate.middleware.js";
import {
  loginSchema,
  refreshSchema,
  forgotPasswordSchema,
  resetPasswordSchema,
  logoutSchema,
  auditLogsQuerySchema,
  idParamSchema,
} from "../validators/schemas.js";
import ROLES from "../config/roles.js";

const adminRouter = express.Router();

// Public auth routes (rate limited + zod validated)
adminRouter.post("/register", register); // Returns 403 disabled
adminRouter.post("/login", authRateLimiter, validate(loginSchema), login);
adminRouter.post("/refresh-token", validate(refreshSchema), refreshSession);
adminRouter.post("/forgot-password", authRateLimiter, validate(forgotPasswordSchema), forgotPassword);
adminRouter.post("/reset-password", authRateLimiter, validate(resetPasswordSchema), resetPassword);

// Protected routes (Admin only)
adminRouter.post("/logout", verifyToken([ROLES.ADMIN]), validate(logoutSchema), logout);
adminRouter.get("/profile", verifyToken([ROLES.ADMIN]), getProfile);
adminRouter.get("/audit-logs", verifyToken([ROLES.ADMIN]), validate(auditLogsQuerySchema, "query"), getAuditLogs);
adminRouter.get("/consultations/export-csv", verifyToken([ROLES.ADMIN]), downloadConsultationsCsv);
adminRouter.get("/sessions", verifyToken([ROLES.ADMIN]), getActiveSessions);
adminRouter.delete("/sessions/:id", verifyToken([ROLES.ADMIN]), validate(idParamSchema, "params"), revokeSession);

export default adminRouter;
