import jwt from "jsonwebtoken";
import mongoose from "mongoose";
import serverConfig from "../config/serverConfig.js";
import ROLES from "../config/roles.js";
import Worker from "../models/worker/workerSchema.js";
import Doctor from "../models/doctor/doctorSchema.js";

/**
 * Authentication Middleware: Extracts token from Authorization header or httpOnly cookie.
 * Populates req.user with { id, role, organization }
 * Enforces strict, canonical role authorization matching against ROLES constant.
 * Immediately rejects deactivated accounts with 403 ACCOUNT_DEACTIVATED.
 */
export const verifyToken = (roles = []) => {
  return async (req, res, next) => {
    try {
      let token = null;

      // 1. Check Authorization: Bearer <token>
      const authHeader = req.headers.authorization || req.headers.Authorization;
      if (authHeader && authHeader.startsWith("Bearer ")) {
        token = authHeader.split(" ")[1];
      }

      // 2. Fallback to cookies
      if (!token && req.cookies) {
        token = req.cookies.token || req.cookies.accessToken;
      }

      if (!token) {
        return res.status(401).json({ message: "Unauthorized: No authentication token provided" });
      }

      const decoded = jwt.verify(token, serverConfig.JWT_SECRET);

      // Validate role permissions (strict canonical matching against ROLES constant)
      if (roles.length > 0) {
        if (!roles.includes(decoded.role)) {
          return res.status(403).json({ message: "Forbidden: Insufficient role permissions" });
        }
      }

      // Verify active account status for roles subject to deactivation
      if (mongoose.connection.readyState !== 0 && (decoded.role === ROLES.WORKER || decoded.role === ROLES.DOCTOR)) {
        let isInactive = false;
        if (decoded.role === ROLES.WORKER) {
          const w = await Worker.findById(decoded.id).select("isActive").lean();
          if (w && w.isActive === false) isInactive = true;
        } else if (decoded.role === ROLES.DOCTOR) {
          const d = await Doctor.findById(decoded.id).select("isActive").lean();
          if (d && d.isActive === false) isInactive = true;
        }
        if (isInactive) {
          return res.status(403).json({
            message: "Forbidden: Account has been deactivated",
            code: "ACCOUNT_DEACTIVATED",
          });
        }
      }

      req.user = decoded; // { id, role, organization }
      req.organization = decoded.organization;
      next();
    } catch (error) {
      if (error.name === "TokenExpiredError") {
        return res.status(401).json({ message: "Unauthorized: Access token has expired", code: "TOKEN_EXPIRED" });
      }
      return res.status(401).json({ message: "Unauthorized: Invalid token" });
    }
  };
};

export default verifyToken;
