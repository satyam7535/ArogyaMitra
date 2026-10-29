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
