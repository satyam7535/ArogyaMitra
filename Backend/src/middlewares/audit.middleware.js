import AuditLog from "../models/audit/auditLogSchema.js";

/**
 * Audit Logger Helper
 */
export const logAuditEvent = async ({
  req,
  action,
  resourceType,
  resourceId = null,
  metadata = {},
}) => {
  try {
    const userId = req?.user?.id || null;
    const userRole = req?.user?.role || "Anonymous";
    const organization = req?.user?.organization || req?.organization || null;
    const ipAddress =
      req?.headers["x-forwarded-for"] ||
      req?.socket?.remoteAddress ||
      req?.ip ||
      "unknown";

    await AuditLog.create({
      userId,
      userRole,
      action,
      resourceType,
      resourceId: resourceId ? String(resourceId) : null,
      organization,
      ipAddress,
      metadata,
    });
  } catch (err) {
    // Audit logging failure should not crash the main request flow, but log error
    console.error("Audit logging error:", err.message);
  }
};
