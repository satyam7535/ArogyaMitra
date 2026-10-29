import Admin from "../models/admin/adminSchema.js";
import ROLES from "../config/roles.js";
import { dispatchPasswordReset } from "../utils/emailAdapter.js";
import {
  generateTokenPair,
  authenticateWithLockout,
  initiatePasswordReset,
  completePasswordReset,
  rotateRefreshToken,
} from "./auth.service.js";

const loginAdmin = async ({ email, password }) => {
  const admin = await Admin.findOne({ email });
  if (!admin) {
    throw { status: 401, message: "Invalid email or password", code: "INVALID_CREDENTIALS" };
  }

  // Validate password with 5-attempt lockout enforcement
  await authenticateWithLockout(admin, password);

  // Generate short-lived accessToken and rotating refreshToken
  const tokens = await generateTokenPair(admin, "Admin");

  return { ...tokens, admin };
};

const handleForgotPassword = async (email) => {
  const admin = await Admin.findOne({ email });
  if (!admin) {
    // Return generic success message to prevent user enumeration
    return { message: "If that email exists, password reset instructions have been sent." };
  }
  const resetToken = await initiatePasswordReset(admin);
  dispatchPasswordReset({ email, role: ROLES.ADMIN, resetToken });
  return { message: "If that email exists, password reset instructions have been sent." };
};

const handleResetPassword = async (resetToken, newPassword) => {
  return await completePasswordReset(Admin, resetToken, newPassword);
};

export {
  loginAdmin,
  handleForgotPassword,
  handleResetPassword,
  rotateRefreshToken,
};


import RefreshToken from "../models/auth/refreshTokenSchema.js";
import Consultation from "../models/consultation/consultationSchema.js";

/**
 * Neutralizes CSV injection formula characters (=, +, -, @).
 * Prepends a single quote to prevent spreadsheet interpreters from executing code.
 */
export const sanitizeCsvField = (value) => {
  if (value === null || value === undefined) return "";
  const str = String(value);
  if (/^[=+\-@\t\r]/.test(str)) {
    return `'${str}`;
  }
  return str;
};

/**
 * Generates an audit CSV export of all consultations with formula injection neutralization.
 */
export const exportConsultationsCsv = async (organization) => {
  const consultations = await Consultation.find({ organization })
    .populate("patient", "name age gender")
    .populate("submittedBy", "name email")
    .lean();

  const headers = [
    "ConsultationID",
    "CreatedAt",
    "Status",
    "PrimaryDiagnosis",
    "ConfidenceScore",
    "Risk",
    "RedFlag",
    "NeedsEscalation",
    "WorkerDecision",
    "OverrideReason",
    "OverrideNote",
    "PatientName",
    "PatientAge",
    "PatientGender",
    "WorkerName",
  ];

  const rows = [headers.join(",")];

  for (const c of consultations) {
    const row = [
      sanitizeCsvField(c._id),
      sanitizeCsvField(c.createdAt ? new Date(c.createdAt).toISOString() : ""),
      sanitizeCsvField(c.status),
      sanitizeCsvField(c.mlAnalysis?.disease || c.finalVerdict?.primaryDiagnosis || ""),
      sanitizeCsvField(c.mlAnalysis?.confidence || ""),
      sanitizeCsvField(c.risk || ""),
      sanitizeCsvField(c.redFlag ? "YES" : "NO"),
      sanitizeCsvField(c.needsEscalation ? "YES" : "NO"),
      sanitizeCsvField(c.workerDecision || ""),
      sanitizeCsvField(c.overrideReason || ""),
      sanitizeCsvField(c.overrideDetails?.note || c.decisionNote || ""),
      sanitizeCsvField(c.patient?.name || "Patient"),
      sanitizeCsvField(c.patient?.age || ""),
      sanitizeCsvField(c.patient?.gender || ""),
      sanitizeCsvField(c.submittedBy?.name || "Worker"),
    ];
    // Quote fields containing comma or quotes
    const escapedRow = row.map((field) => {
      if (field.includes(",") || field.includes('"') || field.includes("\n")) {
        return `"${field.replace(/"/g, '""')}"`;
      }
      return field;
    });
    rows.push(escapedRow.join(","));
  }

  return rows.join("\n");
};

/**
 * Lists active sessions (refresh tokens) within the admin's organization.
 */
export const listActiveSessions = async (organization) => {
  const now = new Date();
  const sessions = await RefreshToken.find({
    organization,
    isRevoked: false,
    expiresAt: { $gt: now },
  })
    .populate("userId", "name email")
    .sort({ createdAt: -1 })
    .lean();

  return sessions.map((s) => ({
    id: s._id,
    userId: s.userId?._id || s.userId,
    userEmail: s.userId?.email || "Unknown",
    userName: s.userId?.name || "Unknown",
    userRole: s.userModel,
    familyId: s.familyId,
    createdAt: s.createdAt,
    expiresAt: s.expiresAt,
  }));
};

/**
 * Revokes an active session by ID, scoped to the organization.
 */
export const revokeSessionById = async (sessionId, organization) => {
  const session = await RefreshToken.findOne({ _id: sessionId, organization });
  if (!session) {
    throw { status: 404, message: "Session not found" };
  }
  session.isRevoked = true;
  await session.save();
  return { message: "Session successfully revoked" };
};
