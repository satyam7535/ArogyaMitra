import express from "express";
import {
  createWorker,
  getWorkers,
  login,
  refreshSession,
  forgotPassword,
  resetPassword,
  logout,
  deleteWorker,
  reactivateWorker,
} from "../controller/worker.controller.js";
import verifyToken from "../middlewares/auth.middleware.js";
import { authRateLimiter } from "../middlewares/security.middleware.js";
import { validate } from "../middlewares/validate.middleware.js";
import {
  loginSchema,
  refreshSchema,
  forgotPasswordSchema,
  resetPasswordSchema,
  logoutSchema,
  createWorkerSchema,
  idParamSchema,
} from "../validators/schemas.js";
import ROLES from "../config/roles.js";

const workerRouter = express.Router();

// Public auth routes (rate limited + zod validated)
workerRouter.post("/login", authRateLimiter, validate(loginSchema), login);
workerRouter.post("/refresh-token", validate(refreshSchema), refreshSession);
workerRouter.post("/forgot-password", authRateLimiter, validate(forgotPasswordSchema), forgotPassword);
workerRouter.post("/reset-password", authRateLimiter, validate(resetPasswordSchema), resetPassword);

// Worker self-logout
workerRouter.post("/logout", verifyToken([ROLES.WORKER]), validate(logoutSchema), logout);

// Admin-only routes (strictly scoped to Admin's organization)
workerRouter.post("/", verifyToken([ROLES.ADMIN]), validate(createWorkerSchema), createWorker);
workerRouter.get("/", verifyToken([ROLES.ADMIN]), getWorkers);
workerRouter.delete("/:id", verifyToken([ROLES.ADMIN]), validate(idParamSchema, "params"), deleteWorker);
workerRouter.patch("/:id/deactivate", verifyToken([ROLES.ADMIN]), validate(idParamSchema, "params"), deleteWorker);
workerRouter.patch("/:id/reactivate", verifyToken([ROLES.ADMIN]), validate(idParamSchema, "params"), reactivateWorker);

export default workerRouter;
