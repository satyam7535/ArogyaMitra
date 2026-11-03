import mongoose from "mongoose";
import Doctor from "../models/doctor/doctorSchema.js";
import RefreshToken from "../models/auth/refreshTokenSchema.js";
import ROLES from "../config/roles.js";
import { dispatchPasswordReset } from "../utils/emailAdapter.js";
import {
  generateTokenPair,
  authenticateWithLockout,
  initiatePasswordReset,
  completePasswordReset,
  rotateRefreshToken,
} from "./auth.service.js";

// Called by Admin to add a doctor in their organization
const addDoctor = async ({ name, email, phoneNumber, password, specialization }, adminId, organization) => {
  const existing = await Doctor.findOne({ $or: [{ email }, { phoneNumber }] });
  if (existing) {
    throw { status: 400, message: "Doctor with this email or phone number already exists" };
  }

  const doctor = await Doctor.create({
    name,
    email,
    phoneNumber,
    password,
    specialization,
    addedBy: adminId,
    organization,
    role: ROLES.DOCTOR,
  });

  return doctor;
};

// Get all doctors in admin's organization
const getDoctorsByOrg = async (organization) => {
  return await Doctor.find({ organization }).select("-password");
};

// Doctor login with lockout and token rotation
const loginDoctor = async ({ email, password }) => {
  const doctor = await Doctor.findOne({ email }).populate("organization");
  if (!doctor) {
    throw { status: 401, message: "Invalid email or password", code: "INVALID_CREDENTIALS" };
  }

  if (doctor.isActive === false) {
    throw { status: 403, message: "Account has been deactivated. Please contact your administrator.", code: "ACCOUNT_DEACTIVATED" };
  }

  await authenticateWithLockout(doctor, password);
  const tokens = await generateTokenPair(doctor, "Doctor");

  return { ...tokens, doctor };
};

// Soft-deactivate a doctor strictly scoped to the admin's organization (no hard delete)
const deleteDoctorScoped = async (doctorId, organization, adminId = null) => {
  const updated = await Doctor.findOneAndUpdate(
    { _id: doctorId, organization },
    { isActive: false, deactivatedAt: new Date(), deactivatedBy: adminId },
    { new: true }
  );
  if (updated && mongoose.connection.readyState !== 0) {
    await RefreshToken.updateMany({ userId: doctorId }, { isRevoked: true });
  }
  return updated;
};

// Reactivate a deactivated doctor strictly scoped to the admin's organization
const reactivateDoctorScoped = async (doctorId, organization) => {
  return await Doctor.findOneAndUpdate(
    { _id: doctorId, organization },
    { isActive: true, deactivatedAt: null, deactivatedBy: null },
    { new: true }
  );
};

// Get available doctors in the organization (for escalation dropdown)
const getAllDoctorsFromDB = async (organization) => {
  return await Doctor.find({ organization, isAvailable: true })
    .select("-password")
    .sort({ name: 1 });
};

const handleForgotPassword = async (email) => {
  const doctor = await Doctor.findOne({ email });
  if (!doctor) {
    return { message: "If that email exists, password reset instructions have been sent." };
  }
  const resetToken = await initiatePasswordReset(doctor);
  dispatchPasswordReset({ email, role: ROLES.DOCTOR, resetToken });
  return { message: "If that email exists, password reset instructions have been sent." };
};

const handleResetPassword = async (resetToken, newPassword) => {
  return await completePasswordReset(Doctor, resetToken, newPassword);
};

export {
  addDoctor,
  getDoctorsByOrg,
  getAllDoctorsFromDB,
  loginDoctor,
  deleteDoctorScoped,
  reactivateDoctorScoped,
  handleForgotPassword,
  handleResetPassword,
  rotateRefreshToken,
};
