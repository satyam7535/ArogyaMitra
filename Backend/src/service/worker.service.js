import Worker from "../models/worker/workerSchema.js";
import bcrypt from "bcrypt";
import jwt from "jsonwebtoken";
import serverConfig from "../config/serverConfig.js";

// Called by admin to add a new worker
const addWorker = async ({ name, email, phoneNumber, password }, adminId) => {
    const existing = await Worker.findOne({ $or: [{ email }, { phoneNumber }] });
    if (existing) {
        throw new Error("Worker with this email or phone number already exists");
    }

    const worker = await Worker.create({
        name,
        email,
        phoneNumber,
        password,
        addedBy: adminId,
    });

    return worker;
};

// Get all workers added by a specific admin
const getWorkersByAdmin = async (adminId) => {
    return await Worker.find({ addedBy: adminId }).select("-password");
};

// Worker login
const loginWorker = async ({ email, password }) => {
    const worker = await Worker.findOne({ email }).populate("addedBy");
    if (!worker) {
        throw new Error("Invalid email or password");
    }

    const isMatch = await bcrypt.compare(password, worker.password);
    if (!isMatch) {
        throw new Error("Invalid email or password");
    }

    const token = jwt.sign(
        { id: worker._id, role: "worker" },
        serverConfig.JWT_SECRET,
        { expiresIn: serverConfig.JWT_EXPIRY || "1d" }
    );

    return { token, worker };
};

// Delete a worker by ID
const deleteWorkerById = async (workerId) => {
    return await Worker.findByIdAndDelete(workerId);
};

export { addWorker, getWorkersByAdmin, loginWorker, deleteWorkerById };
