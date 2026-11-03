import mongoose from "mongoose";
import Worker from "../models/worker/workerSchema.js";
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
    role: ROLES.WORKER,
  });

  return worker;
};

// Admin gets all workers in their organization
const getWorkersByOrg = async (organization) => {
  return await Worker.find({ organization })
    .select("-password")
    .sort({ createdAt: -1 });
};

// Worker login with lockout check and token family generation
const loginWorker = async ({ email, password }) => {
  const worker = await Worker.findOne({ email }).populate("organization");
  if (!worker) {
    throw { status: 401, message: "Invalid email or password", code: "INVALID_CREDENTIALS" };
  }

  if (worker.isActive === false) {
    throw { status: 403, message: "Account has been deactivated. Please contact your administrator.", code: "ACCOUNT_DEACTIVATED" };
  }

  await authenticateWithLockout(worker, password);
  const tokens = await generateTokenPair(worker, "Worker");

  return { ...tokens, worker };
};

// Soft-deactivate a worker strictly scoped to the admin's organization (no hard delete)
const deleteWorkerScoped = async (workerId, organization, adminId = null) => {
  const updated = await Worker.findOneAndUpdate(
    { _id: workerId, organization },
    { isActive: false, deactivatedAt: new Date(), deactivatedBy: adminId },
    { new: true }
  );
  if (updated && mongoose.connection.readyState !== 0) {
    await RefreshToken.updateMany({ userId: workerId }, { isRevoked: true });
  }
  return updated;
};

// Reactivate a deactivated worker strictly scoped to the admin's organization
const reactivateWorkerScoped = async (workerId, organization) => {
  return await Worker.findOneAndUpdate(
    { _id: workerId, organization },
    { isActive: true, deactivatedAt: null, deactivatedBy: null },
    { new: true }
  );
};

const handleForgotPassword = async (email) => {
  const worker = await Worker.findOne({ email });
  if (!worker) {
    return { message: "If that email exists, password reset instructions have been sent." };
  }
  const resetToken = await initiatePasswordReset(worker);
  dispatchPasswordReset({ email, role: ROLES.WORKER, resetToken });
  return { message: "If that email exists, password reset instructions have been sent." };
};

const handleResetPassword = async (resetToken, newPassword) => {
  return await completePasswordReset(Worker, resetToken, newPassword);
};

export {
  addWorker,
  getWorkersByOrg,
  loginWorker,
  deleteWorkerScoped,
  reactivateWorkerScoped,
  handleForgotPassword,
  handleResetPassword,
  rotateRefreshToken,
};
