import Admin from "../models/admin/adminSchema.js";
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
    // Return dummy token or success message to prevent user enumeration
    return { message: "If that email exists, password reset instructions have been sent." };
  }
  const resetToken = await initiatePasswordReset(admin);
  return { message: "Password reset token generated.", resetToken };
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
