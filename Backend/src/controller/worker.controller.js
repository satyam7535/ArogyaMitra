import { addWorker, getWorkersByAdmin, loginWorker, deleteWorkerById } from "../service/worker.service.js";

// Admin deletes a worker
const deleteWorker = async (req, res) => {
    try {
        const { id } = req.params;
        const worker = await deleteWorkerById(id);

        if (!worker) {
            return res.status(404).json({ message: "Worker not found" });
        }

        return res.status(200).json({ message: "Worker deleted successfully" });
    } catch (error) {
        return res.status(500).json({ message: error.message });
    }
};

// Admin adds a worker
const createWorker = async (req, res) => {
    try {
        const { name, email, phoneNumber, password } = req.body;

        if (!name || !email || !phoneNumber || !password) {
            return res.status(400).json({ message: "All fields are required" });
        }

        const worker = await addWorker(
            { name, email, phoneNumber, password },
            req.user.id  // adminId from JWT
        );

        return res.status(201).json({
            message: "Worker added successfully",
            worker: {
                id: worker._id,
                name: worker.name,
                email: worker.email,
                phoneNumber: worker.phoneNumber,
                addedBy: worker.addedBy,
            },
        });
    } catch (error) {
        return res.status(400).json({ message: error.message });
    }
};

// Admin gets all workers they added
const getWorkers = async (req, res) => {
    try {
        const workers = await getWorkersByAdmin(req.user.id);
        return res.status(200).json({ workers });
    } catch (error) {
        return res.status(500).json({ message: error.message });
    }
};

// Worker login
const login = async (req, res) => {
    try {
        const { email, password } = req.body;

        if (!email || !password) {
            return res.status(400).json({ message: "Email and password are required" });
        }

        const { token, worker } = await loginWorker({ email, password });

        res.cookie("token", token, {
            httpOnly: true,
            secure: process.env.NODE_ENV === "production",
            sameSite: "strict",
            maxAge: 24 * 60 * 60 * 1000,
        });

        return res.status(200).json({
            message: "Login successful",
            worker: {
                id: worker._id,
                name: worker.name,
                email: worker.email,
                phoneNumber: worker.phoneNumber,
                location: worker.addedBy?.location,
            },
        });
    } catch (error) {
        return res.status(401).json({ message: error.message });
    }
};

// Worker logout
const logout = (req, res) => {
    res.clearCookie("token", {
        httpOnly: true,
        secure: process.env.NODE_ENV === "production",
        sameSite: "strict",
    });
    return res.status(200).json({ message: "Logged out successfully" });
};

export { createWorker, getWorkers, login, logout, deleteWorker };
