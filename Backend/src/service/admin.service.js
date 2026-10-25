import Admin from "../models/admin/adminSchema.js";
import bcrypt from "bcrypt";
import jwt from "jsonwebtoken";
import serverConfig from "../config/serverConfig.js";

const registerAdmin = async ({ name, email, phoneNumber, password, location }) => {
    const existing = await Admin.findOne({ $or: [{ email }, { phoneNumber }] });
    if (existing) {
        throw new Error("Admin with this email or phone number already exists");
    }

    const admin = await Admin.create({ name, email, phoneNumber, password, location });
    return admin;
};

const loginAdmin = async ({ email, password }) => {
    const admin = await Admin.findOne({ email });
    if (!admin) {
        throw new Error("Invalid email or password");
    }

    const isMatch = await bcrypt.compare(password, admin.password);
    if (!isMatch) {
        throw new Error("Invalid email or password");
    }

    const token = jwt.sign(
        { id: admin._id, role: "admin" },
        serverConfig.JWT_SECRET,
        { expiresIn: serverConfig.JWT_EXPIRY || "1d" }
    );

    return { token, admin };
};

export { registerAdmin, loginAdmin };
