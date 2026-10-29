import express from "express";
import {
  registerPatient,
  getPatients,
  getPatient,
  exportPatient,
  deletePatient,
  withdrawConsent,
  approveExport,
  approveDelete,
} from "../controller/patient.controller.js";
import verifyToken from "../middlewares/auth.middleware.js";
import { validate } from "../middlewares/validate.middleware.js";
import {
  registerPatientSchema,
  idParamSchema,
  withdrawConsentSchema,
} from "../validators/schemas.js";
import ROLES from "../config/roles.js";

const patientRouter = express.Router();

patientRouter.post("/", verifyToken([ROLES.WORKER]), validate(registerPatientSchema), registerPatient);
patientRouter.get("/", verifyToken([ROLES.WORKER]), getPatients);
patientRouter.get("/:id/export", verifyToken([ROLES.WORKER, ROLES.DOCTOR, ROLES.ADMIN]), validate(idParamSchema, "params"), exportPatient);
patientRouter.get("/:id", verifyToken([ROLES.WORKER]), validate(idParamSchema, "params"), getPatient);
patientRouter.delete("/:id", verifyToken([ROLES.WORKER, ROLES.ADMIN]), validate(idParamSchema, "params"), deletePatient);
patientRouter.post("/:id/withdraw-consent", verifyToken([ROLES.WORKER, ROLES.ADMIN]), validate(idParamSchema, "params"), validate(withdrawConsentSchema), withdrawConsent);
patientRouter.post("/:id/approve-export", verifyToken([ROLES.ADMIN]), validate(idParamSchema, "params"), approveExport);
patientRouter.post("/:id/approve-delete", verifyToken([ROLES.ADMIN]), validate(idParamSchema, "params"), approveDelete);

export default patientRouter;
