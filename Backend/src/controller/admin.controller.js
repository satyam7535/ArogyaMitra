import { registerAdmin, loginAdmin } from "../service/admin.service.js";

const register = async (req, res) => {
    try {
        const { name, email, phoneNumber, password, location } = req.body;

        if (!name || !email || !phoneNumber || !password || !location) {
            return res.status(400).json({ message: "All fields are required" });
        }

        const admin = await registerAdmin({ name, email, phoneNumber, password, location });

        return res.status(201).json({
            message: "Admin registered successfully",
            admin: {
                id: admin._id,
                name: admin.name,
                email: admin.email,
                location: admin.location,
                phoneNumber: admin.phoneNumber,
            },
        });
    } catch (error) {
        return res.status(400).json({ message: error.message });
    }
};

const login = async (req, res) => {
    try {
        const { email, password } = req.body;

        if(!email || !password) {
            return res.status(400).json({ message: "Email and password are required" });
        }

        const { token, admin } = await loginAdmin({ email, password });

        res.cookie("token", token, {
            httpOnly: true,
            secure: process.env.NODE_ENV === "production",
            sameSite: "strict",
            maxAge: 24 * 60 * 60 * 1000, // 1 day in ms
        });

        return res.status(200).json({
            message: "Login successful",
            admin: {
                id: admin._id,
                name: admin.name,
                email: admin.email,
                location: admin.location,
                phoneNumber: admin.phoneNumber,
            },
        });
    } catch (error) {
        return res.status(401).json({ message: error.message });
    }
};

const logout = (req, res) => {
    res.clearCookie("token", {
        httpOnly: true,
        secure: process.env.NODE_ENV === "production",
        sameSite: "strict",
    });
    return res.status(200).json({ message: "Logged out successfully" });
};

const getProfile = (req, res) => {
    // req.user is set by auth middleware
    return res.status(200).json({ user: req.user });
};

export { register, login, logout, getProfile };
