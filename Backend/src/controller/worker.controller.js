import {
  addWorker,
  getWorkersByOrg,
  loginWorker,
  deleteWorkerScoped,
  reactivateWorkerScoped,
  handleForgotPassword,
  handleResetPassword,
  rotateRefreshToken,
} from "../service/worker.service.js";
import { logAuditEvent } from "../middlewares/audit.middleware.js";
import RefreshToken from "../models/auth/refreshTokenSchema.js";
import { hashToken } from "../utils/crypto.js";

// Admin soft-deactivates a worker (strictly scoped to admin's organization)
const deleteWorker = async (req, res) => {
  try {
    const { id } = req.params;
    const worker = await deleteWorkerScoped(id, req.user.organization, req.user.id);

    if (!worker) {
      return res.status(404).json({ message: "Worker not found" });
    }

    await logAuditEvent({
      req,
      action: "WORKER_DEACTIVATED",
      resourceType: "Worker",
      resourceId: id,
    });

    return res.status(200).json({ message: "Worker deactivated successfully", worker });
  } catch (error) {
    return res.status(500).json({ message: error.message });
  }
};

// Admin reactivates a worker
const reactivateWorker = async (req, res) => {
  try {
    const { id } = req.params;
    const worker = await reactivateWorkerScoped(id, req.user.organization);

    if (!worker) {
      return res.status(404).json({ message: "Worker not found" });
    }

    await logAuditEvent({
      req,
      action: "WORKER_REACTIVATED",
      resourceType: "Worker",
      resourceId: id,
    });

    return res.status(200).json({ message: "Worker reactivated successfully", worker });
  } catch (error) {
    return res.status(500).json({ message: error.message });
  }
};

// Admin adds a worker (inherits admin's organization)
const createWorker = async (req, res) => {
  try {
    const { name, email, phoneNumber, password } = req.body;

    if (!name || !email || !phoneNumber || !password) {
      return res.status(400).json({ message: "All fields are required" });
    }

    const worker = await addWorker(
      { name, email, phoneNumber, password },
      req.user.id,
      req.user.organization
    );

    await logAuditEvent({
      req,
      action: "WORKER_CREATED",
      resourceType: "Worker",
      resourceId: worker._id,
      metadata: { email: worker.email },
    });

    return res.status(201).json({
      message: "Worker added successfully",
      worker: {
        id: worker._id,
        name: worker.name,
        email: worker.email,
        phoneNumber: worker.phoneNumber,
        organization: worker.organization,
        addedBy: worker.addedBy,
      },
    });
  } catch (error) {
    return res.status(error.status || 400).json({ message: error.message });
  }
};

// Admin gets all workers in their organization
const getWorkers = async (req, res) => {
  try {
    const workers = await getWorkersByOrg(req.user.organization);
    return res.status(200).json({ workers });
  } catch (error) {
    return res.status(500).json({ message: error.message });
  }
};

// Worker login
const login = async (req, res) => {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      return res.status(400).json({ message: "Email and password are required" });
    }

    const { accessToken, refreshToken, worker } = await loginWorker({ email, password });

    res.cookie("token", accessToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "strict",
      maxAge: 15 * 60 * 1000,
    });

    res.cookie("refreshToken", refreshToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "strict",
      maxAge: 7 * 24 * 60 * 60 * 1000,
    });

    await logAuditEvent({
      req,
      action: "WORKER_LOGIN_SUCCESS",
      resourceType: "Worker",
      resourceId: worker._id,
      metadata: { email: worker.email },
    });

    return res.status(200).json({
      message: "Login successful",
      accessToken,
      refreshToken,
      worker: {
        id: worker._id,
        name: worker.name,
        email: worker.email,
        phoneNumber: worker.phoneNumber,
        organization: worker.organization?._id || worker.organization,
        role: worker.role,
      },
    });
  } catch (error) {
    await logAuditEvent({
      req,
      action: "WORKER_LOGIN_FAILED",
      resourceType: "Worker",
      metadata: { email: req.body?.email, reason: error.message },
    });
    return res.status(error.status || 401).json({
      message: error.message || "Invalid credentials",
      code: error.code || "AUTH_FAILED",
    });
  }
};

const refreshSession = async (req, res) => {
  try {
    const rawRefreshToken = req.body.refreshToken || req.cookies?.refreshToken;
    if (!rawRefreshToken) {
      return res.status(401).json({ message: "Refresh token is required" });
    }

    const { accessToken, refreshToken } = await rotateRefreshToken(rawRefreshToken);

    res.cookie("token", accessToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "strict",
      maxAge: 15 * 60 * 1000,
    });

    res.cookie("refreshToken", refreshToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "strict",
      maxAge: 7 * 24 * 60 * 60 * 1000,
    });

    return res.status(200).json({
      message: "Tokens refreshed successfully",
      accessToken,
      refreshToken,
    });
  } catch (error) {
    return res.status(error.status || 401).json({
      message: error.message || "Failed to refresh token",
      code: error.code || "REFRESH_FAILED",
    });
  }
};

const forgotPassword = async (req, res) => {
  try {
    const { email } = req.body;
    if (!email) {
      return res.status(400).json({ message: "Email is required" });
    }
    const result = await handleForgotPassword(email);
    return res.status(200).json(result);
  } catch (error) {
    return res.status(error.status || 500).json({ message: error.message });
  }
};

const resetPassword = async (req, res) => {
  try {
    const { token, newPassword } = req.body;
    if (!token || !newPassword) {
      return res.status(400).json({ message: "Token and new password are required" });
    }
    if (newPassword.length < 8) {
      return res.status(400).json({ message: "Password must be at least 8 characters long" });
    }
    await handleResetPassword(token, newPassword);
    return res.status(200).json({ message: "Password reset successfully. You may now log in." });
  } catch (error) {
    return res.status(error.status || 400).json({ message: error.message });
  }
};

const logout = async (req, res) => {
  try {
    const rawRefreshToken = req.body?.refreshToken || req.cookies?.refreshToken;
    if (rawRefreshToken) {
      const tokenHash = hashToken(rawRefreshToken);
      await RefreshToken.updateOne({ tokenHash }, { isRevoked: true });
    } else if (req.user?.id) {
      await RefreshToken.updateMany({ userId: req.user.id }, { isRevoked: true });
    }
  } catch (err) {
    // Ignore revoke errors on logout
  }

  res.clearCookie("token", {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "strict",
  });
  res.clearCookie("refreshToken", {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "strict",
  });
  return res.status(200).json({ message: "Logged out successfully" });
};

export {
  createWorker,
  getWorkers,
  login,
  refreshSession,
  forgotPassword,
  resetPassword,
  logout,
  deleteWorker,
  reactivateWorker,
};
