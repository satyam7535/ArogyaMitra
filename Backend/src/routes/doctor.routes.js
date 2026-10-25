import express from "express";
import { createDoctor, getDoctors, getAllDoctors, login, logout, deleteDoctor } from "../controller/doctor.controller.js";
import verifyToken from "../middlewares/auth.middleware.js";

const doctorRouter = express.Router();

// Admin-only routes
doctorRouter.post("/", verifyToken(["admin"]), createDoctor);        // POST   /api/v1/doctor
doctorRouter.get("/", verifyToken(["admin"]), getDoctors);           // GET    /api/v1/doctor
doctorRouter.delete("/:id", verifyToken(["admin"]), deleteDoctor);   // DELETE /api/v1/doctor/:id

// Worker can fetch all doctors (for escalation dropdown)
doctorRouter.get("/list", verifyToken(["worker", "admin"]), getAllDoctors); // GET /api/v1/doctor/list

// Doctor auth routes (public)
doctorRouter.post("/login", login);                                   // POST /api/v1/doctor/login
doctorRouter.post("/logout", verifyToken(["doctor"]), logout);        // POST /api/v1/doctor/logout

export default doctorRouter;
