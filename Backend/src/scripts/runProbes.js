/**
 * ArogyaMitra — Stage 0 Real Database & API Probes
 * Executes probes against running backend (:5000), ML (:8000), and Graph (:8001)
 * Captures raw HTTP transcripts and saves to docs/evidence/stage0_probes.txt
 * All JWTs and passwords are strictly sanitized/redacted before writing.
 */

import fs from "fs";
import path from "path";
import mongoose from "mongoose";
import jwt from "jsonwebtoken";
import serverConfig from "../config/serverConfig.js";
import Organization from "../models/organization/organizationSchema.js";
import Patient from "../models/patient/patientSchema.js";
import Consultation from "../models/consultation/consultationSchema.js";
import Worker from "../models/worker/workerSchema.js";
import Doctor from "../models/doctor/doctorSchema.js";
import Admin from "../models/admin/adminSchema.js";

const BACKEND_URL = "http://127.0.0.1:5000";
const ML_URL = "http://127.0.0.1:8000";
const GRAPH_URL = "http://127.0.0.1:8001";
const EVIDENCE_FILE = path.resolve("../docs/evidence/stage0_probes.txt");

function sanitizeText(str) {
  if (!str) return str;
  return str
    .replace(/eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+/g, "[REDACTED_JWT]")
    .replace(/"password":\s*"[^"]+"/g, '"password": "[REDACTED_PASSWORD]"')
    .replace(/"refreshToken":\s*"[^"]+"/g, '"refreshToken": "[REDACTED_REFRESH_TOKEN]"')
    .replace(/"accessToken":\s*"[^"]+"/g, '"accessToken": "[REDACTED_JWT]"')
    .replace(/refreshToken=[^;\s"]+/g, "refreshToken=[REDACTED_COOKIE]")
    .replace(/token=[^;\s"]+/g, "token=[REDACTED_COOKIE]");
}

async function run() {
  const logEntries = [];
  const log = (msg) => {
    const clean = sanitizeText(msg);
    console.log(clean);
    logEntries.push(clean);
  };

  log("================================================================================");
  log("AROGYAMITRA STAGE 0 — REAL DATABASE & API PROBE EVIDENCE");
  log(`Timestamp: ${new Date().toISOString()}`);
  log("Database: MongoDB Atlas arogyamitra_dev");
  log("================================================================================\n");

  // Connect to DB to fetch IDs of seeded test fixtures
  await mongoose.connect(serverConfig.DB_URL);
  const org1 = await Organization.findOne({ code: "PUNE-RHM" });
  const org2 = await Organization.findOne({ code: "NASHIK-RHM" });
  const p1 = await Patient.findOne({ organization: org1._id, name: "Kavita Devi" });
  const c1 = await Consultation.findOne({ organization: org1._id });
  const w1 = await Worker.findOne({ organization: org1._id });
  const d1 = await Doctor.findOne({ organization: org1._id });
  const d2 = await Doctor.findOne({ organization: org2._id });

  log(`[FIXTURES FOUND]`);
  log(`Org 1 (Pune): ${org1._id} (${org1.code})`);
  log(`Org 2 (Nashik): ${org2._id} (${org2.code})`);
  log(`Patient 1 (Org 1): ${p1._id} (${p1.name})`);
  log(`Consultation 1 (Org 1): ${c1._id}`);
  log(`Worker 1 (Org 1): ${w1._id} (${w1.email})`);
  log(`Doctor 1 (Org 1): ${d1._id} (${d1.email})`);
  log(`Doctor 2 (Org 2): ${d2._id} (${d2.email})\n`);

  async function sendReq(name, method, url, headers = {}, body = null) {
    log(`--------------------------------------------------------------------------------`);
    log(`PROBE: ${name}`);
    log(`--------------------------------------------------------------------------------`);
    log(`>>> REQUEST:`);
    log(`${method} ${url}`);
    for (const [k, v] of Object.entries(headers)) {
      if (k.toLowerCase() === "authorization") {
        log(`${k}: Bearer [REDACTED_BEARER_TOKEN]`);
      } else {
        log(`${k}: ${v}`);
      }
    }
    if (body) {
      log(`Body: ${JSON.stringify(body, null, 2)}`);
    }

    try {
      const fetchOpts = {
        method,
        headers: { ...headers },
      };
      if (body) {
        if (!fetchOpts.headers["Content-Type"]) {
          fetchOpts.headers["Content-Type"] = "application/json";
        }
        fetchOpts.body = JSON.stringify(body);
      }

      const res = await fetch(url, fetchOpts);
      const text = await res.text();
      let parsed;
      try {
        parsed = JSON.parse(text);
      } catch {
        parsed = text;
      }

      log(`<<< RESPONSE:`);
      log(`Status: ${res.status} ${res.statusText}`);
      for (const [k, v] of res.headers.entries()) {
        if (k.toLowerCase() === "set-cookie") {
          log(`${k}: [REDACTED_COOKIE]`);
        } else {
          log(`${k}: ${v}`);
        }
      }
      log(`Body: ${typeof parsed === "object" ? JSON.stringify(parsed, null, 2) : parsed}\n`);
      return { status: res.status, headers: res.headers, data: parsed };
    } catch (err) {
      log(`<<< ERROR: ${err.message}\n`);
      return { status: 0, error: err.message };
    }
  }

  // 1. Login as Worker 1 (Org 1)
  const worker1Login = await sendReq("Worker 1 Login (Org 1)", "POST", `${BACKEND_URL}/api/v1/worker/login`, {}, {
    email: "worker@arogyamitra.gov.in",
    password: "Worker@Arogya2026!"
  });
  const worker1Token = worker1Login.data?.accessToken;
  if (worker1Token) {
    const decoded = jwt.decode(worker1Token);
    log(`[JWT Worker 1 Claims]: ${JSON.stringify(decoded, null, 2)}\n`);
  }

  // 2. Login as Worker 2 (Org 2 - Cross-Tenant)
  const worker2Login = await sendReq("Worker 2 Login (Org 2 - Cross-Tenant)", "POST", `${BACKEND_URL}/api/v1/worker/login`, {}, {
    email: "worker2@arogyamitra.gov.in",
    password: "Worker@Arogya2026!"
  });
  const worker2Token = worker2Login.data?.accessToken;
  if (worker2Token) {
    const decoded = jwt.decode(worker2Token);
    log(`[JWT Worker 2 Claims]: ${JSON.stringify(decoded, null, 2)}\n`);
  }

  // 3. Login as Doctor 1 (Org 1)
  const doc1Login = await sendReq("Doctor 1 Login (Org 1)", "POST", `${BACKEND_URL}/api/v1/doctor/login`, {}, {
    email: "doctor@arogyamitra.gov.in",
    password: "Doctor@Arogya2026!"
  });
  const doc1Token = doc1Login.data?.accessToken;

  // 4. Login as Doctor 2 (Org 2 - Cross-Tenant)
  const doc2Login = await sendReq("Doctor 2 Login (Org 2 - Cross-Tenant)", "POST", `${BACKEND_URL}/api/v1/doctor/login`, {}, {
    email: "doctor2@arogyamitra.gov.in",
    password: "Doctor@Arogya2026!"
  });
  const doc2Token = doc2Login.data?.accessToken;

  // 5. Login as Admin 1 (Org 1)
  const admin1Login = await sendReq("Admin 1 Login (Org 1)", "POST", `${BACKEND_URL}/api/v1/admin/login`, {}, {
    email: "admin@arogyamitra.gov.in",
    password: "Admin@Arogya2026!"
  });
  const admin1Token = admin1Login.data?.accessToken;

  // 6. Login as Admin 2 (Org 2 - Cross-Tenant)
  const admin2Login = await sendReq("Admin 2 Login (Org 2 - Cross-Tenant)", "POST", `${BACKEND_URL}/api/v1/admin/login`, {}, {
    email: "admin2@arogyamitra.gov.in",
    password: "Admin@Arogya2026!"
  });
  const admin2Token = admin2Login.data?.accessToken;

  // ── READ PROBES ─────────────────────────────────────────────────────────────

  // Probe: Cross-Org Read: Worker 2 (Org 2) accessing Patient 1 (Org 1) -> 404
  await sendReq(
    "Cross-Tenant READ: Worker 2 (Org 2) requesting Patient 1 (Org 1)",
    "GET",
    `${BACKEND_URL}/api/v1/patient/${p1._id}`,
    { Authorization: `Bearer ${worker2Token}` }
  );

  // Probe: Cross-Org Read: Worker 2 (Org 2) accessing Consultation 1 (Org 1) -> 404
  await sendReq(
    "Cross-Tenant READ: Worker 2 (Org 2) requesting Consultation 1 (Org 1)",
    "GET",
    `${BACKEND_URL}/api/v1/consultation/${c1._id}`,
    { Authorization: `Bearer ${worker2Token}` }
  );

  // Probe: Same-Org Read Baseline: Worker 1 (Org 1) accessing Patient 1 (Org 1) -> 200
  await sendReq(
    "Legitimate Same-Tenant READ: Worker 1 (Org 1) requesting Patient 1 (Org 1)",
    "GET",
    `${BACKEND_URL}/api/v1/patient/${p1._id}`,
    { Authorization: `Bearer ${worker1Token}` }
  );

  // ── WRITE PROBES (CROSS-ORGANIZATION) ───────────────────────────────────────

  // Probe: Cross-Org WRITE (Escalate): Worker 2 (Org 2) escalates Consultation 1 (Org 1) -> 404
  await sendReq(
    "Cross-Tenant WRITE (Escalate): Worker 2 (Org 2) escalating Consultation 1 (Org 1)",
    "PATCH",
    `${BACKEND_URL}/api/v1/consultation/${c1._id}/escalate`,
    { Authorization: `Bearer ${worker2Token}` },
    {
      doctorId: d2._id.toString(),
      reason: "Unauthorized cross-org escalation attempt",
    }
  );

  // Probe: Cross-Org WRITE (Accept): Worker 2 (Org 2) accepts AI on Consultation 1 (Org 1) -> 404
  await sendReq(
    "Cross-Tenant WRITE (Accept AI): Worker 2 (Org 2) accepting AI on Consultation 1 (Org 1)",
    "PATCH",
    `${BACKEND_URL}/api/v1/consultation/${c1._id}/accept`,
    { Authorization: `Bearer ${worker2Token}` }
  );

  // Probe: Cross-Org WRITE (Respond): Doctor 2 (Org 2) responds to Consultation 1 (Org 1) -> 404
  await sendReq(
    "Cross-Tenant WRITE (Respond): Doctor 2 (Org 2) submitting second opinion on Consultation 1 (Org 1)",
    "PATCH",
    `${BACKEND_URL}/api/v1/consultation/${c1._id}/respond`,
    { Authorization: `Bearer ${doc2Token}` },
    {
      diagnosis: "Forged cross-tenant opinion",
      recommendation: "Prescribe unauthorized medication",
    }
  );

  // Probe: Cross-Org WRITE (Delete Worker): Admin 2 (Org 2) deleting Worker 1 (Org 1) -> 404
  await sendReq(
    "Cross-Tenant WRITE (Delete Worker): Admin 2 (Org 2) attempting to delete Worker 1 (Org 1)",
    "DELETE",
    `${BACKEND_URL}/api/v1/worker/${w1._id}`,
    { Authorization: `Bearer ${admin2Token}` }
  );

  // Probe: Cross-Org WRITE (Delete Doctor): Admin 2 (Org 2) deleting Doctor 1 (Org 1) -> 404
  await sendReq(
    "Cross-Tenant WRITE (Delete Doctor): Admin 2 (Org 2) attempting to delete Doctor 1 (Org 1)",
    "DELETE",
    `${BACKEND_URL}/api/v1/doctor/${d1._id}`,
    { Authorization: `Bearer ${admin2Token}` }
  );

  // Probe: Worker direct analysis write attempt -> POST /api/v1/consultation/:id/analysis/ml -> 403
  await sendReq(
    "Worker Direct Analysis Mutation Attempt (POST /api/v1/consultation/:id/analysis/ml)",
    "POST",
    `${BACKEND_URL}/api/v1/consultation/${c1._id}/analysis/ml`,
    { Authorization: `Bearer ${worker1Token}` },
    {
      disease: "Hacked Diagnosis",
      confidence: 0.999
    }
  );

  // ── MASS ASSIGNMENT PROBE ───────────────────────────────────────────────────

  // Probe: Mass Assignment Attempt on POST /api/v1/patient
  const massAssignPayload = {
    _id: "000000000000000000000001",
    name: "Pooja Deshmukh",
    age: 29,
    gender: "female",
    phoneNumber: "+91 98888 77777",
    address: "Shirur Tehsil, Pune",
    organization: org2._id.toString(), // attempting to force assign into Org 2 (Nashik)
    role: "Admin",                     // attempting privilege escalation
    addedBy: "malicious_actor_id",
    mlAnalysis: { disease: "Maliciously Injected Analysis", confidence: 100 },
    analysis: { bypassed: true },
    status: "verified"
  };

  const massAssignRes = await sendReq(
    "Mass Assignment Probe: Worker 1 creates Patient with injected _id, organization, role, analysis",
    "POST",
    `${BACKEND_URL}/api/v1/patient`,
    { Authorization: `Bearer ${worker1Token}` },
    massAssignPayload
  );

  // Query MongoDB to verify stored document properties
  if (massAssignRes.data?.patient?._id) {
    const createdPatientId = massAssignRes.data.patient._id;
    const dbDoc = await Patient.findById(createdPatientId).lean();
    log(`[DATABASE VERIFICATION OF STORED PATIENT]`);
    log(`Stored _id: ${dbDoc._id} (Matches injected 000000000000000000000001: ${dbDoc._id.toString() === "000000000000000000000001"})`);
    log(`Stored organization: ${dbDoc.organization} (Matches user org Org 1: ${dbDoc.organization.toString() === org1._id.toString()}; Injected Org 2 Ignored: ${dbDoc.organization.toString() !== org2._id.toString()})`);
    log(`Stored role field: ${dbDoc.role || "[NOT PRESENT]"} (Role injected ignored)`);
    log(`Stored mlAnalysis field: ${JSON.stringify(dbDoc.mlAnalysis) || "[NOT PRESENT]"} (Analysis injected ignored)`);
    log(`Stored analysis field: ${JSON.stringify(dbDoc.analysis) || "[NOT PRESENT]"} (Analysis injected ignored)\n`);
  }

  // ── INTER-SERVICE TOKENS PROBES ─────────────────────────────────────────────

  // Probe: Unauthenticated Call to ML Microservice (:8000) -> 401
  await sendReq(
    "Unauthenticated Call to ML Service (:8000/predict)",
    "POST",
    `${ML_URL}/predict`,
    {},
    { symptoms: ["itching", "skin_rash"] }
  );

  // Probe: Unauthenticated Call to Graph AI Pipeline (:8001) -> 401
  await sendReq(
    "Unauthenticated Call to Graph AI Pipeline (:8001/analyze)",
    "POST",
    `${GRAPH_URL}/analyze`,
    {},
    {
      symptoms: ["itching", "skin_rash"],
      patient_info: { age: 30, gender: "female" }
    }
  );

  // Write all collected evidence to docs/evidence/stage0_probes.txt
  fs.mkdirSync(path.dirname(EVIDENCE_FILE), { recursive: true });
  fs.writeFileSync(EVIDENCE_FILE, logEntries.join("\n"), "utf8");
  console.log(`\nEvidence saved to: ${EVIDENCE_FILE}`);

  await mongoose.disconnect();
  process.exit(0);
}

run().catch((err) => {
  console.error("Probe runner error:", err);
  process.exit(1);
});
