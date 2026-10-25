import jwt from "jsonwebtoken";
import serverConfig from "../config/serverConfig.js";

const verifyToken = (roles = []) => {
    return (req, res, next) => {
        try {
            const token = req.cookies?.token;

            if (!token) {
                return res.status(401).json({ message: "Unauthorized: No token provided" });
            }

            const decoded = jwt.verify(token, serverConfig.JWT_SECRET);

            // If roles are specified, check if the user's role is allowed
            if (roles.length > 0 && !roles.includes(decoded.role)) {
                return res.status(403).json({ message: "Forbidden: Insufficient permissions" });
            }

            req.user = decoded; // { id, role }
            next();
        } catch (error) {
            return res.status(401).json({ message: "Unauthorized: Invalid or expired token" });
        }
    };
};

export default verifyToken;
