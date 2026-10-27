import jwt from "jsonwebtoken";
import serverConfig from "../config/serverConfig.js";

/**
 * Authentication Middleware: Extracts token from Authorization header or httpOnly cookie.
 * Populates req.user with { id, role, organization }
 */
export const verifyToken = (roles = []) => {
  return (req, res, next) => {
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

      // Validate role permissions (case-insensitive whitelist matching)
      if (roles.length > 0) {
        const userRoleLower = (decoded.role || "").toLowerCase();
        const allowedRolesLower = roles.map((r) => r.toLowerCase());
        if (!allowedRolesLower.includes(userRoleLower)) {
          return res.status(403).json({ message: "Forbidden: Insufficient role permissions" });
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
