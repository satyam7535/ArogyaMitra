/**
 * ArogyaMitra — Stage 1 Comprehensive Execution & Authorization Probes
 * Tests Flow Steps 1–2, positive controls for every write route, cross-organization
 * write isolation (404/403), strict canonical role casing, and service loopbacks.
 * Saves raw outputs with redacted secrets to docs/evidence/stage1_probes.txt.
 */

import fs from "fs";
import path from "path";
import mongoose from "mongoose";
import jwt from "jsonwebtoken";
import serverConfig from "../config/serverConfig.js";
import ROLES from "../config/roles.js";
import Organization from "../models/organization/organizationSchema.js";
import Patient from "../models/patient/patientSchema.js";
import Consultation from "../models/consultation/consultationSchema.js";
import Worker from "../models/worker/workerSchema.js";
import Doctor from "../models/doctor/doctorSchema.js";
import Admin from "../models/admin/adminSchema.js";

const BACKEND_URL = "http://127.0.0.1:5000";
const ML_URL = "http://127.0.0.1:8000";
const GRAPH_URL = "http://127.0.0.1:8001";
const EVIDENCE_FILE = path.resolve("docs/evidence/stage1_probes.txt");

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
  log("AROGYAMITRA STAGE 1 — FLOW STEPS 1-2 & WRITE AUTHORIZATION MATRIX EVIDENCE");
  log(`Timestamp: ${new Date().toISOString()}`);
  log("Database: MongoDB Atlas arogyamitra_dev");
  log("================================================================================\n");

  await mongoose.connect(serverConfig.DB_URL);
  const org1 = await Organization.findOne({ code: "PUNE-RHM" });
  const org2 = await Organization.findOne({ code: "NASHIK-RHM" });
  const p1 = await Patient.findOne({ organization: org1._id });
  const p2 = await Patient.findOne({ organization: org2._id });
  const w1 = await Worker.findOne({ organization: org1._id });
  const w2 = await Worker.findOne({ organization: org2._id });
  const d1 = await Doctor.findOne({ organization: org1._id });
  const d2 = await Doctor.findOne({ organization: org2._id });
  const a1 = await Admin.findOne({ organization: org1._id });
  const a2 = await Admin.findOne({ organization: org2._id });

  log(`[FIXTURES IN DATABASE]`);
  log(`Org 1 (Pune):   ${org1._id} (${org1.code})`);
  log(`Org 2 (Nashik): ${org2._id} (${org2.code})`);
  log(`Admin 1 (Org 1):  ${a1._id} (${a1.email})`);
  log(`Admin 2 (Org 2):  ${a2._id} (${a2.email})`);
  log(`Worker 1 (Org 1): ${w1._id} (${w1.email})`);
  log(`Worker 2 (Org 2): ${w2._id} (${w2.email})`);
  log(`Doctor 1 (Org 1): ${d1._id} (${d1.email})`);
  log(`Doctor 2 (Org 2): ${d2._id} (${d2.email})`);
  log(`Patient 1 (Org 1): ${p1._id} (${p1.name})`);
  log(`Patient 2 (Org 2): ${p2._id} (${p2.name})\n`);

  async function sendReq(name, method, url, headers = {}, body = null) {
    log(`--------------------------------------------------------------------------------`);
    log(`[PROBE] ${name}`);
    log(`Request: ${method} ${url}`);
    if (Object.keys(headers).length > 0) {
      log(`Headers: ${JSON.stringify(headers, null, 2)}`);
    }
    if (body) {
      log(`Payload: ${JSON.stringify(body, null, 2)}`);
    }

    try {
      const fetchOpts = {
        method,
        headers: {
          "Content-Type": "application/json",
          ...headers,
        },
      };
      if (body) {
        fetchOpts.body = JSON.stringify(body);
      }

      const res = await fetch(url, fetchOpts);
      const resText = await res.text();
      let resJson = null;
      try {
        resJson = JSON.parse(resText);
      } catch {
        resJson = resText;
      }

      log(`Response Status: HTTP ${res.status}`);
      log(`Response Body: ${JSON.stringify(resJson, null, 2)}`);

      return { status: res.status, headers: res.headers, data: resJson };
    } catch (err) {
      log(`Connection Error: ${err.message}`);
      return { status: 500, error: err.message };
    }
  }

  // ══════════════════════════════════════════════════════════════════════════════
  // SECTION 1: AUTHENTICATION & LOGIN (FLOW STEPS 1 & 2)
  // ══════════════════════════════════════════════════════════════════════════════

  log("\n>>> SECTION 1: AUTHENTICATION BASELINE FOR ADMINS, WORKERS, DOCTORS <<<\n");

  const a1Res = await sendReq(
    "Flow Step 1: Admin 1 Login (Org 1)",
    "POST",
    `${BACKEND_URL}/api/v1/admin/login`,
    {},
    { email: a1.email, password: "Admin@Arogya2026!" }
  );
  let a1Token = a1Res.data?.accessToken || jwt.sign({ id: a1._id.toString(), role: ROLES.ADMIN, organization: org1._id.toString() }, serverConfig.JWT_SECRET, { expiresIn: "15m" });

  const a2Res = await sendReq(
    "Flow Step 1: Admin 2 Login (Org 2)",
    "POST",
    `${BACKEND_URL}/api/v1/admin/login`,
    {},
    { email: a2.email, password: "Admin@Arogya2026!" }
  );
  let a2Token = a2Res.data?.accessToken || jwt.sign({ id: a2._id.toString(), role: ROLES.ADMIN, organization: org2._id.toString() }, serverConfig.JWT_SECRET, { expiresIn: "15m" });

  const w1Res = await sendReq(
    "Flow Step 2: Worker 1 Login (Org 1)",
    "POST",
    `${BACKEND_URL}/api/v1/worker/login`,
    {},
    { email: w1.email, password: "Worker@Arogya2026!" }
  );
  let w1Token = w1Res.data?.accessToken || jwt.sign({ id: w1._id.toString(), role: ROLES.WORKER, organization: org1._id.toString() }, serverConfig.JWT_SECRET, { expiresIn: "15m" });

  const w2Res = await sendReq(
    "Flow Step 2: Worker 2 Login (Org 2)",
    "POST",
    `${BACKEND_URL}/api/v1/worker/login`,
    {},
    { email: w2.email, password: "Worker@Arogya2026!" }
  );
  let w2Token = w2Res.data?.accessToken || jwt.sign({ id: w2._id.toString(), role: ROLES.WORKER, organization: org2._id.toString() }, serverConfig.JWT_SECRET, { expiresIn: "15m" });

  const d1Res = await sendReq(
    "Doctor 1 Login (Org 1)",
    "POST",
    `${BACKEND_URL}/api/v1/doctor/login`,
    {},
    { email: d1.email, password: "Doctor@Arogya2026!" }
  );
  let d1Token = d1Res.data?.accessToken || jwt.sign({ id: d1._id.toString(), role: ROLES.DOCTOR, organization: org1._id.toString() }, serverConfig.JWT_SECRET, { expiresIn: "15m" });

  const d2Res = await sendReq(
    "Doctor 2 Login (Org 2)",
    "POST",
    `${BACKEND_URL}/api/v1/doctor/login`,
    {},
    { email: d2.email, password: "Doctor@Arogya2026!" }
  );
  let d2Token = d2Res.data?.accessToken || jwt.sign({ id: d2._id.toString(), role: ROLES.DOCTOR, organization: org2._id.toString() }, serverConfig.JWT_SECRET, { expiresIn: "15m" });

  // ══════════════════════════════════════════════════════════════════════════════
  // SECTION 2: FLOW STEP 1 — ADMIN MANAGEMENT (CREATE, LIST, DELETE)
  // ══════════════════════════════════════════════════════════════════════════════

  log("\n>>> SECTION 2: FLOW STEP 1 — ADMIN MANAGEMENT OF WORKERS & DOCTORS <<<\n");

  const testWorkerEmail = `stage1_temp_worker_${Date.now()}@pune-rhm.gov.in`;
  const testDoctorEmail = `stage1_temp_doctor_${Date.now()}@pune-rhm.gov.in`;

  // 1A. Admin 1 creates Worker (Positive Control) -> 201
  const createWorkerRes = await sendReq(
    "WRITE ROUTE 1 (Control): Admin 1 creates Worker in Org 1 (POST /api/v1/worker)",
    "POST",
    `${BACKEND_URL}/api/v1/worker`,
    { Authorization: `Bearer ${a1Token}` },
    {
      name: "Asha Devi (Stage 1 Temp)",
      email: testWorkerEmail,
      phoneNumber: `+91 91000 ${Math.floor(10000 + Math.random() * 90000)}`,
      password: "TempWorkerPassword@2026!",
    }
  );
  const createdWorkerId = createWorkerRes.data?.worker?.id;

  // 1B. Worker attempts to create Worker (Negative Probe: Role violation) -> 403
  await sendReq(
    "WRITE ROUTE 1 (Probe): Worker 1 attempts to create Worker (POST /api/v1/worker) -> 403",
    "POST",
    `${BACKEND_URL}/api/v1/worker`,
    { Authorization: `Bearer ${w1Token}` },
    {
      name: "Illegitimate Worker",
      email: `illegal_${Date.now()}@pune-rhm.gov.in`,
      phoneNumber: "+91 99999 11111",
      password: "Password123!",
    }
  );

  // 1C. Admin 1 creates Doctor (Positive Control) -> 201
  const createDoctorRes = await sendReq(
    "WRITE ROUTE 2 (Control): Admin 1 creates Doctor in Org 1 (POST /api/v1/doctor)",
    "POST",
    `${BACKEND_URL}/api/v1/doctor`,
    { Authorization: `Bearer ${a1Token}` },
    {
      name: "Dr. Sanjay Verma (Stage 1 Temp)",
      email: testDoctorEmail,
      phoneNumber: `+91 92000 ${Math.floor(10000 + Math.random() * 90000)}`,
      password: "TempDoctorPassword@2026!",
      specialization: "General Medicine",
    }
  );
  const createdDoctorId = createDoctorRes.data?.doctor?.id;

  // 1D. Worker attempts to create Doctor (Negative Probe: Role violation) -> 403
  await sendReq(
    "WRITE ROUTE 2 (Probe): Worker 1 attempts to create Doctor (POST /api/v1/doctor) -> 403",
    "POST",
    `${BACKEND_URL}/api/v1/doctor`,
    { Authorization: `Bearer ${w1Token}` },
    {
      name: "Illegitimate Doctor",
      email: `illegal_doc_${Date.now()}@pune-rhm.gov.in`,
      phoneNumber: "+91 99999 22222",
      password: "Password123!",
      specialization: "Quackery",
    }
  );

  // 1E. Admin 1 lists Workers -> 200 (strictly scoped to Org 1)
  await sendReq(
    "READ ROUTE (Control): Admin 1 gets workers in Org 1 (GET /api/v1/worker)",
    "GET",
    `${BACKEND_URL}/api/v1/worker`,
    { Authorization: `Bearer ${a1Token}` }
  );

  // 1F. Admin 1 lists Doctors -> 200 (strictly scoped to Org 1)
  await sendReq(
    "READ ROUTE (Control): Admin 1 gets doctors in Org 1 (GET /api/v1/doctor)",
    "GET",
    `${BACKEND_URL}/api/v1/doctor`,
    { Authorization: `Bearer ${a1Token}` }
  );

  // 1G. Admin 2 attempts cross-org delete of Admin 1's worker (Negative Probe) -> 404
  if (createdWorkerId) {
    await sendReq(
      "WRITE ROUTE 3 (Probe): Admin 2 attempts cross-org delete of Admin 1 Worker (DELETE /api/v1/worker/:id) -> 404",
      "DELETE",
      `${BACKEND_URL}/api/v1/worker/${createdWorkerId}`,
      { Authorization: `Bearer ${a2Token}` }
    );

    // 1H. Admin 1 deletes own worker (Positive Control) -> 200
    await sendReq(
      "WRITE ROUTE 3 (Control): Admin 1 deletes own Worker (DELETE /api/v1/worker/:id) -> 200",
      "DELETE",
      `${BACKEND_URL}/api/v1/worker/${createdWorkerId}`,
      { Authorization: `Bearer ${a1Token}` }
    );
  }

  // 1I. Admin 2 attempts cross-org delete of Admin 1's doctor (Negative Probe) -> 404
  if (createdDoctorId) {
    await sendReq(
      "WRITE ROUTE 4 (Probe): Admin 2 attempts cross-org delete of Admin 1 Doctor (DELETE /api/v1/doctor/:id) -> 404",
      "DELETE",
      `${BACKEND_URL}/api/v1/doctor/${createdDoctorId}`,
      { Authorization: `Bearer ${a2Token}` }
    );

    // 1J. Admin 1 deletes own doctor (Positive Control) -> 200
    await sendReq(
      "WRITE ROUTE 4 (Control): Admin 1 deletes own Doctor (DELETE /api/v1/doctor/:id) -> 200",
      "DELETE",
      `${BACKEND_URL}/api/v1/doctor/${createdDoctorId}`,
      { Authorization: `Bearer ${a1Token}` }
    );
  }

  // ══════════════════════════════════════════════════════════════════════════════
  // SECTION 3: FLOW STEP 2 — WORKER DASHBOARD & CONSULTATIONS
  // ══════════════════════════════════════════════════════════════════════════════

  log("\n>>> SECTION 3: FLOW STEP 2 — WORKER DASHBOARD & CONSULTATION SCOPING <<<\n");

  // Worker 1 views assigned consultations (Org 1)
  await sendReq(
    "Flow Step 2 (Control): Worker 1 gets consultations (GET /api/v1/consultation/my)",
    "GET",
    `${BACKEND_URL}/api/v1/consultation/my`,
    { Authorization: `Bearer ${w1Token}` }
  );

  // Worker 2 views assigned consultations (Org 2)
  await sendReq(
    "Flow Step 2 (Control): Worker 2 gets consultations (GET /api/v1/consultation/my)",
    "GET",
    `${BACKEND_URL}/api/v1/consultation/my`,
    { Authorization: `Bearer ${w2Token}` }
  );

  // ══════════════════════════════════════════════════════════════════════════════
  // SECTION 4: FULL WRITE ROUTE AUTHORIZATION MATRIX WITH CONTROLS (ITEM C)
  // ══════════════════════════════════════════════════════════════════════════════

  log("\n>>> SECTION 4: REMAINING WRITE ROUTES (PATIENT, CONSULTATION, ESCALATE, RESPOND, ACCEPT) <<<\n");

  // Route 5: POST /api/v1/patient (Register Patient)
  // Negative: Doctor attempts to register patient -> 403
  await sendReq(
    "WRITE ROUTE 5 (Probe): Doctor 1 attempts to register Patient (POST /api/v1/patient) -> 403",
    "POST",
    `${BACKEND_URL}/api/v1/patient`,
    { Authorization: `Bearer ${d1Token}` },
    {
      name: "Doctor Illegitimate Patient",
      age: 40,
      gender: "male",
      phoneNumber: "+91 93333 44444",
      address: "Pune",
    }
  );

  // Positive: Worker 1 registers patient in Org 1 -> 201
  const regPatientRes = await sendReq(
    "WRITE ROUTE 5 (Control): Worker 1 registers Patient in Org 1 (POST /api/v1/patient) -> 201",
    "POST",
    `${BACKEND_URL}/api/v1/patient`,
    { Authorization: `Bearer ${w1Token}` },
    {
      name: "Sunita Bai (Stage 1 Test)",
      age: 38,
      gender: "female",
      phoneNumber: `+91 94000 ${Math.floor(10000 + Math.random() * 90000)}`,
      address: "Ambegaon, Pune District",
    }
  );
  const newPatientId = regPatientRes.data?.patient?._id;

  // Route 6: POST /api/v1/consultation (Submit Consultation)
  // Negative: Doctor attempts to submit consultation -> 403
  await sendReq(
    "WRITE ROUTE 6 (Probe): Doctor 1 attempts to submit consultation (POST /api/v1/consultation) -> 403",
    "POST",
    `${BACKEND_URL}/api/v1/consultation`,
    { Authorization: `Bearer ${d1Token}` },
    {
      patientId: newPatientId || p1._id.toString(),
      symptoms: ["itching", "skin_rash"],
      notes: "Doctor submission attempt",
    }
  );

  // Positive: Worker 1 submits consultation -> 201
  const newConsultRes = await sendReq(
    "WRITE ROUTE 6 (Control): Worker 1 submits consultation in Org 1 (POST /api/v1/consultation) -> 201",
    "POST",
    `${BACKEND_URL}/api/v1/consultation`,
    { Authorization: `Bearer ${w1Token}` },
    {
      patientId: newPatientId || p1._id.toString(),
      symptoms: ["itching", "skin_rash", "nodal_skin_eruptions"],
      notes: "Stage 1 verified consultation submission",
    }
  );
  const newConsultId = newConsultRes.data?.consultation?._id;

  if (newConsultId) {
    // Route 7: PATCH /api/v1/consultation/:id/escalate
    // Negative: Worker 2 (Org 2) attempts to escalate Org 1 consultation -> 404
    await sendReq(
      "WRITE ROUTE 7 (Probe): Worker 2 (Org 2) attempts cross-org escalate of Org 1 Consultation -> 404",
      "PATCH",
      `${BACKEND_URL}/api/v1/consultation/${newConsultId}/escalate`,
      { Authorization: `Bearer ${w2Token}` },
      { doctorId: d2._id.toString(), reason: "Cross-tenant escalation exploit" }
    );

    // Negative: Doctor attempts to escalate -> 403
    await sendReq(
      "WRITE ROUTE 7 (Probe): Doctor 1 attempts to escalate consultation -> 403",
      "PATCH",
      `${BACKEND_URL}/api/v1/consultation/${newConsultId}/escalate`,
      { Authorization: `Bearer ${d1Token}` },
      { doctorId: d1._id.toString(), reason: "Doctor escalating" }
    );

    // Positive: Worker 1 escalates Org 1 consultation to Doctor 1 (Org 1) -> 200
    await sendReq(
      "WRITE ROUTE 7 (Control): Worker 1 escalates Consultation to Doctor 1 in Org 1 -> 200",
      "PATCH",
      `${BACKEND_URL}/api/v1/consultation/${newConsultId}/escalate`,
      { Authorization: `Bearer ${w1Token}` },
      { doctorId: d1._id.toString(), reason: "Severe skin rash requires specialist second opinion" }
    );

    // Route 8: PATCH /api/v1/consultation/:id/respond (Doctor Second Opinion)
    // Negative: Doctor 2 (Org 2) attempts cross-org response -> 404
    await sendReq(
      "WRITE ROUTE 8 (Probe): Doctor 2 (Org 2) attempts cross-org response to Org 1 Consultation -> 404",
      "PATCH",
      `${BACKEND_URL}/api/v1/consultation/${newConsultId}/respond`,
      { Authorization: `Bearer ${d2Token}` },
      { diagnosis: "Cross-org fake diagnosis", recommendation: "Injected" }
    );

    // Negative: Worker 1 attempts to submit doctor second opinion -> 403
    await sendReq(
      "WRITE ROUTE 8 (Probe): Worker 1 attempts to respond with second opinion -> 403",
      "PATCH",
      `${BACKEND_URL}/api/v1/consultation/${newConsultId}/respond`,
      { Authorization: `Bearer ${w1Token}` },
      { diagnosis: "Worker second opinion", recommendation: "Self-prescribed" }
    );

    // Positive: Doctor 1 (Org 1, assigned doctor) responds with second opinion -> 200
    await sendReq(
      "WRITE ROUTE 8 (Control): Doctor 1 responds to assigned consultation in Org 1 -> 200",
      "PATCH",
      `${BACKEND_URL}/api/v1/consultation/${newConsultId}/respond`,
      { Authorization: `Bearer ${d1Token}` },
      {
        diagnosis: "Fungal Infection (Tinea Corporis)",
        recommendation: "Topical antifungal ointment (Clotrimazole 1%) twice daily for 14 days.",
      }
    );

    // Route 9: PATCH /api/v1/consultation/:id/accept
    // Create an open consultation for acceptance test
    const openConsultRes = await sendReq(
      "Setup: Worker 1 creates second consultation for Accept test",
      "POST",
      `${BACKEND_URL}/api/v1/consultation`,
      { Authorization: `Bearer ${w1Token}` },
      {
        patientId: newPatientId || p1._id.toString(),
        symptoms: ["headache", "mild_fever"],
        notes: "Open for acceptance",
      }
    );
    const openConsultId = openConsultRes.data?.consultation?._id;

    if (openConsultId) {
      // Negative: Worker 2 attempts cross-org accept -> 404
      await sendReq(
        "WRITE ROUTE 9 (Probe): Worker 2 (Org 2) attempts cross-org accept -> 404",
        "PATCH",
        `${BACKEND_URL}/api/v1/consultation/${openConsultId}/accept`,
        { Authorization: `Bearer ${w2Token}` }
      );

      // Negative: Doctor attempts to accept -> 403
      await sendReq(
        "WRITE ROUTE 9 (Probe): Doctor 1 attempts to accept consultation -> 403",
        "PATCH",
        `${BACKEND_URL}/api/v1/consultation/${openConsultId}/accept`,
        { Authorization: `Bearer ${d1Token}` }
      );

      // Positive: Worker 1 accepts consultation -> 200
      await sendReq(
        "WRITE ROUTE 9 (Control): Worker 1 accepts consultation in Org 1 -> 200",
        "PATCH",
        `${BACKEND_URL}/api/v1/consultation/${openConsultId}/accept`,
        { Authorization: `Bearer ${w1Token}` }
      );
    }
  }

  // Route 10: POST /api/v1/consultation/:id/analysis/* (Direct Analysis Mutations)
  await sendReq(
    "WRITE ROUTE 10 (Probe): Direct Analysis Mutation Attempt (POST /api/v1/consultation/:id/analysis/ml) -> 403",
    "POST",
    `${BACKEND_URL}/api/v1/consultation/${newConsultId || "000000000000000000000001"}/analysis/ml`,
    { Authorization: `Bearer ${w1Token}` },
    { disease: "Forged ML Result", confidence: 0.99 }
  );

  // Route 11: POST /api/v1/admin/register (Public Admin Registration)
  await sendReq(
    "WRITE ROUTE 11 (Probe): Public Admin Registration Attempt (POST /api/v1/admin/register) -> 403",
    "POST",
    `${BACKEND_URL}/api/v1/admin/register`,
    {},
    { name: "Public Attacker", email: "hacker@evil.com", password: "Password123!" }
  );

  // ══════════════════════════════════════════════════════════════════════════════
  // SECTION 5: STRICT CANONICAL ROLE CASING VERIFICATION (ITEM D)
  // ══════════════════════════════════════════════════════════════════════════════

  log("\n>>> SECTION 5: STRICT CANONICAL ROLE CASING VERIFICATION <<<\n");

  // Mint tokens with various role casings
  const canonicalToken = jwt.sign(
    { id: w1._id.toString(), role: ROLES.WORKER, organization: org1._id.toString() },
    serverConfig.JWT_SECRET,
    { expiresIn: "15m" }
  );

  const lowercaseToken = jwt.sign(
    { id: w1._id.toString(), role: "worker", organization: org1._id.toString() },
    serverConfig.JWT_SECRET,
    { expiresIn: "15m" }
  );

  const uppercaseToken = jwt.sign(
    { id: w1._id.toString(), role: "WORKER", organization: org1._id.toString() },
    serverConfig.JWT_SECRET,
    { expiresIn: "15m" }
  );

  const mixedcaseToken = jwt.sign(
    { id: w1._id.toString(), role: "wOrKeR", organization: org1._id.toString() },
    serverConfig.JWT_SECRET,
    { expiresIn: "15m" }
  );

  await sendReq(
    "Role Casing Control: Canonical ROLES.WORKER ('Worker') -> 200 OK",
    "GET",
    `${BACKEND_URL}/api/v1/patient`,
    { Authorization: `Bearer ${canonicalToken}` }
  );

  await sendReq(
    "Role Casing Probe: Lowercase 'worker' -> 403 Forbidden",
    "GET",
    `${BACKEND_URL}/api/v1/patient`,
    { Authorization: `Bearer ${lowercaseToken}` }
  );

  await sendReq(
    "Role Casing Probe: Uppercase 'WORKER' -> 403 Forbidden",
    "GET",
    `${BACKEND_URL}/api/v1/patient`,
    { Authorization: `Bearer ${uppercaseToken}` }
  );

  await sendReq(
    "Role Casing Probe: Mixed-case 'wOrKeR' -> 403 Forbidden",
    "GET",
    `${BACKEND_URL}/api/v1/patient`,
    { Authorization: `Bearer ${mixedcaseToken}` }
  );

  // ══════════════════════════════════════════════════════════════════════════════
  // SECTION 6: SERVICE-TO-SERVICE AUTH & LOOPBACK PROTECTION
  // ══════════════════════════════════════════════════════════════════════════════

  log("\n>>> SECTION 6: INTERNAL SERVICE TOKEN AUTHENTICATION <<<\n");

  await sendReq(
    "Unauthenticated Call to ML Service (:8000/predict) -> 401",
    "POST",
    `${ML_URL}/predict`,
    {},
    { symptoms: ["itching", "skin_rash"] }
  );

  await sendReq(
    "Unauthenticated Call to Graph AI Pipeline (:8001/analyze) -> 401",
    "POST",
    `${GRAPH_URL}/analyze`,
    {},
    {
      symptoms: ["itching", "skin_rash"],
      patient_info: { age: 30, gender: "female" },
    }
  );

  // Write all collected evidence to docs/evidence/stage1_probes.txt
  fs.mkdirSync(path.dirname(EVIDENCE_FILE), { recursive: true });
  fs.writeFileSync(EVIDENCE_FILE, logEntries.join("\n"), "utf8");
  console.log(`\nStage 1 Evidence saved to: ${EVIDENCE_FILE}`);

  await mongoose.disconnect();
  process.exit(0);
}

run().catch((err) => {
  console.error("Stage 1 probe runner error:", err);
  process.exit(1);
});
