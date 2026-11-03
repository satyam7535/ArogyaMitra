import Patient from "../models/patient/patientSchema.js";
import Consultation from "../models/consultation/consultationSchema.js";
import ROLES from "../config/roles.js";
import crypto from "crypto";
import serverConfig from "../config/serverConfig.js";
import { computePhoneBlindIndex } from "../utils/crypto.js";

// HMAC Blind Index helper for privacy-preserving duplicate detection (only phone is hashed with HMAC, not name)
export const computePatientBlindIndex = (name, phoneNumber) => {
  return computePhoneBlindIndex(phoneNumber);
};

// Worker registers a new patient in their organization
const createPatient = async (
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
  workerId,
  organization
) => {
  // Duplicate-patient warning: check keyed HMAC blind index of phone number (only phone is hashed), warning only
  const blindIndex = phoneNumber ? computePhoneBlindIndex(phoneNumber) : null;
  let potentialDuplicate = null;
  if (blindIndex) {
    potentialDuplicate = await Patient.findOne({
      organization,
      isDeleted: { $ne: true },
      blindIndex,
    });
  }

  if (!potentialDuplicate) {
    const escapedName = name.trim().replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    potentialDuplicate = await Patient.findOne({
      organization,
      isDeleted: { $ne: true },
      name: { $regex: `^${escapedName}$`, $options: "i" },
      gender,
      age: Number(age),
    });
  }

  const patient = await Patient.create({
    name,
    age: Number(age),
    gender,
    phoneNumber,
    blindIndex,
    address,
    medicalHistory,
    emergencyContact,
    consentGiven: consentGiven !== undefined ? consentGiven : true,
    consentLanguage: consentLanguage || "en",
    consentTimestamp: new Date(),
    consentVersion: consentVersion || "1.0",
    registeredBy: workerId,
    organization,
  });

  const decrypted = patient.getDecrypted();

  if (potentialDuplicate) {
    decrypted.duplicateWarning = {
      detected: true,
      existingPatientId: potentialDuplicate._id,
      message: `Potential duplicate patient record detected matching name '${name}', age ${age}, gender '${gender}' in this organization.`,
    };
  }

  return decrypted;
};

// Withdraw patient consent (DPDP Act)
const withdrawConsentScoped = async (patientId, organization, reason) => {
  const patient = await Patient.findOne({ _id: patientId, organization, isDeleted: { $ne: true } });
  if (!patient) return null;

  patient.consentGiven = false;
  patient.consentWithdrawnAt = new Date();
  patient.consentWithdrawalReason = reason || "Patient requested withdrawal of processing consent under DPDP Act";
  patient.revokedAt = new Date();
  await patient.save();

  return {
    success: true,
    message: "Patient processing consent successfully withdrawn under DPDP Act. Further AI processing is blocked.",
    patientId: patient._id,
    consentWithdrawnAt: patient.consentWithdrawnAt,
  };
};

// Admin approves patient data export under DPDP
const approveExportScoped = async (patientId, organization, adminId) => {
  const patient = await Patient.findOne({ _id: patientId, organization, isDeleted: { $ne: true } });
  if (!patient) return null;

  patient.exportApproved = true;
  patient.exportApprovedBy = adminId;
  await patient.save();

  return {
    success: true,
    message: "Patient data export request approved by Administrator",
    patientId: patient._id,
    exportApproved: true,
  };
};

// Admin approves patient deletion under DPDP
const approveDeleteScoped = async (patientId, organization, adminId) => {
  const patient = await Patient.findOne({ _id: patientId, organization, isDeleted: { $ne: true } });
  if (!patient) return null;

  patient.deletionApproved = true;
  patient.deletionApprovedBy = adminId;
  await patient.save();

  return {
    success: true,
    message: "Patient record deletion request approved by Administrator",
    patientId: patient._id,
    deletionApproved: true,
  };
};

// Get all patients strictly within the user's organization (excluding soft-deleted)
const getPatientsByOrg = async (organization) => {
  const patients = await Patient.find({ organization, isDeleted: { $ne: true } }).sort({ createdAt: -1 });
  return patients.map((p) => p.getDecrypted());
};

// Get a single patient strictly scoped to organization (returns null if cross-org or soft-deleted)
const getPatientByIdScoped = async (patientId, organization) => {
  const patient = await Patient.findOne({ _id: patientId, organization, isDeleted: { $ne: true } });
  return patient ? patient.getDecrypted() : null;
};

// Export full patient data and history under DPDP Act
const exportPatientDataScoped = async (patientId, organization, userRole) => {
  const patient = await Patient.findOne({ _id: patientId, organization, isDeleted: { $ne: true } });
  if (!patient) return null;

  if (userRole === ROLES.ADMIN && !patient.exportApproved) {
    patient.exportApproved = true;
    await patient.save();
  } else if (userRole !== ROLES.ADMIN && !patient.exportApproved) {
    const err = new Error("Patient data export requires Administrator approval under DPDP Act");
    err.statusCode = 403;
    err.code = "ADMIN_APPROVAL_REQUIRED";
    throw err;
  }

  const consultations = await Consultation.find({ patient: patientId, organization }).sort({ createdAt: -1 });

  return {
    patient: patient.getDecrypted(),
    consent: {
      consentGiven: patient.consentGiven,
      consentLanguage: patient.consentLanguage,
      consentTimestamp: patient.consentTimestamp,
      consentVersion: patient.consentVersion,
      consentWithdrawnAt: patient.consentWithdrawnAt,
      consentWithdrawalReason: patient.consentWithdrawalReason,
      revokedAt: patient.revokedAt,
    },
    exportApproved: patient.exportApproved,
    deletionApproved: patient.deletionApproved,
    emergencyContact: patient.getDecrypted().emergencyContact,
    consultations: consultations.map((c) => ({
      _id: c._id,
      symptoms: c.symptoms,
      status: c.status,
      createdAt: c.createdAt,
      mlAnalysis: c.mlAnalysis
        ? {
            disease: c.mlAnalysis.disease,
            confidence: c.mlAnalysis.confidence,
            severityScore: c.mlAnalysis.severityScore,
          }
        : null,
      secondOpinion: c.secondOpinion,
      workerDecision: c.workerDecision,
    })),
    exportedAt: new Date(),
  };
};

// Revoke patient consent and anonymize record under DPDP Act
const deletePatientScoped = async (patientId, organization, userRole) => {
  const patient = await Patient.findOne({ _id: patientId, organization, isDeleted: { $ne: true } });
  if (!patient) return null;

  if (userRole === ROLES.ADMIN && !patient.deletionApproved) {
    patient.deletionApproved = true;
  } else if (userRole !== ROLES.ADMIN && !patient.deletionApproved) {
    const err = new Error("Patient data erasure requires Administrator approval under DPDP Act");
    err.statusCode = 403;
    err.code = "ADMIN_APPROVAL_REQUIRED";
    throw err;
  }

  patient.consentGiven = false;
  patient.revokedAt = new Date();
  patient.isDeleted = true;
  patient.deletedAt = new Date();

  // DPDP Anonymization: Wipe all direct and sensitive identifiers
  patient.name = "[ANONYMIZED]";
  patient.phoneNumber = "[ANONYMIZED]";
  patient.address = "[ANONYMIZED]";
  patient.medicalHistory = "[ANONYMIZED]";
  if (patient.emergencyContact) {
    patient.emergencyContact.name = "[ANONYMIZED]";
    patient.emergencyContact.phoneNumber = "[ANONYMIZED]";
    patient.emergencyContact.relationship = "[ANONYMIZED]";
  }

  await patient.save();
  return {
    success: true,
    message: "Patient consent revoked and record anonymized under DPDP",
    patientId: patient._id,
    deletionApproved: patient.deletionApproved,
  };
};

// Patient history timeline endpoint (organization-scoped) (WP 3.10)
const getPatientTimelineScoped = async (patientId, organization) => {
  const patient = await Patient.findOne({ _id: patientId, organization, isDeleted: { $ne: true } });
  if (!patient) return null;

  const consultations = await Consultation.find({ patient: patientId, organization })
    .populate("submittedBy", "name email")
    .populate("assignedDoctor", "name specialization email")
    .sort({ createdAt: -1 });

  const timelineEvents = [
    {
      type: "PATIENT_REGISTERED",
      timestamp: patient.createdAt,
      title: "Patient Registered",
      description: `Registered with DPDP consent (${patient.consentLanguage}, v${patient.consentVersion})`,
    },
  ];

  if (patient.consentWithdrawnAt) {
    timelineEvents.push({
      type: "CONSENT_WITHDRAWN",
      timestamp: patient.consentWithdrawnAt,
      title: "Consent Withdrawn",
      description: patient.consentWithdrawalReason || "Consent withdrawn under DPDP",
    });
  }

  for (const c of consultations) {
    timelineEvents.push({
      type: "CONSULTATION_CREATED",
      consultationId: c._id,
      timestamp: c.createdAt,
      title: `Consultation (${c.status})`,
      symptoms: c.symptoms,
      disease: c.mlAnalysis?.disease || "Pending Analysis",
      needsEscalation: c.mlAnalysis?.needsEscalation || false,
      redFlag: c.mlAnalysis?.redFlag || false,
      workerDecision: c.workerDecision || null,
      submittedBy: c.submittedBy?.name || "Healthcare Worker",
    });

    if (c.secondOpinion?.respondedAt) {
      timelineEvents.push({
        type: "DOCTOR_REVIEW",
        consultationId: c._id,
        timestamp: c.secondOpinion.respondedAt,
        title: "Doctor Second Opinion",
        doctor: c.assignedDoctor?.name || "Medical Officer",
        diagnosis: c.secondOpinion.diagnosis,
        recommendation: c.secondOpinion.recommendation,
        agreement: c.aiDoctorAgreement?.agreement ?? null,
      });
    }
  }

  timelineEvents.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

  return {
    patient: patient.getDecrypted(),
    timeline: timelineEvents,
  };
};

export {
  createPatient,
  getPatientsByOrg,
  getPatientByIdScoped,
  getPatientTimelineScoped,
  exportPatientDataScoped,
  deletePatientScoped,
  withdrawConsentScoped,
  approveExportScoped,
  approveDeleteScoped,
};
