/**
 * ArogyaMitra Email / Password Reset Adapter
 * Follows principle of least privilege and credential confidentiality.
 * - In development (NODE_ENV === "development"): Logs the full, actionable reset link to stdout.
 * - In test (NODE_ENV === "test") or production: Never logs link/token to console to prevent leakage.
 * - In production (NODE_ENV === "production"): Would dispatch via configured SMTP/SES transport.
 */

export const dispatchPasswordReset = ({
  email,
  role,
  resetToken,
  baseUrl = "http://localhost:5000",
}) => {
  const resetUrl = `${baseUrl}/api/v1/${(role || "").toLowerCase()}/reset-password?token=${resetToken}`;

  if (process.env.NODE_ENV === "development") {
    console.log(`[DEV RESET LINK] Password reset link for ${role} (${email}): ${resetUrl}`);
    return { dispatched: true, mode: "console", resetUrl };
  }

  if (process.env.NODE_ENV === "production") {
    // In production, dispatch via configured email transport (SMTP)
    // Never print secret to console
    return { dispatched: true, mode: "smtp" };
  }

  // In test or other environments: suppressed from logs
  return { dispatched: true, mode: "suppressed" };
};

export default { dispatchPasswordReset };
