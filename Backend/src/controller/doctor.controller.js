import { addDoctor, getDoctorsByAdmin, getAllDoctorsFromDB, loginDoctor, deleteDoctorById } from "../service/doctor.service.js";

// Admin deletes a doctor
const deleteDoctor = async (req, res) => {
    try {
        const { id } = req.params;
        const doctor = await deleteDoctorById(id);

        if (!doctor) {
            return res.status(404).json({ message: "Doctor not found" });
        }

        return res.status(200).json({ message: "Doctor deleted successfully" });
    } catch (error) {
        return res.status(500).json({ message: error.message });
    }
};

// Admin adds a doctor
const createDoctor = async (req, res) => {
    try {
        const { name, email, phoneNumber, password, specialization } = req.body;

        if (!name || !email || !phoneNumber || !password || !specialization) {
            return res.status(400).json({ message: "All fields are required" });
        }

        const doctor = await addDoctor(
            { name, email, phoneNumber, password, specialization },
            req.user.id  // adminId from JWT
        );

        return res.status(201).json({
            message: "Doctor added successfully",
            doctor: {
                id: doctor._id,
                name: doctor.name,
                email: doctor.email,
                phoneNumber: doctor.phoneNumber,
                specialization: doctor.specialization,
                isAvailable: doctor.isAvailable,
                addedBy: doctor.addedBy,
            },
        });
    } catch (error) {
        return res.status(400).json({ message: error.message });
    }
};

// Admin gets all doctors they added
const getDoctors = async (req, res) => {
    try {
        const doctors = await getDoctorsByAdmin(req.user.id);
        return res.status(200).json({ doctors });
    } catch (error) {
        return res.status(500).json({ message: error.message });
    }
};

import Worker from "../models/worker/workerSchema.js";

// Worker gets all doctors (for escalation)
const getAllDoctors = async (req, res) => {
    try {
        let adminId = null;
        if (req.user.role === "worker") {
            const worker = await Worker.findById(req.user.id);
            adminId = worker?.addedBy;
        }

        const doctors = await getAllDoctorsFromDB(adminId);
        return res.status(200).json({ doctors });
    } catch (error) {
        return res.status(500).json({ message: error.message });
    }
};

// Doctor login
const login = async (req, res) => {
    try {
        const { email, password } = req.body;

        if (!email || !password) {
            return res.status(400).json({ message: "Email and password are required" });
        }

        const { token, doctor } = await loginDoctor({ email, password });

        res.cookie("token", token, {
            httpOnly: true,
            secure: process.env.NODE_ENV === "production",
            sameSite: "strict",
            maxAge: 24 * 60 * 60 * 1000,
        });

        return res.status(200).json({
            message: "Login successful",
            doctor: {
                id: doctor._id,
                name: doctor.name,
                email: doctor.email,
                phoneNumber: doctor.phoneNumber,
                location: doctor.addedBy?.location,
                specialization: doctor.specialization,
            },
        });
    } catch (error) {
        return res.status(401).json({ message: error.message });
    }
};

// Doctor logout
const logout = (req, res) => {
    res.clearCookie("token", {
        httpOnly: true,
        secure: process.env.NODE_ENV === "production",
        sameSite: "strict",
    });
    return res.status(200).json({ message: "Logged out successfully" });
};

export { createDoctor, getDoctors, getAllDoctors, login, logout, deleteDoctor };
