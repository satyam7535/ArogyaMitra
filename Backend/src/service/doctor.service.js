import Doctor from "../models/doctor/doctorSchema.js";
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
    role: "Doctor",
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

  await authenticateWithLockout(doctor, password);
  const tokens = await generateTokenPair(doctor, "Doctor");

  return { ...tokens, doctor };
};

// Delete a doctor strictly scoped to the admin's organization (returns null if cross-org)
const deleteDoctorScoped = async (doctorId, organization) => {
  return await Doctor.findOneAndDelete({ _id: doctorId, organization });
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
  if (process.env.NODE_ENV === "development") {
    console.log(`[DEV RESET LINK] Doctor (${email}): resetToken=[REDACTED]`);
  }
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
  handleForgotPassword,
  handleResetPassword,
  rotateRefreshToken,
};
