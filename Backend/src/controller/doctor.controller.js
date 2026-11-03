import {
  addDoctor,
  getDoctorsByOrg,
  getAllDoctorsFromDB,
  loginDoctor,
  deleteDoctorScoped,
  reactivateDoctorScoped,
  handleForgotPassword,
  handleResetPassword,
  rotateRefreshToken,
} from "../service/doctor.service.js";
import { logAuditEvent } from "../middlewares/audit.middleware.js";
import RefreshToken from "../models/auth/refreshTokenSchema.js";
import { hashToken } from "../utils/crypto.js";

// Admin soft-deactivates a doctor (strictly scoped to admin's organization)
const deleteDoctor = async (req, res) => {
  try {
    const { id } = req.params;
    const doctor = await deleteDoctorScoped(id, req.user.organization, req.user.id);

    if (!doctor) {
      return res.status(404).json({ message: "Doctor not found" });
    }

    await logAuditEvent({
      req,
      action: "DOCTOR_DEACTIVATED",
      resourceType: "Doctor",
      resourceId: id,
    });

    return res.status(200).json({ message: "Doctor deactivated successfully", doctor });
  } catch (error) {
    return res.status(500).json({ message: error.message });
  }
};

// Admin reactivates a doctor
const reactivateDoctor = async (req, res) => {
  try {
    const { id } = req.params;
    const doctor = await reactivateDoctorScoped(id, req.user.organization);

    if (!doctor) {
      return res.status(404).json({ message: "Doctor not found" });
    }

    await logAuditEvent({
      req,
      action: "DOCTOR_REACTIVATED",
      resourceType: "Doctor",
      resourceId: id,
    });

    return res.status(200).json({ message: "Doctor reactivated successfully", doctor });
  } catch (error) {
    return res.status(500).json({ message: error.message });
  }
};

// Admin adds a doctor (inherits admin's organization)
const createDoctor = async (req, res) => {
  try {
    const { name, email, phoneNumber, password, specialization } = req.body;

    if (!name || !email || !phoneNumber || !password || !specialization) {
      return res.status(400).json({ message: "All fields are required" });
    }

    const doctor = await addDoctor(
      { name, email, phoneNumber, password, specialization },
      req.user.id,
      req.user.organization
    );

    await logAuditEvent({
      req,
      action: "DOCTOR_CREATED",
      resourceType: "Doctor",
      resourceId: doctor._id,
      metadata: { email: doctor.email },
    });

    return res.status(201).json({
      message: "Doctor added successfully",
      doctor: {
        id: doctor._id,
        name: doctor.name,
        email: doctor.email,
        phoneNumber: doctor.phoneNumber,
        specialization: doctor.specialization,
        organization: doctor.organization,
        isAvailable: doctor.isAvailable,
        addedBy: doctor.addedBy,
      },
    });
  } catch (error) {
    return res.status(error.status || 400).json({ message: error.message });
  }
};

// Admin gets all doctors in their organization
const getDoctors = async (req, res) => {
  try {
    const doctors = await getDoctorsByOrg(req.user.organization);
    return res.status(200).json({ doctors });
  } catch (error) {
    return res.status(500).json({ message: error.message });
  }
};

// Worker or Admin gets doctors within their organization (for escalation dropdown)
const getAllDoctors = async (req, res) => {
  try {
    const doctors = await getAllDoctorsFromDB(req.user.organization);
    return res.status(200).json({ doctors });
  } catch (error) {
    return res.status(500).json({ message: error.message });
  }
};

// Doctor login
const login = async (req, res) => {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      return res.status(400).json({ message: "Email and password are required" });
    }

    const { accessToken, refreshToken, doctor } = await loginDoctor({ email, password });

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
      action: "DOCTOR_LOGIN_SUCCESS",
      resourceType: "Doctor",
      resourceId: doctor._id,
      metadata: { email: doctor.email },
    });

    return res.status(200).json({
      message: "Login successful",
      accessToken,
      refreshToken,
      doctor: {
        id: doctor._id,
        name: doctor.name,
        email: doctor.email,
        phoneNumber: doctor.phoneNumber,
        specialization: doctor.specialization,
        organization: doctor.organization?._id || doctor.organization,
        role: doctor.role,
      },
    });
  } catch (error) {
    await logAuditEvent({
      req,
      action: "DOCTOR_LOGIN_FAILED",
      resourceType: "Doctor",
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
  createDoctor,
  getDoctors,
  getAllDoctors,
  login,
  refreshSession,
  forgotPassword,
  resetPassword,
  logout,
  deleteDoctor,
  reactivateDoctor,
};
