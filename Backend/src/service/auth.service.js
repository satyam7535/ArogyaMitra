import jwt from "jsonwebtoken";
import serverConfig from "../config/serverConfig.js";
import RefreshToken from "../models/auth/refreshTokenSchema.js";
import { generateSecureToken, hashToken, verifyPassword } from "../utils/crypto.js";

/**
 * Generate Access Token & Refresh Token pair with family tracking
 */
export const generateTokenPair = async (user, userModel, existingFamilyId = null) => {
  const orgId = user.organization?._id
    ? user.organization._id.toString()
    : user.organization
    ? user.organization.toString()
    : null;

  const payload = {
    id: user._id.toString(),
    role: user.role,
    organization: orgId,
  };

  const accessToken = jwt.sign(payload, serverConfig.JWT_SECRET, {
    expiresIn: serverConfig.JWT_EXPIRY,
  });

  const rawRefreshToken = generateSecureToken(40);
  const tokenHash = hashToken(rawRefreshToken);
  const familyId = existingFamilyId || generateSecureToken(16);

  const expiresAt = new Date();
  expiresAt.setDate(expiresAt.getDate() + 7); // 7 days expiry

  await RefreshToken.create({
    tokenHash,
    userId: user._id,
    userModel,
    organization: orgId,
    familyId,
    expiresAt,
    isRevoked: false,
  });

  return { accessToken, refreshToken: rawRefreshToken };
};

/**
 * Rotate Refresh Token with Automatic Reuse Detection
 */
export const rotateRefreshToken = async (rawRefreshToken) => {
  if (!rawRefreshToken) {
    throw { status: 401, message: "No refresh token provided" };
  }

  const tokenHash = hashToken(rawRefreshToken);
  const tokenRecord = await RefreshToken.findOne({ tokenHash });

  if (!tokenRecord) {
    throw { status: 401, message: "Invalid refresh token" };
  }

  // Reuse Detection: If token is already revoked, compromise detected!
  if (tokenRecord.isRevoked) {
    // Invalidate entire token family immediately
    await RefreshToken.updateMany(
      { familyId: tokenRecord.familyId },
      { isRevoked: true }
    );
    throw {
      status: 401,
      message: "Refresh token reuse detected. All sessions in this family invalidated for security.",
      code: "TOKEN_REUSE_DETECTED",
    };
  }

  // Check expiration
  if (tokenRecord.expiresAt < new Date()) {
    throw { status: 401, message: "Refresh token has expired" };
  }

  // Revoke current token
  tokenRecord.isRevoked = true;
  await tokenRecord.save();

  // Load User model dynamically
  const Model = (await import(`../models/${tokenRecord.userModel.toLowerCase()}/${tokenRecord.userModel.toLowerCase()}Schema.js`)).default;
  const user = await Model.findById(tokenRecord.userId);
  if (!user) {
    throw { status: 401, message: "User not found" };
  }

  // Issue new token pair within the SAME family
  return await generateTokenPair(user, tokenRecord.userModel, tokenRecord.familyId);
};

/**
 * Handle Login with 5-attempt Account Lockout (15 mins)
 */
export const authenticateWithLockout = async (user, plainPassword) => {
  if (user.lockUntil && user.lockUntil > new Date()) {
    const remainingMinutes = Math.ceil((user.lockUntil - new Date()) / 60000);
    throw {
      status: 423,
      message: `Account is temporarily locked due to excessive failed attempts. Try again in ${remainingMinutes} minute(s).`,
      code: "ACCOUNT_LOCKED",
    };
  }

  const isValid = await verifyPassword(user.password, plainPassword);

  if (!isValid) {
    user.failedLoginAttempts = (user.failedLoginAttempts || 0) + 1;
    if (user.failedLoginAttempts >= 5) {
      user.lockUntil = new Date(Date.now() + 15 * 60 * 1000); // 15 mins
    }
    await user.save();

    const attemptsRemaining = Math.max(0, 5 - user.failedLoginAttempts);
    throw {
      status: 401,
      message: attemptsRemaining > 0
        ? `Invalid email or password. ${attemptsRemaining} attempt(s) remaining before account lockout.`
        : "Invalid email or password. Account has been locked for 15 minutes.",
      code: "INVALID_CREDENTIALS",
    };
  }

  // Reset lockout counters on success
  if (user.failedLoginAttempts > 0 || user.lockUntil) {
    user.failedLoginAttempts = 0;
    user.lockUntil = null;
    await user.save();
  }

  return true;
};

/**
 * Password Reset Flow
 */
export const initiatePasswordReset = async (user) => {
  const rawToken = generateSecureToken(32);
  user.resetPasswordToken = hashToken(rawToken);
  user.resetPasswordExpires = new Date(Date.now() + 15 * 60 * 1000); // 15 min expiry
  await user.save();
  return rawToken;
};

export const completePasswordReset = async (Model, rawToken, newPassword) => {
  const tokenHash = hashToken(rawToken);
  const user = await Model.findOne({
    resetPasswordToken: tokenHash,
    resetPasswordExpires: { $gt: new Date() },
  });

  if (!user) {
    throw { status: 400, message: "Password reset token is invalid or has expired." };
  }

  user.password = newPassword; // Pre-save hook hashes with Argon2id
  user.resetPasswordToken = null;
  user.resetPasswordExpires = null;
  user.failedLoginAttempts = 0;
  user.lockUntil = null;
  await user.save();

  // Revoke all existing refresh tokens
  await RefreshToken.updateMany({ userId: user._id }, { isRevoked: true });
  return user;
};
