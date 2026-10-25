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
import { hashPassword, encryptField } from "../utils/crypto.js";
import serverConfig from "../config/serverConfig.js";

dotenv.config();

const seed = async () => {
  try {
    console.log("Connecting to MongoDB:", serverConfig.DB_URL);
    await mongoose.connect(serverConfig.DB_URL);
    console.log("Connected to MongoDB successfully.\n");

    // 1. Seed Organization
    let org = await Organization.findOne({ code: "PUNE-RHM" });
    if (!org) {
      org = await Organization.create({
        name: "Pune District Rural Health Mission",
        code: "PUNE-RHM",
        type: "phc",
        district: "Pune",
        state: "Maharashtra",
      });
      console.log(`[+] Seeded Organization: ${org.name} (${org.code})`);
    } else {
      console.log(`[*] Organization exists: ${org.name}`);
    }

    // 2. Seed Admin User
    let admin = await Admin.findOne({ email: "admin@arogyamitra.gov.in" });
    if (!admin) {
      const hashedPassword = await hashPassword("Admin@Arogya2026!");
      admin = await Admin.create({
        name: "Dr. Vikram Kulkarni (Chief Medical Officer)",
        email: "admin@arogyamitra.gov.in",
        password: hashedPassword,
        organization: org._id,
      });
      console.log(`[+] Seeded Admin: ${admin.email}`);
    }

    // 3. Seed Worker User
    let worker = await Worker.findOne({ email: "worker@arogyamitra.gov.in" });
    if (!worker) {
      const hashedPassword = await hashPassword("Worker@Arogya2026!");
      worker = await Worker.create({
        name: "Sunita Patil (ASHA Lead)",
        email: "worker@arogyamitra.gov.in",
        password: hashedPassword,
        organization: org._id,
      });
      console.log(`[+] Seeded Health Worker: ${worker.email}`);
    }

    // 4. Seed Doctor User
    let doctor = await Doctor.findOne({ email: "doctor@arogyamitra.gov.in" });
    if (!doctor) {
      const hashedPassword = await hashPassword("Doctor@Arogya2026!");
      doctor = await Doctor.create({
        name: "Dr. Anand Joshi (Medical Officer)",
        email: "doctor@arogyamitra.gov.in",
        password: hashedPassword,
        organization: org._id,
      });
      console.log(`[+] Seeded Doctor: ${doctor.email}`);
    }

    // 5. Seed Patients with AES-256-GCM Encrypted PII
    let p1 = await Patient.findOne({ name: "Kavita Devi", organization: org._id });
    if (!p1) {
      p1 = await Patient.create({
        name: "Kavita Devi",
        age: 42,
        gender: "female",
        phone: encryptField("+91 98765 43210"),
        address: encryptField("House 42, Khed Village, Pune, Maharashtra"),
        organization: org._id,
        registeredBy: worker._id,
        medicalHistory: "Mild hypertension managed by lifestyle. No known drug allergies.",
      });
      console.log(`[+] Seeded Patient: ${p1.name} (PII Encrypted with AES-256-GCM)`);
    }

    let p2 = await Patient.findOne({ name: "Ramesh Shinde", organization: org._id });
    if (!p2) {
      p2 = await Patient.create({
        name: "Ramesh Shinde",
        age: 48,
        gender: "male",
        phone: encryptField("+91 91234 56789"),
        address: encryptField("Plot 12, Pali Sub-Centre, Raigad, Maharashtra"),
        organization: org._id,
        registeredBy: worker._id,
        medicalHistory: "History of seasonal malaria 2 years ago.",
      });
      console.log(`[+] Seeded Patient: ${p2.name} (PII Encrypted with AES-256-GCM)`);
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
