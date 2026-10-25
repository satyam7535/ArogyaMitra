import Doctor from "../models/doctor/doctorSchema.js";
import bcrypt from "bcrypt";
import jwt from "jsonwebtoken";
import serverConfig from "../config/serverConfig.js";

// Called by admin to add a new doctor
const addDoctor = async ({ name, email, phoneNumber, password, specialization }, adminId) => {
    const existing = await Doctor.findOne({ $or: [{ email }, { phoneNumber }] });
    if (existing) {
        throw new Error("Doctor with this email or phone number already exists");
    }

    const doctor = await Doctor.create({
        name,
        email,
        phoneNumber,
        password,
        specialization,
        addedBy: adminId,
    });

    return doctor;
};

// Get all doctors added by a specific admin
const getDoctorsByAdmin = async (adminId) => {
    return await Doctor.find({ addedBy: adminId }).select("-password");
};

// Doctor login
const loginDoctor = async ({ email, password }) => {
    const doctor = await Doctor.findOne({ email }).populate("addedBy");
    if (!doctor) {
        throw new Error("Invalid email or password");
    }

    const isMatch = await bcrypt.compare(password, doctor.password);
    if (!isMatch) {
        throw new Error("Invalid email or password");
    }

    const token = jwt.sign(
        { id: doctor._id, role: "doctor" },
        serverConfig.JWT_SECRET,
        { expiresIn: serverConfig.JWT_EXPIRY || "1d" }
    );

    return { token, doctor };
};

// Delete a doctor by ID
const deleteDoctorById = async (doctorId) => {
    return await Doctor.findByIdAndDelete(doctorId);
};

// Get ALL doctors (filtered by admin if provided)
const getAllDoctorsFromDB = async (adminId = null) => {
    const query = adminId ? { addedBy: adminId } : {};
    return await Doctor.find(query).select("-password").sort({ name: 1 });
};

export { addDoctor, getDoctorsByAdmin, getAllDoctorsFromDB, loginDoctor, deleteDoctorById };
