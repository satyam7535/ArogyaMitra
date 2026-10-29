import AuditLog from "../models/audit/auditLogSchema.js";
import mongoose from "mongoose";

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
    if (mongoose.connection.readyState === 0) {
      if (process.env.NODE_ENV === "test") return;
      throw new Error("Audit log failure: Database is disconnected in non-test environment");
    }

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

export default logAuditEvent;
