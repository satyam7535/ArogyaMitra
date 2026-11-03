/**
 * ArogyaMitra — Clean Demo Data Reset Script
 * Clears out all consultations, patients, and audit records,
 * leaving only clean seed users (Admin, Worker, Doctor) and organizations.
 *
 * Run via: node src/scripts/resetDemoData.js
 */

import mongoose from "mongoose";
import dotenv from "dotenv";
import Organization from "../models/organization/organizationSchema.js";
import Admin from "../models/admin/adminSchema.js";
import Worker from "../models/worker/workerSchema.js";
import Doctor from "../models/doctor/doctorSchema.js";
import Patient from "../models/patient/patientSchema.js";
import Consultation from "../models/consultation/consultationSchema.js";
import AuditLog from "../models/audit/auditLogSchema.js";
import serverConfig from "../config/serverConfig.js";

dotenv.config();

const resetDemo = async () => {
  try {
    console.log("============================================================");
    console.log("  AROGYAMITRA DEMO DATA RESET");
    console.log("============================================================");
    console.log("Connecting to MongoDB:", serverConfig.DB_URL);
    await mongoose.connect(serverConfig.DB_URL);
    console.log("Connected to MongoDB successfully.\n");

    // 1. Delete all consultations, patients, and audit records
    const delConsultations = await Consultation.deleteMany({});
    console.log(`[+] Cleared consultations: ${delConsultations.deletedCount} removed.`);

    const delPatients = await Patient.deleteMany({});
    console.log(`[+] Cleared patients: ${delPatients.deletedCount} removed.`);

    const delAudits = await AuditLog.deleteMany({});
    console.log(`[+] Cleared audit logs: ${delAudits.deletedCount} removed.`);

    // 2. Unlock all seed users and reset failed attempts
    await Admin.updateMany({}, { failedLoginAttempts: 0, lockUntil: null });
    await Worker.updateMany({}, { failedLoginAttempts: 0, lockUntil: null });
    await Doctor.updateMany({}, { failedLoginAttempts: 0, lockUntil: null });
    console.log("[+] Reset failed login counters and locks for all users.");

    // 3. Verify counts
    const cCount = await Consultation.countDocuments();
    const pCount = await Patient.countDocuments();
    const aCount = await AuditLog.countDocuments();
    const uCount =
      (await Admin.countDocuments()) +
      (await Worker.countDocuments()) +
      (await Doctor.countDocuments());
    const oCount = await Organization.countDocuments();

    console.log("\n--- DEMO RESET SUMMARY ---");
    console.log(`Consultations in DB : ${cCount} (Clean 0-state)`);
    console.log(`Patients in DB      : ${pCount} (Clean 0-state)`);
    console.log(`Audit Logs in DB    : ${aCount} (Clean 0-state)`);
    console.log(`Seed Users Intact   : ${uCount}`);
    console.log(`Organizations Intact: ${oCount}`);
    console.log("============================================================\n");

    await mongoose.disconnect();
    console.log("Database connection closed. Demo environment is pristine.\n");
    process.exit(0);
  } catch (err) {
    console.error("[-] Demo reset error:", err.message);
    process.exit(1);
  }
};

resetDemo();
