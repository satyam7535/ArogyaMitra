import {
  createPatient,
  getPatientsByOrg,
  getPatientByIdScoped,
  getPatientTimelineScoped,
  exportPatientDataScoped,
  deletePatientScoped,
  withdrawConsentScoped,
  approveExportScoped,
  approveDeleteScoped,
} from "../service/patient.service.js";
import { logAuditEvent } from "../middlewares/audit.middleware.js";

// Worker registers a new patient
const registerPatient = async (req, res) => {
  try {
    const {
      name,
      age,
      gender,
      phoneNumber,
      address,
      medicalHistory,
      emergencyContact,
      consentGiven,
      consentLanguage,
      consentVersion,
    } = req.body;

    if (!name || !age || !gender) {
      return res.status(400).json({ message: "Name, age, and gender are required" });
    }

    const patient = await createPatient(
      {
        name,
        age,
        gender,
        phoneNumber,
        address,
        medicalHistory,
        emergencyContact,
        consentGiven,
        consentLanguage,
        consentVersion,
      },
      req.user.id,
      req.user.organization
    );

    await logAuditEvent({
      req,
      action: "PATIENT_REGISTERED",
      resourceType: "Patient",
      resourceId: patient._id,
      metadata: { consentGiven: patient.consentGiven, consentVersion: patient.consentVersion },
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

// Export patient data under DPDP (scoped to organization, requires Admin approval for Worker)
const exportPatient = async (req, res) => {
  try {
    const exportData = await exportPatientDataScoped(req.params.id, req.user.organization, req.user.role);
    if (!exportData) {
      return res.status(404).json({ message: "Patient not found" });
    }

    await logAuditEvent({
      req,
      action: "PATIENT_DATA_EXPORTED",
      resourceType: "Patient",
      resourceId: req.params.id,
    });

    return res.status(200).json({ message: "Patient data exported successfully", data: exportData });
  } catch (error) {
    if (error.statusCode === 403 || error.code === "ADMIN_APPROVAL_REQUIRED") {
      return res.status(403).json({ message: error.message, code: error.code });
    }
    return res.status(500).json({ message: error.message });
  }
};

// Revoke consent and anonymize patient data under DPDP (scoped to organization, requires Admin approval for Worker)
const deletePatient = async (req, res) => {
  try {
    const result = await deletePatientScoped(req.params.id, req.user.organization, req.user.role);
    if (!result) {
      return res.status(404).json({ message: "Patient not found" });
    }

    await logAuditEvent({
      req,
      action: "PATIENT_CONSENT_REVOKED_DELETED",
      resourceType: "Patient",
      resourceId: req.params.id,
    });

    return res.status(200).json({ message: "Patient consent revoked and record anonymized under DPDP", result });
  } catch (error) {
    if (error.statusCode === 403 || error.code === "ADMIN_APPROVAL_REQUIRED") {
      return res.status(403).json({ message: error.message, code: error.code });
    }
    return res.status(500).json({ message: error.message });
  }
};

// Withdraw patient consent endpoint (DPDP Act)
const withdrawConsent = async (req, res) => {
  try {
    const result = await withdrawConsentScoped(req.params.id, req.user.organization, req.body.reason);
    if (!result) {
      return res.status(404).json({ message: "Patient not found" });
    }

    await logAuditEvent({
      req,
      action: "PATIENT_CONSENT_WITHDRAWN",
      resourceType: "Patient",
      resourceId: req.params.id,
      metadata: { reason: req.body.reason },
    });

    return res.status(200).json({ message: "Patient consent successfully withdrawn under DPDP Act", result });
  } catch (error) {
    return res.status(500).json({ message: error.message });
  }
};

// Admin approves export request
const approveExport = async (req, res) => {
  try {
    const result = await approveExportScoped(req.params.id, req.user.organization, req.user.id);
    if (!result) {
      return res.status(404).json({ message: "Patient not found" });
    }

    await logAuditEvent({
      req,
      action: "PATIENT_EXPORT_APPROVED",
      resourceType: "Patient",
      resourceId: req.params.id,
    });

    return res.status(200).json({ message: "Export approved successfully", result });
  } catch (error) {
    return res.status(500).json({ message: error.message });
  }
};

// Admin approves deletion request
const approveDelete = async (req, res) => {
  try {
    const result = await approveDeleteScoped(req.params.id, req.user.organization, req.user.id);
    if (!result) {
      return res.status(404).json({ message: "Patient not found" });
    }

    await logAuditEvent({
      req,
      action: "PATIENT_DELETION_APPROVED",
      resourceType: "Patient",
      resourceId: req.params.id,
    });

    return res.status(200).json({ message: "Deletion approved successfully", result });
  } catch (error) {
    return res.status(500).json({ message: error.message });
  }
};

// Patient history timeline (organization-scoped) (WP 3.10)
const getPatientTimeline = async (req, res) => {
  try {
    const data = await getPatientTimelineScoped(req.params.id, req.user.organization);
    if (!data) {
      return res.status(404).json({ message: "Patient not found" });
    }

    await logAuditEvent({
      req,
      action: "PATIENT_TIMELINE_VIEWED",
      resourceType: "Patient",
      resourceId: req.params.id,
    });

    return res.status(200).json(data);
  } catch (error) {
    return res.status(500).json({ message: error.message });
  }
};

export {
  registerPatient,
  getPatients,
  getPatient,
  getPatientTimeline,
  exportPatient,
  deletePatient,
  withdrawConsent,
  approveExport,
  approveDelete,
};
