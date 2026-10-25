import {
  loginAdmin,
  handleForgotPassword,
  handleResetPassword,
  rotateRefreshToken,
} from "../service/admin.service.js";
import { logAuditEvent } from "../middlewares/audit.middleware.js";

// Public self-registration disabled
const register = (req, res) => {
  return res.status(403).json({
    message: "Public administrator registration is disabled for security. Use the seedAdmin CLI script or invite.",
    code: "REGISTRATION_DISABLED",
  });
};

const login = async (req, res) => {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      return res.status(400).json({ message: "Email and password are required" });
    }

    const { accessToken, refreshToken, admin } = await loginAdmin({ email, password });

    // Set secure HTTP-only cookies
    res.cookie("token", accessToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "strict",
      maxAge: 15 * 60 * 1000, // 15 mins
    });

    res.cookie("refreshToken", refreshToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "strict",
      maxAge: 7 * 24 * 60 * 60 * 1000, // 7 days
    });

    await logAuditEvent({
      req,
      action: "ADMIN_LOGIN_SUCCESS",
      resourceType: "Admin",
      resourceId: admin._id,
      metadata: { email: admin.email },
    });

    return res.status(200).json({
      message: "Login successful",
      accessToken,
      refreshToken,
      admin: {
        id: admin._id,
        name: admin.name,
        email: admin.email,
        location: admin.location,
        phoneNumber: admin.phoneNumber,
        organization: admin.organization,
        role: admin.role,
      },
    });
  } catch (error) {
    await logAuditEvent({
      req,
      action: "ADMIN_LOGIN_FAILED",
      resourceType: "Admin",
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

const logout = (req, res) => {
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

const getProfile = (req, res) => {
  return res.status(200).json({ user: req.user });
};

export {
  register,
  login,
  refreshSession,
  forgotPassword,
  resetPassword,
  logout,
  getProfile,
};
