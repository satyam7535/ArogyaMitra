import express from "express";
import { registerPatient, getPatients, getPatient } from "../controller/patient.controller.js";
import verifyToken from "../middlewares/auth.middleware.js";

const patientRouter = express.Router();

// All patient routes are worker-only
patientRouter.post("/", verifyToken(["worker"]), registerPatient);        // POST /api/v1/patient
patientRouter.get("/", verifyToken(["worker"]), getPatients);             // GET  /api/v1/patient
patientRouter.get("/:id", verifyToken(["worker"]), getPatient);           // GET  /api/v1/patient/:id

export default patientRouter;
