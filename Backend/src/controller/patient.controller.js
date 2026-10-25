import {
  createPatient,
  getPatientsByOrg,
  getPatientByIdScoped,
} from "../service/patient.service.js";
import { logAuditEvent } from "../middlewares/audit.middleware.js";

// Worker registers a new patient
const registerPatient = async (req, res) => {
  try {
    const { name, age, gender, phoneNumber, address, medicalHistory } = req.body;

    if (!name || !age || !gender) {
      return res.status(400).json({ message: "Name, age, and gender are required" });
    }

    const patient = await createPatient(
      { name, age, gender, phoneNumber, address, medicalHistory },
      req.user.id,
      req.user.organization
    );

    await logAuditEvent({
      req,
      action: "PATIENT_REGISTERED",
      resourceType: "Patient",
      resourceId: patient._id,
      metadata: { name: patient.name },
    });

    return res.status(201).json({ message: "Patient registered successfully", patient });
  } catch (error) {
    return res.status(500).json({ message: error.message });
  }
};

// Worker gets all patients in their organization
const getPatients = async (req, res) => {
  try {
    const patients = await getPatientsByOrg(req.user.organization);
    return res.status(200).json({ patients });
  } catch (error) {
    return res.status(500).json({ message: error.message });
  }
};

// Get a single patient (strictly scoped to organization)
const getPatient = async (req, res) => {
  try {
    const patient = await getPatientByIdScoped(req.params.id, req.user.organization);
    if (!patient) {
      // 404 Not Found to prevent enumeration across organizations
      return res.status(404).json({ message: "Patient not found" });
    }

    await logAuditEvent({
      req,
      action: "PATIENT_VIEWED",
      resourceType: "Patient",
      resourceId: req.params.id,
    });

    return res.status(200).json({ patient });
  } catch (error) {
    return res.status(500).json({ message: error.message });
  }
};

export { registerPatient, getPatients, getPatient };
