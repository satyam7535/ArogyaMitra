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
} from "../controller/worker.controller.js";
import verifyToken from "../middlewares/auth.middleware.js";
import { authRateLimiter } from "../middlewares/security.middleware.js";

const workerRouter = express.Router();

// Public auth routes (rate limited)
workerRouter.post("/login", authRateLimiter, login);
workerRouter.post("/refresh-token", refreshSession);
workerRouter.post("/forgot-password", authRateLimiter, forgotPassword);
workerRouter.post("/reset-password", authRateLimiter, resetPassword);

// Worker self-logout
workerRouter.post("/logout", verifyToken(["Worker", "worker"]), logout);

// Admin-only routes (strictly scoped to Admin's organization)
workerRouter.post("/", verifyToken(["Admin", "admin"]), createWorker);
workerRouter.get("/", verifyToken(["Admin", "admin"]), getWorkers);
workerRouter.delete("/:id", verifyToken(["Admin", "admin"]), deleteWorker);

export default workerRouter;
