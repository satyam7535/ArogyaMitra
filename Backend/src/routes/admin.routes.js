import express from "express";
import {
  register,
  login,
  refreshSession,
  forgotPassword,
  resetPassword,
  logout,
  getProfile,
} from "../controller/admin.controller.js";
import verifyToken from "../middlewares/auth.middleware.js";
import { authRateLimiter } from "../middlewares/security.middleware.js";

const adminRouter = express.Router();

// Public auth routes (rate limited)
adminRouter.post("/register", register); // Returns 403 disabled
adminRouter.post("/login", authRateLimiter, login);
adminRouter.post("/refresh-token", refreshSession);
adminRouter.post("/forgot-password", authRateLimiter, forgotPassword);
adminRouter.post("/reset-password", authRateLimiter, resetPassword);

// Protected routes (Admin only)
adminRouter.post("/logout", verifyToken(["Admin", "admin"]), logout);
adminRouter.get("/profile", verifyToken(["Admin", "admin"]), getProfile);

export default adminRouter;
