import Patient from "../models/patient/patientSchema.js";

// Worker registers a new patient in their organization
const createPatient = async (
  { name, age, gender, phoneNumber, address, medicalHistory },
  workerId,
  organization
) => {
  const patient = await Patient.create({
    name,
    age,
    gender,
    phoneNumber,
    address,
    medicalHistory,
    registeredBy: workerId,
    organization,
  });
  return patient.getDecrypted();
};

// Get all patients strictly within the user's organization
const getPatientsByOrg = async (organization) => {
  const patients = await Patient.find({ organization }).sort({ createdAt: -1 });
  return patients.map((p) => p.getDecrypted());
};

// Get a single patient strictly scoped to organization (returns null if cross-org)
const getPatientByIdScoped = async (patientId, organization) => {
  const patient = await Patient.findOne({ _id: patientId, organization });
  return patient ? patient.getDecrypted() : null;
};

export { createPatient, getPatientsByOrg, getPatientByIdScoped };
