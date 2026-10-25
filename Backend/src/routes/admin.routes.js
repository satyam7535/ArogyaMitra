import express from "express";
import { register, login, logout, getProfile } from "../controller/admin.controller.js";
import verifyToken from "../middlewares/auth.middleware.js";

const adminRouter = express.Router();

// Public routes
adminRouter.post("/register", register);
adminRouter.post("/login", login);

// Protected routes (admin only)
adminRouter.post("/logout", verifyToken(["admin"]), logout);
adminRouter.get("/profile", verifyToken(["admin"]), getProfile);

export default adminRouter;
