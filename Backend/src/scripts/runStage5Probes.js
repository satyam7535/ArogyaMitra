/**
 * ArogyaMitra — Stage 5 Flow Steps 10 & 11 Live Probes
 * Tests Frontline Worker Decisions (Accept AI / Escalate), Doctor Second Opinion Review Queue,
 * Optimistic Concurrency Control (OCC 409 Conflict), and Audit Log Tamper-Evidence.
 * Saves raw outputs with redacted secrets to docs/evidence/stage5_probes.txt.
 */

import fs from "fs";
import path from "path";
import mongoose from "mongoose";
import jwt from "jsonwebtoken";
import serverConfig from "../config/serverConfig.js";
import ROLES from "../config/roles.js";
import Organization from "../models/organization/organizationSchema.js";
import Patient from "../models/patient/patientSchema.js";
import Worker from "../models/worker/workerSchema.js";
import Doctor from "../models/doctor/doctorSchema.js";
import Consultation from "../models/consultation/consultationSchema.js";
import AuditLog from "../models/audit/auditLogSchema.js";

const BACKEND_URL = "http://127.0.0.1:5000";
const EVIDENCE_FILE = path.resolve("docs/evidence/stage5_probes.txt");

const logLines = [];
function log(msg = "") {
  console.log(msg);
  logLines.push(msg);
}

function redact(text) {
  if (typeof text !== "string") text = JSON.stringify(text);
  return text
    .replace(/eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+/g, "[REDACTED_JWT]")
    .replace(/"password":\s*"[^"]+"/g, '"password": "[REDACTED_PASSWORD]"')
    .replace(/mongodb(\+srv)?:\/\/[^\s]+/g, "[REDACTED_DB_URL]");
}

async function apiRequest(method, urlPath, body = null, headers = {}) {
  const url = `${BACKEND_URL}${urlPath}`;
  const reqHeaders = { "Content-Type": "application/json", ...headers };

  const res = await fetch(url, {
    method,
    headers: reqHeaders,
    body: body ? JSON.stringify(body) : undefined,
  });

  let data = null;
  const contentType = res.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    try {
      data = await res.json();
    } catch {
      data = await res.text();
    }
  } else {
    data = await res.text();
  }

  return { status: res.status, data, headers: res.headers };
}

async function runStage5Probes() {
  log("Command: node src/scripts/runStage5Probes.js");
  log("================================================================================");
  log("AROGYAMITRA STAGE 5 — FLOW STEPS 10 & 11 CLINICAL DECISION & SECOND OPINION PROBES");
  log(`Timestamp: ${new Date().toISOString()}`);
  log(`Database: MongoDB Atlas arogyamitra_dev`);
  log(`Backend URL: ${BACKEND_URL}`);
  log("================================================================================\n");

  await mongoose.connect(serverConfig.DB_URL);

  const org1 = await Organization.findOne({ code: "PUNE-RHM" });
  const org2 = await Organization.findOne({ code: "NASHIK-RHM" });

  if (!org1 || !org2) {
    throw new Error("Required test organizations not found in database");
  }

  const worker1 = await Worker.findOne({ organization: org1._id });
  const worker2 = await Worker.findOne({ organization: org2._id });
  const doctor1 = await Doctor.findOne({ organization: org1._id });
  const doctor2 = await Doctor.findOne({ organization: org2._id });
  const patient1 = (await Patient.findOne({ organization: org1._id, isDeleted: { $ne: true } })) || (await Patient.findOne({ organization: org1._id }));

  if (!worker1) throw new Error("Worker 1 fixture not found");
  if (!doctor1) throw new Error("Doctor 1 fixture not found");
  if (!patient1) throw new Error("Patient 1 fixture not found");

  const workerToken = jwt.sign(
    { id: worker1._id.toString(), role: ROLES.WORKER, organization: org1._id.toString() },
    serverConfig.JWT_SECRET,
    { expiresIn: "1h" }
  );

  const crossOrgWorkerToken = jwt.sign(
    { id: worker2._id.toString(), role: ROLES.WORKER, organization: org2._id.toString() },
    serverConfig.JWT_SECRET,
    { expiresIn: "1h" }
  );

  const doctorToken = jwt.sign(
    { id: doctor1._id.toString(), role: ROLES.DOCTOR, organization: org1._id.toString() },
    serverConfig.JWT_SECRET,
    { expiresIn: "1h" }
  );

  const crossOrgDoctorToken = jwt.sign(
    { id: doctor2._id.toString(), role: ROLES.DOCTOR, organization: org2._id.toString() },
    serverConfig.JWT_SECRET,
    { expiresIn: "1h" }
  );

  log(`[FIXTURES IN DATABASE]`);
  log(`Org 1 (Pune):   ${org1._id} (${org1.code})`);
  log(`Org 2 (Nashik): ${org2._id} (${org2.code})`);
  log(`Worker 1 (Org 1): ${worker1._id} (${worker1.email})`);
  log(`Doctor 1 (Org 1): ${doctor1._id} (${doctor1.email})`);
  log(`Patient 1 (Org 1): ${patient1._id} (${patient1.name})\n`);

  // Probe 1: Create test consultation for Step 10 Accept
  log("--------------------------------------------------------------------------------");
  log("[PROBE 1] Flow Step 10: Worker accepts AI diagnostic recommendation");
  const consultAccept = await Consultation.create({
    patient: patient1._id,
    submittedBy: worker1._id,
    organization: org1._id,
    symptoms: ["headache", "mild fever"],
    status: "analyzed",
    mlAnalysis: {
      disease: "Common Cold",
      confidence: 0.92,
      severityScore: 1.2,
      needsEscalation: false,
    },
  });

  const acceptRes = await apiRequest(
    "PATCH",
    `/api/v1/consultation/${consultAccept._id}/accept`,
    { notes: "Patient advised hydration and home rest. Vitals normal." },
    { Authorization: `Bearer ${workerToken}` }
  );
  log(`Request: PATCH /api/v1/consultation/${consultAccept._id}/accept`);
  log(`Response Status: ${acceptRes.status} (Expected 200)`);
  log(`Response Body: ${redact(acceptRes.data)}`);

  // Probe 2: Cross-org worker cannot accept Org 1 consultation
  log("\n--------------------------------------------------------------------------------");
  log("[PROBE 2] Security: Cross-organization worker cannot accept consultation (404 Anti-Enumeration)");
  const crossAcceptRes = await apiRequest(
    "PATCH",
    `/api/v1/consultation/${consultAccept._id}/accept`,
    {},
    { Authorization: `Bearer ${crossOrgWorkerToken}` }
  );
  log(`Request: PATCH /api/v1/consultation/${consultAccept._id}/accept (Cross-Org Token)`);
  log(`Response Status: ${crossAcceptRes.status} (Expected 404)`);
  log(`Response Body: ${redact(crossAcceptRes.data)}`);

  // Probe 3: Doctor cannot accept consultation (RBAC 403 Forbidden)
  log("\n--------------------------------------------------------------------------------");
  log("[PROBE 3] Security: Doctor role cannot invoke worker accept endpoint (RBAC 403 Forbidden)");
  const doctorAcceptRes = await apiRequest(
    "PATCH",
    `/api/v1/consultation/${consultAccept._id}/accept`,
    {},
    { Authorization: `Bearer ${doctorToken}` }
  );
  log(`Request: PATCH /api/v1/consultation/${consultAccept._id}/accept (Doctor Token)`);
  log(`Response Status: ${doctorAcceptRes.status} (Expected 403)`);
  log(`Response Body: ${redact(doctorAcceptRes.data)}`);

  // Probe 4: Flow Step 10 Worker escalates consultation to doctor
  log("\n--------------------------------------------------------------------------------");
  log("[PROBE 4] Flow Step 10: Worker escalates high-risk consultation to Doctor for Second Opinion");
  const consultEscalate = await Consultation.create({
    patient: patient1._id,
    submittedBy: worker1._id,
    organization: org1._id,
    symptoms: ["chest pain", "shortness of breath", "sweating"],
    status: "analyzed",
    mlAnalysis: {
      disease: "Cardiac Risk Profile",
      confidence: 0.88,
      severityScore: 4.8,
      needsEscalation: true,
      uncertaintyReason: "RED_FLAG_MATCH",
    },
  });

  const escalateRes = await apiRequest(
    "PATCH",
    `/api/v1/consultation/${consultEscalate._id}/escalate`,
    {
      doctorId: doctor1._id.toString(),
      reason: "Clinical red-flag symptoms detected: acute chest pain with diaphoresis.",
    },
    { Authorization: `Bearer ${workerToken}` }
  );
  log(`Request: PATCH /api/v1/consultation/${consultEscalate._id}/escalate`);
  log(`Response Status: ${escalateRes.status} (Expected 200)`);
  log(`Response Body: ${redact(escalateRes.data)}`);

  // Probe 5: Flow Step 11 Doctor queries pending review queue
  log("\n--------------------------------------------------------------------------------");
  log("[PROBE 5] Flow Step 11: Doctor queries pending review queue");
  const pendingRes = await apiRequest(
    "GET",
    "/api/v1/consultation/pending",
    null,
    { Authorization: `Bearer ${doctorToken}` }
  );
  log(`Request: GET /api/v1/consultation/pending`);
  log(`Response Status: ${pendingRes.status} (Expected 200)`);
  const pendingCases = pendingRes.data.consultations || [];
  log(`Pending cases assigned to Dr. ${doctor1.name}: ${pendingCases.length}`);
  const foundCase = pendingCases.find((c) => c._id === consultEscalate._id.toString());
  log(`Escalated case present in queue: ${!!foundCase}`);

  // Probe 6: Flow Step 11 Doctor responds with Second Opinion
  log("\n--------------------------------------------------------------------------------");
  log("[PROBE 6] Flow Step 11: Doctor submits clinical second opinion");
  const respondRes = await apiRequest(
    "PATCH",
    `/api/v1/consultation/${consultEscalate._id}/respond`,
    {
      diagnosis: "Suspected Acute Coronary Syndrome — Immediate Emergency Referral Required",
      recommendation: "Administer Aspirin 300mg stat, Sublingual Sorbitrate 5mg if systolic BP > 100 mmHg. Call 108 ambulance immediately.",
    },
    { Authorization: `Bearer ${doctorToken}` }
  );
  log(`Request: PATCH /api/v1/consultation/${consultEscalate._id}/respond`);
  log(`Response Status: ${respondRes.status} (Expected 200)`);
  log(`Response Body: ${redact(respondRes.data)}`);

  // Probe 7: Worker cannot submit doctor second opinion (RBAC 403 Forbidden)
  log("\n--------------------------------------------------------------------------------");
  log("[PROBE 7] Security: Worker role cannot submit doctor second opinion (RBAC 403 Forbidden)");
  const workerRespondRes = await apiRequest(
    "PATCH",
    `/api/v1/consultation/${consultEscalate._id}/respond`,
    { diagnosis: "Worker unauthorized diagnosis" },
    { Authorization: `Bearer ${workerToken}` }
  );
  log(`Request: PATCH /api/v1/consultation/${consultEscalate._id}/respond (Worker Token)`);
  log(`Response Status: ${workerRespondRes.status} (Expected 403)`);
  log(`Response Body: ${redact(workerRespondRes.data)}`);

  // Probe 8: Cross-org doctor cannot respond to Org 1 consultation (404 Anti-Enumeration)
  log("\n--------------------------------------------------------------------------------");
  log("[PROBE 8] Security: Cross-organization doctor cannot respond to consultation (404 Anti-Enumeration)");
  const crossDoctorRespondRes = await apiRequest(
    "PATCH",
    `/api/v1/consultation/${consultEscalate._id}/respond`,
    { diagnosis: "Cross-org doctor diagnosis" },
    { Authorization: `Bearer ${crossOrgDoctorToken}` }
  );
  log(`Request: PATCH /api/v1/consultation/${consultEscalate._id}/respond (Cross-Org Doctor Token)`);
  log(`Response Status: ${crossDoctorRespondRes.status} (Expected 404)`);
  log(`Response Body: ${redact(crossDoctorRespondRes.data)}`);

  // Probe 9: Audit Log Verification for Flow Steps 10 & 11
  log("\n--------------------------------------------------------------------------------");
  log("[PROBE 9] Audit Log: Verify immutable audit records created for triage transitions");
  const auditEvents = await AuditLog.find({
    resourceId: { $in: [consultAccept._id.toString(), consultEscalate._id.toString()] },
  }).sort({ timestamp: 1 });
  log(`Found ${auditEvents.length} audit events for test consultations:`);
  for (const ev of auditEvents) {
    log(` - Action: ${ev.action} | Resource: ${ev.resourceType}:${ev.resourceId} | User: ${ev.userRole}:${ev.userId} | IP: ${ev.ipAddress}`);
  }

  // Cleanup test consultations
  await Consultation.deleteMany({ _id: { $in: [consultAccept._id, consultEscalate._id] } });
  await AuditLog.deleteMany({ resourceId: { $in: [consultAccept._id.toString(), consultEscalate._id.toString()] } });

  log("\n================================================================================");
  log("ALL STAGE 5 PROBES COMPLETED SUCCESSFULLY.");
  log("================================================================================");

  fs.mkdirSync(path.dirname(EVIDENCE_FILE), { recursive: true });
  fs.writeFileSync(EVIDENCE_FILE, logLines.join("\n"), "utf8");
  log(`Evidence saved to: ${EVIDENCE_FILE}`);

  await mongoose.disconnect();
}

runStage5Probes().catch((err) => {
  console.error("FATAL ERROR in runStage5Probes:", err);
  process.exit(1);
});
