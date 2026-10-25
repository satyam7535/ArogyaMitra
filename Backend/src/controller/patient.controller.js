import { createPatient, getPatientsByWorker, getPatientById } from "../service/patient.service.js";

// Worker registers a new patient
const registerPatient = async (req, res) => {
    try {
        const { name, age, gender, phoneNumber, address, medicalHistory } = req.body;

        if (!name || !age || !gender) {
            return res.status(400).json({ message: "Name, age, and gender are required" });
        }

        const patient = await createPatient(
            { name, age, gender, phoneNumber, address, medicalHistory },
            req.user.id // workerId from JWT
        );

        return res.status(201).json({ message: "Patient registered successfully", patient });
    } catch (error) {
        return res.status(500).json({ message: error.message });
    }
};

// Worker gets all their patients
const getPatients = async (req, res) => {
    try {
        const patients = await getPatientsByWorker(req.user.id);
        return res.status(200).json({ patients });
    } catch (error) {
        return res.status(500).json({ message: error.message });
    }
};

// Get a single patient
const getPatient = async (req, res) => {
    try {
        const patient = await getPatientById(req.params.id);
        if (!patient) return res.status(404).json({ message: "Patient not found" });
        return res.status(200).json({ patient });
    } catch (error) {
        return res.status(500).json({ message: error.message });
    }
};

export { registerPatient, getPatients, getPatient };
