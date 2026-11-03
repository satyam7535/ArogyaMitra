/**
 * ArogyaMitra — 1-Command Comprehensive Demo Data Seeder
 * Provisions Organization, Admin, Health Worker, Medical Officer,
 * sample patients with AES-256-GCM encrypted PII, and full triage consultations.
 *
 * Run: node src/scripts/seedDemo.js
 */

import mongoose from "mongoose";
import dotenv from "dotenv";
import Organization from "../models/organization/organizationSchema.js";
import Admin from "../models/admin/adminSchema.js";
import Worker from "../models/worker/workerSchema.js";
import Doctor from "../models/doctor/doctorSchema.js";
import Patient from "../models/patient/patientSchema.js";
import Consultation from "../models/consultation/consultationSchema.js";
import serverConfig from "../config/serverConfig.js";

dotenv.config();

// Refuse to run demo seeding in production environment
if (process.env.NODE_ENV === "production") {
  throw new Error("SECURITY_ERROR: seedDemo.js cannot be executed in production (NODE_ENV=production).");
}

const seed = async () => {
  try {
    console.log("Connecting to MongoDB:", serverConfig.DB_URL);
    await mongoose.connect(serverConfig.DB_URL);
    console.log("Connected to MongoDB successfully.\n");

    // 1. Seed Organization 1 (Pune)
    let org = await Organization.findOne({ code: "PUNE-RHM" });
    if (!org) {
      org = await Organization.create({
        name: "Pune District Rural Health Mission",
        code: "PUNE-RHM",
        active: true,
      });
      console.log(`[+] Seeded Organization 1: ${org.name} (${org.code})`);
    } else {
      console.log(`[*] Organization 1 exists: ${org.name}`);
    }

    // Seed Organization 2 (Nashik - for cross-tenant scoping tests)
    let org2 = await Organization.findOne({ code: "NASHIK-RHM" });
    if (!org2) {
      org2 = await Organization.create({
        name: "Nashik Rural Health Mission",
        code: "NASHIK-RHM",
        active: true,
      });
      console.log(`[+] Seeded Organization 2: ${org2.name} (${org2.code})`);
    } else {
      console.log(`[*] Organization 2 exists: ${org2.name}`);
    }

    // 2. Seed Admin User (Org 1)
    let admin = await Admin.findOne({ email: "admin@arogyamitra.gov.in" });
    if (!admin) {
      admin = await Admin.create({
        name: "Dr. Vikram Kulkarni (Chief Medical Officer)",
        email: "admin@arogyamitra.gov.in",
        phoneNumber: "+91 98200 11111",
        location: "Pune PHC Central",
        password: "Admin@Arogya2026!",
        organization: org._id,
      });
      console.log(`[+] Seeded Admin: ${admin.email}`);
    } else {
      admin.password = "Admin@Arogya2026!";
      admin.failedLoginAttempts = 0;
      admin.lockUntil = null;
      await admin.save();
      console.log(`[*] Updated Admin password: ${admin.email}`);
    }

    // Seed Admin User (Org 2)
    let admin2 = await Admin.findOne({ email: "admin2@arogyamitra.gov.in" });
    if (!admin2) {
      admin2 = await Admin.create({
        name: "Dr. Rajesh Shinde (Nashik CMO)",
        email: "admin2@arogyamitra.gov.in",
        phoneNumber: "+91 98200 11112",
        location: "Nashik Sub-center",
        password: "Admin@Arogya2026!",
        organization: org2._id,
      });
      console.log(`[+] Seeded Admin 2: ${admin2.email}`);
    } else {
      admin2.password = "Admin@Arogya2026!";
      admin2.failedLoginAttempts = 0;
      admin2.lockUntil = null;
      await admin2.save();
      console.log(`[*] Updated Admin 2 password: ${admin2.email}`);
    }

    // 3. Seed Worker User (Org 1)
    let worker = await Worker.findOne({ email: "worker@arogyamitra.gov.in" });
    if (!worker) {
      worker = await Worker.create({
        name: "Sunita Patil (ASHA Lead)",
        email: "worker@arogyamitra.gov.in",
        phoneNumber: "+91 98200 22221",
        password: "Worker@Arogya2026!",
        organization: org._id,
        addedBy: admin._id,
      });
      console.log(`[+] Seeded Health Worker 1: ${worker.email}`);
    } else {
      worker.password = "Worker@Arogya2026!";
      worker.failedLoginAttempts = 0;
      worker.lockUntil = null;
      await worker.save();
      console.log(`[*] Updated Health Worker 1 password: ${worker.email}`);
    }

    // Seed Worker User (Org 2)
    let worker2 = await Worker.findOne({ email: "worker2@arogyamitra.gov.in" });
    if (!worker2) {
      worker2 = await Worker.create({
        name: "Anita Deshmukh (ASHA Lead Nashik)",
        email: "worker2@arogyamitra.gov.in",
        phoneNumber: "+91 98200 22222",
        password: "Worker@Arogya2026!",
        organization: org2._id,
        addedBy: admin2._id,
      });
      console.log(`[+] Seeded Health Worker 2: ${worker2.email}`);
    } else {
      worker2.password = "Worker@Arogya2026!";
      worker2.failedLoginAttempts = 0;
      worker2.lockUntil = null;
      await worker2.save();
      console.log(`[*] Updated Health Worker 2 password: ${worker2.email}`);
    }

    // 4. Seed Doctor User (Org 1)
    let doctor = await Doctor.findOne({ email: "doctor@arogyamitra.gov.in" });
    if (!doctor) {
      doctor = await Doctor.create({
        name: "Dr. Anand Joshi (Medical Officer)",
        email: "doctor@arogyamitra.gov.in",
        phoneNumber: "+91 98200 33331",
        specialization: "General Medicine",
        password: "Doctor@Arogya2026!",
        organization: org._id,
        addedBy: admin._id,
      });
      console.log(`[+] Seeded Doctor 1: ${doctor.email}`);
    } else {
      doctor.password = "Doctor@Arogya2026!";
      doctor.failedLoginAttempts = 0;
      doctor.lockUntil = null;
      await doctor.save();
      console.log(`[*] Updated Doctor 1 password: ${doctor.email}`);
    }

    // Seed Doctor User (Org 2)
    let doctor2 = await Doctor.findOne({ email: "doctor2@arogyamitra.gov.in" });
    if (!doctor2) {
      doctor2 = await Doctor.create({
        name: "Dr. Sneha Rao (Medical Officer Nashik)",
        email: "doctor2@arogyamitra.gov.in",
        phoneNumber: "+91 98200 33332",
        specialization: "Pediatrics",
        password: "Doctor@Arogya2026!",
        organization: org2._id,
        addedBy: admin2._id,
      });
      console.log(`[+] Seeded Doctor 2: ${doctor2.email}`);
    } else {
      doctor2.password = "Doctor@Arogya2026!";
      doctor2.failedLoginAttempts = 0;
      doctor2.lockUntil = null;
      await doctor2.save();
      console.log(`[*] Updated Doctor 2 password: ${doctor2.email}`);
    }

    // 5. Seed Patients with AES-256-GCM Encrypted PII
    let p1 = await Patient.findOne({ name: "Kavita Devi", organization: org._id });
    if (!p1) {
      p1 = await Patient.create({
        name: "Kavita Devi",
        age: 42,
        gender: "female",
        phoneNumber: "+91 98765 43210",
        address: "House 42, Khed Village, Pune, Maharashtra",
        organization: org._id,
        registeredBy: worker._id,
        medicalHistory: "Mild hypertension managed by lifestyle. No known drug allergies.",
      });
      console.log(`[+] Seeded Patient 1 (Org 1): ${p1.name}`);
    }

    let p2 = await Patient.findOne({ name: "Ramesh Shinde", organization: org._id });
    if (!p2) {
      p2 = await Patient.create({
        name: "Ramesh Shinde",
        age: 48,
        gender: "male",
        phoneNumber: "+91 91234 56789",
        address: "Plot 12, Pali Sub-Centre, Raigad, Maharashtra",
        organization: org._id,
        registeredBy: worker._id,
        medicalHistory: "History of seasonal malaria 2 years ago.",
      });
      console.log(`[+] Seeded Patient 2 (Org 1): ${p2.name}`);
    }

    let p3 = await Patient.findOne({ name: "Sanjay More", organization: org2._id });
    if (!p3) {
      p3 = await Patient.create({
        name: "Sanjay More",
        age: 35,
        gender: "male",
        phoneNumber: "+91 94220 54321",
        address: "Ward 4, Igatpuri, Nashik, Maharashtra",
        organization: org2._id,
        registeredBy: worker2._id,
        medicalHistory: "No prior chronic medical conditions.",
      });
      console.log(`[+] Seeded Patient 3 (Org 2): ${p3.name}`);
    }

    // 6. Seed Consultations
    let c1 = await Consultation.findOne({ patient: p1._id });
    if (!c1) {
      c1 = await Consultation.create({
        patient: p1._id,
        submittedBy: worker._id,
        assignedDoctor: doctor._id,
        organization: org._id,
        symptoms: ["itching", "skin_rash", "nodal_skin_eruptions"],
        notes: "Patient reports intense pruritus and localized rash on arms.",
        status: "analyzed",
        mlAnalysis: {
          disease: "Fungal infection",
          confidence: 0.924,
          severityScore: 2.5,
          precautions: ["bath twice", "use clean clothes", "avoid sharing towels"],
          description: "Common superficial dermatomycosis.",
          analyzedAt: new Date(),
        },
        llmAnalysis: {
          summary: "Patient displays classic presentation of cutaneous fungal infection.",
          recommendations: "Apply topical antifungal cream twice daily for 14 days.",
          referral: "Routine outpatient follow-up if rash does not resolve within 2 weeks.",
          riskLevel: "low",
          llmFallback: false,
          analyzedAt: new Date(),
        },
        workerDecision: "accepted",
      });
      console.log(`[+] Seeded Consultation #1: Fungal Infection (Accepted by Worker)`);
    }

    let c2 = await Consultation.findOne({ patient: p2._id });
    if (!c2) {
      c2 = await Consultation.create({
        patient: p2._id,
        submittedBy: worker._id,
        assignedDoctor: doctor._id,
        organization: org._id,
        symptoms: ["chills", "vomiting", "high_fever", "sweating", "headache"],
        notes: "High spiking fever with severe rigors. Patient is very weak and dehydrated.",
        status: "reviewed",
        mlAnalysis: {
          disease: "Malaria",
          confidence: 0.885,
          severityScore: 3.8,
          precautions: ["use mosquito net", "drink boiled water", "take anti-malarials"],
          description: "Plasmodium parasite infection transmitted via Anopheles mosquito bite.",
          analyzedAt: new Date(),
        },
        llmAnalysis: {
          summary: "Acute febrile illness consistent with Plasmodium vivax / falciparum malaria.",
          recommendations: "Immediate RDT / Peripheral smear for MP. Rehydrate orally.",
          referral: "Medical Officer review within 24 hours.",
          riskLevel: "high",
          llmFallback: false,
          analyzedAt: new Date(),
        },
        workerDecision: "escalated",
        escalationReason: "High clinical severity score (3.8) and risk of malarial complications.",
        secondOpinion: {
          diagnosis: "Confirmed Acute Uncomplicated Vivax Malaria",
          recommendation: "Prescribed Tab Paracetamol 650mg TDS x 3 days, Tab Chloroquine 600mg base stat, followed by 300mg at 6h, 24h, 48h as per NVBDCP guidelines. CBC & MP smear ordered.",
          respondedAt: new Date(),
        },
      });
      console.log(`[+] Seeded Consultation #2: Malaria (Escalated & Reviewed with Second Opinion)`);
    }

    console.log("\n=======================================================");
    console.log("   🎉 AROGYAMITRA DEMO SEEDING COMPLETED SUCCESSFULLY   ");
    console.log("=======================================================");
    console.log("ORGANIZATION: Pune District Rural Health Mission (PUNE-RHM)");
    console.log("-------------------------------------------------------");
    console.log("ROLE       | EMAIL                       | PASSWORD");
    console.log("-------------------------------------------------------");
    console.log("Admin      | admin@arogyamitra.gov.in    | Admin@Arogya2026!");
    console.log("Worker     | worker@arogyamitra.gov.in   | Worker@Arogya2026!");
    console.log("Doctor     | doctor@arogyamitra.gov.in   | Doctor@Arogya2026!");
    console.log("-------------------------------------------------------");
    console.log("Streamlit Frontend : http://localhost:8501");
    console.log("Backend API        : http://localhost:5000");
    console.log("ML Microservice    : http://localhost:8000");
    console.log("Graph AI Pipeline  : http://localhost:8001");
    console.log("=======================================================\n");

    process.exit(0);
  } catch (err) {
    console.error("Seeding error:", err);
    process.exit(1);
  }
};

seed();
