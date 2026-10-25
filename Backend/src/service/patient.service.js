import Patient from "../models/patient/patientSchema.js";

// Worker registers a new patient
const createPatient = async ({ name, age, gender, phoneNumber, address, medicalHistory }, workerId) => {
    const patient = await Patient.create({
        name,
        age,
        gender,
        phoneNumber,
        address,
        medicalHistory,
        registeredBy: workerId,
    });
    return patient;
};

import Worker from "../models/worker/workerSchema.js";

// Get all patients belong to the same admin organization
const getPatientsByWorker = async (workerId) => {
    const worker = await Worker.findById(workerId);
    if (!worker) return [];

    // Find all workers under the same admin
    const workers = await Worker.find({ addedBy: worker.addedBy }).select("_id");
    const workerIds = workers.map(w => w._id);

    return await Patient.find({ registeredBy: { $in: workerIds } }).sort({ createdAt: -1 });
};

// Get a single patient by ID
const getPatientById = async (patientId) => {
    return await Patient.findById(patientId);
};

export { createPatient, getPatientsByWorker, getPatientById };
