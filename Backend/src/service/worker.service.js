import Worker from "../models/worker/workerSchema.js";
import {
  generateTokenPair,
  authenticateWithLockout,
  initiatePasswordReset,
  completePasswordReset,
  rotateRefreshToken,
} from "./auth.service.js";

// Called by Admin to add a worker in their organization
const addWorker = async ({ name, email, phoneNumber, password }, adminId, organization) => {
  const existing = await Worker.findOne({ $or: [{ email }, { phoneNumber }] });
  if (existing) {
    throw { status: 400, message: "Worker with this email or phone number already exists" };
  }

  const worker = await Worker.create({
    name,
    email,
    phoneNumber,
    password,
    addedBy: adminId,
    organization,
    role: "Worker",
  });

  return worker;
};

// Get all workers scoped to the organization
const getWorkersByOrg = async (organization) => {
  return await Worker.find({ organization }).select("-password");
};

// Worker login with lockout and token rotation
const loginWorker = async ({ email, password }) => {
  const worker = await Worker.findOne({ email }).populate("organization");
  if (!worker) {
    throw { status: 401, message: "Invalid email or password", code: "INVALID_CREDENTIALS" };
  }

  await authenticateWithLockout(worker, password);
  const tokens = await generateTokenPair(worker, "Worker");

  return { ...tokens, worker };
};

// Delete a worker strictly scoped to the admin's organization (returns null if cross-org)
const deleteWorkerScoped = async (workerId, organization) => {
  return await Worker.findOneAndDelete({ _id: workerId, organization });
};

const handleForgotPassword = async (email) => {
  const worker = await Worker.findOne({ email });
  if (!worker) {
    return { message: "If that email exists, password reset instructions have been sent." };
  }
  const resetToken = await initiatePasswordReset(worker);
  return { message: "Password reset token generated.", resetToken };
};

const handleResetPassword = async (resetToken, newPassword) => {
  return await completePasswordReset(Worker, resetToken, newPassword);
};

export {
  addWorker,
  getWorkersByOrg,
  loginWorker,
  deleteWorkerScoped,
  handleForgotPassword,
  handleResetPassword,
  rotateRefreshToken,
};
