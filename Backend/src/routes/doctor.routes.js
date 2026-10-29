import express from "express";
import {
  createDoctor,
  getDoctors,
  getAllDoctors,
  login,
  refreshSession,
  forgotPassword,
  resetPassword,
  logout,
  deleteDoctor,
  reactivateDoctor,
} from "../controller/doctor.controller.js";
import verifyToken from "../middlewares/auth.middleware.js";
import { authRateLimiter } from "../middlewares/security.middleware.js";
import { validate } from "../middlewares/validate.middleware.js";
import {
  loginSchema,
  refreshSchema,
  forgotPasswordSchema,
  resetPasswordSchema,
  logoutSchema,
  createDoctorSchema,
  idParamSchema,
} from "../validators/schemas.js";
import ROLES from "../config/roles.js";

const doctorRouter = express.Router();

// Public auth routes (rate limited + zod validated)
doctorRouter.post("/login", authRateLimiter, validate(loginSchema), login);
doctorRouter.post("/refresh-token", validate(refreshSchema), refreshSession);
doctorRouter.post("/forgot-password", authRateLimiter, validate(forgotPasswordSchema), forgotPassword);
doctorRouter.post("/reset-password", authRateLimiter, validate(resetPasswordSchema), resetPassword);

// Doctor self-logout
doctorRouter.post("/logout", verifyToken([ROLES.DOCTOR]), validate(logoutSchema), logout);

// Admin-only routes (scoped to Admin's organization)
doctorRouter.post("/", verifyToken([ROLES.ADMIN]), validate(createDoctorSchema), createDoctor);
doctorRouter.get("/", verifyToken([ROLES.ADMIN]), getDoctors);
doctorRouter.delete("/:id", verifyToken([ROLES.ADMIN]), validate(idParamSchema, "params"), deleteDoctor);
doctorRouter.patch("/:id/deactivate", verifyToken([ROLES.ADMIN]), validate(idParamSchema, "params"), deleteDoctor);
doctorRouter.patch("/:id/reactivate", verifyToken([ROLES.ADMIN]), validate(idParamSchema, "params"), reactivateDoctor);

// Worker or Admin gets doctors within their organization for escalation
doctorRouter.get("/list", verifyToken([ROLES.WORKER, ROLES.ADMIN]), getAllDoctors);

export default doctorRouter;
