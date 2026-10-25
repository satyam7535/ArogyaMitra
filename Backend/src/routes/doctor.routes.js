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
} from "../controller/doctor.controller.js";
import verifyToken from "../middlewares/auth.middleware.js";
import { authRateLimiter } from "../middlewares/security.middleware.js";

const doctorRouter = express.Router();

// Public auth routes (rate limited)
doctorRouter.post("/login", authRateLimiter, login);
doctorRouter.post("/refresh-token", refreshSession);
doctorRouter.post("/forgot-password", authRateLimiter, forgotPassword);
doctorRouter.post("/reset-password", authRateLimiter, resetPassword);

// Doctor self-logout
doctorRouter.post("/logout", verifyToken(["Doctor", "doctor"]), logout);

// Admin-only routes (scoped to Admin's organization)
doctorRouter.post("/", verifyToken(["Admin", "admin"]), createDoctor);
doctorRouter.get("/", verifyToken(["Admin", "admin"]), getDoctors);
doctorRouter.delete("/:id", verifyToken(["Admin", "admin"]), deleteDoctor);

// Worker or Admin gets doctors within their organization for escalation
doctorRouter.get("/list", verifyToken(["Worker", "worker", "Admin", "admin"]), getAllDoctors);

export default doctorRouter;
