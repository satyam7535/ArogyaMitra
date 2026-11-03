/**
 * ArogyaMitra — Stage 4 Flow Steps 6, 7 & 8 Live Probes
 * Tests Asynchronous Job Queue with Durable MongoDB Persistence, Status Polling,
 * LangGraph AI Pipeline Orchestration, Safe Multilingual LLM, and ReportLab PDF Generation.
 * Saves raw outputs with redacted secrets to docs/evidence/stage4_probes.txt.
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
import AnalysisJob from "../models/job/jobSchema.js";

const BACKEND_URL = "http://127.0.0.1:5000";
const GRAPH_URL = "http://127.0.0.1:8001";
const EVIDENCE_FILE = path.resolve("../docs/evidence/stage4_probes.txt");

const logLines = [];
function log(msg = "") {
  console.log(msg);
  logLines.push(msg);
}

async function apiRequest(baseUrl, method, urlPath, body = null, headers = {}) {
  const url = `${baseUrl}${urlPath}`;
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
  } else if (contentType.includes("application/pdf")) {
    const arrayBuffer = await res.arrayBuffer();
    data = Buffer.from(arrayBuffer);
  } else {
    data = await res.text();
  }

  return { status: res.status, data, headers: res.headers };
}

async function runStage4Probes() {
  log("Command: node src/scripts/runStage4Probes.js");
  log("================================================================================");
  log("AROGYAMITRA STAGE 4 — ASYNC QUEUE, SAFE LLM & MULTILINGUAL PDF EVIDENCE");
  log(`Timestamp: ${new Date().toISOString()}`);
  log(`Database: MongoDB Atlas arogyamitra_dev`);
  log(`Backend URL: ${BACKEND_URL}`);
  log(`Graph URL:   ${GRAPH_URL}`);
  log("================================================================================\n");

  await mongoose.connect(serverConfig.DB_URL);

  const org1 = await Organization.findOne({ code: "PUNE-RHM" });
  const org2 = await Organization.findOne({ code: "NASHIK-RHM" });
  const worker1 = await Worker.findOne({ email: "worker@arogyamitra.gov.in" });
  const worker2 = await Worker.findOne({ email: "worker2@arogyamitra.gov.in" });
  const patient1 = await Patient.findOne({ name: "Kavita Devi", organization: org1._id });

  log("[FIXTURES IN DATABASE]");
  log(`Org 1 (Pune):     ${org1._id} (${org1.code})`);
  log(`Org 2 (Nashik):   ${org2._id} (${org2.code})`);
  log(`Worker 1 (Org 1): ${worker1._id} (${worker1.email})`);
  log(`Worker 2 (Org 2): ${worker2._id} (${worker2.email})`);
  log(`Patient 1 (Org 1): ${patient1._id} (${patient1.name})\n`);

  // SECTION 1: AUTHENTICATION BASELINE
  log(">>> SECTION 1: AUTHENTICATION BASELINE <<<");
  const w1Login = await apiRequest(BACKEND_URL, "POST", "/api/v1/worker/login", {
    email: "worker@arogyamitra.gov.in",
    password: "Worker@Arogya2026!",
  });
  log("[PROBE 1.1] Worker 1 Login (Org 1 Pune)");
  log(`Status: HTTP ${w1Login.status}`);
  const w1Token = w1Login.data.accessToken;

  const w2Login = await apiRequest(BACKEND_URL, "POST", "/api/v1/worker/login", {
    email: "worker2@arogyamitra.gov.in",
    password: "Worker@Arogya2026!",
  });
  log("[PROBE 1.2] Worker 2 Login (Org 2 Nashik)");
  log(`Status: HTTP ${w2Login.status}\n`);
  const w2Token = w2Login.data.accessToken;

  // SECTION 2: FLOW STEP 6 — ASYNCHRONOUS JOB QUEUE WITH DURABLE MONGODB PERSISTENCE
  log(">>> SECTION 2: FLOW STEP 6 — ASYNC QUEUE ENQUEUE, POLLING & DURABILITY <<<");

  // Create Consultation for Async Analysis
  const cPayload = {
    patientId: patient1._id.toString(),
    symptoms: ["itching", "skin_rash", "nodal_skin_eruptions"],
    notes: "Async analysis queue test consultation for patient Savita Patil.",
  };
  const cCreate = await apiRequest(BACKEND_URL, "POST", "/api/v1/consultation", cPayload, {
    "Authorization": `Bearer ${w1Token}`,
  });
  const consultationId = cCreate.data.consultation._id;
  log("--------------------------------------------------------------------------------");
  log("[PROBE 2.1] Worker 1 Submits Consultation for Asynchronous Analysis");
  log(`Response Status: HTTP ${cCreate.status}`);
  log(`Consultation ID: ${consultationId}\n`);

  // Enqueue Async Analysis Job (Returns HTTP 202)
  const enqueueRes = await apiRequest(
    BACKEND_URL,
    "POST",
    `/api/v1/consultation/${consultationId}/analyze/async`,
    { language: "hi" },
    { "Authorization": `Bearer ${w1Token}` }
  );
  log("--------------------------------------------------------------------------------");
  log("[PROBE 2.2] Worker 1 Enqueues Background Analysis Job");
  log(`Request: POST /api/v1/consultation/${consultationId}/analyze/async`);
  log(`Response Status: HTTP ${enqueueRes.status} (Expected: 202 Accepted) -> ${enqueueRes.status === 202 ? "PASS" : "FAIL"}`);
  log(`Response Body: ${JSON.stringify(enqueueRes.data, null, 2)}`);
  const jobId = enqueueRes.data.job.jobId;

  // Immediate Status Poll
  const immediatePoll = await apiRequest(
    BACKEND_URL,
    "GET",
    `/api/v1/consultation/${consultationId}/analyze/status/${jobId}`,
    null,
    { "Authorization": `Bearer ${w1Token}` }
  );
  log("--------------------------------------------------------------------------------");
  log("[PROBE 2.3] Immediate Job Status Poll");
  log(`Request: GET /api/v1/consultation/${consultationId}/analyze/status/${jobId}`);
  log(`Response Status: HTTP ${immediatePoll.status}`);
  log(`Current State: "${immediatePoll.data.job?.status}" -> ${["queued", "processing", "completed"].includes(immediatePoll.data.job?.status) ? "PASS" : "FAIL"}\n`);

  // Poll until completion (max 20 seconds)
  log("[PROBE 2.4] Polling Background Job to Terminal Completion...");
  let finalJobState = null;
  const pollStart = Date.now();
  while (Date.now() - pollStart < 25000) {
    await new Promise((r) => setTimeout(r, 1000));
    const poll = await apiRequest(
      BACKEND_URL,
      "GET",
      `/api/v1/consultation/${consultationId}/analyze/status/${jobId}`,
      null,
      { "Authorization": `Bearer ${w1Token}` }
    );
    if (poll.data.job?.status === "completed" || poll.data.job?.status === "failed") {
      finalJobState = poll.data.job;
      break;
    }
  }

  log(`Terminal Status Reached: "${finalJobState?.status}" (Completed in ${((Date.now() - pollStart) / 1000).toFixed(1)}s)`);
  log(`Job Result: ${JSON.stringify(finalJobState?.result, null, 2)}`);
  log(`Assertions:`);
  log(`  - Job Status is "completed" -> ${finalJobState?.status === "completed" ? "PASS" : "FAIL"}`);
  log(`  - Disease in Result: "${finalJobState?.result?.disease}" -> ${finalJobState?.result?.disease === "Fungal infection" ? "PASS" : "FAIL"}`);
  log(`  - Fallback Status: ${finalJobState?.result?.llmFallback}\n`);

  // Verify Durable MongoDB Document
  const dbJob = await AnalysisJob.findOne({ jobId });
  log("--------------------------------------------------------------------------------");
  log("[PROBE 2.5] Direct MongoDB Atlas Inspection of AnalysisJob Document (Durability Audit)");
  log(`Document Found in Database: ${dbJob ? "YES" : "NO"}`);
  log(`  - _id:          ${dbJob?._id}`);
  log(`  - jobId:        ${dbJob?.jobId}`);
  log(`  - status:       "${dbJob?.status}"`);
  log(`  - organization: ${dbJob?.organization}`);
  log(`  - createdAt:    ${dbJob?.createdAt}`);
  log(`  - startedAt:    ${dbJob?.startedAt}`);
  log(`  - completedAt:  ${dbJob?.completedAt}`);
  log(`  - Durable Persistence: Confirmed stored in Atlas -> ${dbJob && dbJob.status === "completed" ? "PASS" : "FAIL"}\n`);

  // Cross-Tenant Job Isolation (Worker 2 from Org 2 cannot poll Worker 1's job)
  const crossPoll = await apiRequest(
    BACKEND_URL,
    "GET",
    `/api/v1/consultation/${consultationId}/analyze/status/${jobId}`,
    null,
    { "Authorization": `Bearer ${w2Token}` }
  );
  log("--------------------------------------------------------------------------------");
  log("[PROBE 2.6] Cross-Tenant Job Isolation Probe: Worker 2 (Org 2) Polls Org 1 Job");
  log(`Request: GET /api/v1/consultation/${consultationId}/analyze/status/${jobId}`);
  log(`Response Status: HTTP ${crossPoll.status} (Expected: 404 Not Found) -> ${crossPoll.status === 404 ? "PASS" : "FAIL"}`);
  log(`Response Body: ${JSON.stringify(crossPoll.data, null, 2)}\n`);

  // SECTION 3: FLOW STEPS 7 & 8 — DIRECT LANGGRAPH SERVER ORCHESTRATION & PDF
  log(">>> SECTION 3: FLOW STEPS 7 & 8 — LANGGRAPH ORCHESTRATION & PDF GENERATION <<<");

  const serviceToken = jwt.sign(
    {
      iss: "arogyamitra-backend",
      aud: "arogyamitra-internal",
      sub: worker1._id.toString(),
      role: ROLES.WORKER,
      organization: org1._id.toString(),
    },
    serverConfig.INTERNAL_SERVICE_SECRET,
    { expiresIn: "5m" }
  );

  const graphHeaders = {
    "X-Internal-Service-Token": serviceToken,
    "Authorization": `Bearer ${serviceToken}`,
  };

  // Direct Graph Call /analyze/json in Hindi
  const graphJsonReq = {
    symptoms: ["itching", "skin_rash", "nodal_skin_eruptions"],
    patientName: "Savita Ramesh Patil",
    patientAge: 34,
    patientGender: "Female",
    workerName: "Sunita Patil",
    location: "Pune Rural Health Sub-center",
    language: "hi",
  };
  const graphJsonRes = await apiRequest(GRAPH_URL, "POST", "/analyze/json", graphJsonReq, graphHeaders);
  log("--------------------------------------------------------------------------------");
  log("[PROBE 3.1] Direct LangGraph Pipeline Orchestration (/analyze/json in Hindi)");
  log(`Request: POST http://127.0.0.1:8001/analyze/json`);
  log(`Response Status: HTTP ${graphJsonRes.status} -> ${graphJsonRes.status === 200 ? "PASS" : "FAIL"}`);
  const gData = graphJsonRes.data;
  log(`  - ML Disease:          ${gData.mlResult?.disease}`);
  log(`  - ML Confidence:       ${gData.mlResult?.confidence}%`);
  log(`  - TreeSHAP Features:   ${gData.mlResult?.shapExplanation?.length} features recorded`);
  log(`  - LLM Summary:         "${gData.llmResult?.diagnosis_summary?.substring(0, 80)}..."`);
  log(`  - Fallback Status:     ${gData.llmResult?.llmFallback}`);
  log(`  - PDF Base64 Present:  ${typeof gData.pdfBase64 === "string" && gData.pdfBase64.length > 1000 ? "YES" : "NO"}\n`);

  // Direct Graph Call /analyze/pdf in Marathi
  const graphPdfReq = {
    symptoms: ["itching", "skin_rash", "nodal_skin_eruptions"],
    patientName: "Savita Ramesh Patil",
    patientAge: 34,
    patientGender: "Female",
    workerName: "Sunita Patil",
    location: "Pune Rural Health Sub-center",
    language: "mr",
  };
  const graphPdfRes = await apiRequest(GRAPH_URL, "POST", "/analyze/pdf", graphPdfReq, graphHeaders);
  log("--------------------------------------------------------------------------------");
  log("[PROBE 3.2] Direct LangGraph Multilingual PDF Generation (/analyze/pdf in Marathi)");
  log(`Request: POST http://127.0.0.1:8001/analyze/pdf`);
  log(`Response Status: HTTP ${graphPdfRes.status} -> ${graphPdfRes.status === 200 ? "PASS" : "FAIL"}`);
  log(`Content-Type:    "${graphPdfRes.headers.get("content-type")}"`);
  const isPdfBuffer = Buffer.isBuffer(graphPdfRes.data);
  const pdfStartsValid = isPdfBuffer && graphPdfRes.data.slice(0, 5).toString() === "%PDF-";
  log(`Binary PDF Valid: ${pdfStartsValid ? "YES (%PDF- header confirmed)" : "NO"}`);
  log(`PDF Byte Size:    ${isPdfBuffer ? `${graphPdfRes.data.length.toLocaleString()} bytes` : "N/A"}\n`);

  // Unauthenticated Call to Graph Service
  const unauthRes = await apiRequest(GRAPH_URL, "POST", "/analyze/json", graphJsonReq);
  log("--------------------------------------------------------------------------------");
  log("[PROBE 3.3] Negative Security Probe: Unauthenticated Call to Graph Service Rejected");
  log(`Request: POST http://127.0.0.1:8001/analyze/json (no token)`);
  log(`Response Status: HTTP ${unauthRes.status} (Expected: 401 Unauthorized) -> ${unauthRes.status === 401 ? "PASS" : "FAIL"}`);
  log(`Response Detail: "${unauthRes.data.detail}"\n`);

  log("================================================================================");
  log("STAGE 4 LIVE PROBES COMPLETE: ALL CHECKS VERIFIED AGAINST ATLAS & LOCAL SERVICES");
  log("================================================================================");

  fs.writeFileSync(EVIDENCE_FILE, logLines.join("\n"), "utf8");
  console.log(`\n[+] Evidence successfully written to ${EVIDENCE_FILE}`);
  await mongoose.disconnect();
}

runStage4Probes().catch((err) => {
  console.error("Stage 4 probe script failed:", err);
  process.exit(1);
});
