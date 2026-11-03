import mongoose from "mongoose";
import { fork } from "child_process";
import { fileURLToPath } from "url";
import path from "path";
import serverConfig from "../config/serverConfig.js";
import AnalysisJob from "../models/job/jobSchema.js";
import { claimNextJob } from "../service/jobQueue.service.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Subprocess Worker Mode
if (process.argv[2] === "--worker") {
  const workerId = process.argv[3];
  const leaseMs = parseInt(process.argv[4] || "2000", 10);

  await mongoose.connect(serverConfig.DB_URL);
  const claimed = await claimNextJob(workerId, leaseMs);
  if (claimed) {
    process.send({ type: "CLAIMED", jobId: claimed.jobId, workerId, attempts: claimed.attempts });
    // Intentionally hang simulating heavy ML work until killed
    await new Promise(() => {});
  } else {
    process.send({ type: "NO_JOB", workerId });
    process.exit(0);
  }
}

// Master Test Controller
async function runWorkerKillTest() {
  console.log("================================================================================");
  console.log("AROGYAMITRA — P3.7 REAL WORKER-KILL MID-JOB & LEASE EXPIRY RECLAMATION TEST");
  console.log("Date:", new Date().toISOString());
  console.log("Database:", serverConfig.DB_URL);
  console.log("================================================================================\n");

  await mongoose.connect(serverConfig.DB_URL);

  const jobId = `job_kill_live_${Date.now()}`;
  const consultationId = new mongoose.Types.ObjectId();
  const organization = new mongoose.Types.ObjectId();
  const requestingUserId = new mongoose.Types.ObjectId();

  // 1. Enqueue genuine job in MongoDB
  console.log("[STEP 1] Enqueuing real analysis job in MongoDB...");
  const job = await AnalysisJob.create({
    jobId,
    consultationId,
    organization,
    requestingUserId,
    status: "queued",
    attempts: 0,
    maxAttempts: 3,
    payload: {
      symptoms: ["chills", "high_fever", "sweating"],
      language: "en",
    },
    createdAt: new Date(),
  });
  console.log(`[+] Enqueued job: ${job.jobId} (status: ${job.status})\n`);

  // 2. Spawn Worker 1 in separate OS child process
  console.log("[STEP 2] Spawning Worker Process 1 (PID to be killed mid-job)...");
  const worker1Child = fork(__filename, ["--worker", "worker-proc-alpha", "2000"], {
    stdio: ["inherit", "inherit", "inherit", "ipc"],
  });

  const worker1Pid = worker1Child.pid;
  console.log(`[+] Worker 1 started with PID: ${worker1Pid}`);

  await new Promise((resolve) => {
    worker1Child.on("message", (msg) => {
      if (msg.type === "CLAIMED") {
        console.log(`[+] Worker 1 (${msg.workerId}) atomically claimed job ${msg.jobId}`);
        console.log(`[+] Lease granted: 2000ms. Job status in DB is 'processing'.`);
        resolve();
      }
    });
  });

  // Verify job state in DB
  let dbJob = await AnalysisJob.findOne({ jobId });
  console.log(`[AUDIT] In-database state: status='${dbJob.status}', lockedBy='${dbJob.lockedBy}', attempts=${dbJob.attempts}\n`);

  // 3. SIGKILL Worker 1 mid-job
  console.log(`[STEP 3] Issuing SIGKILL to Worker Process 1 (PID ${worker1Pid}) mid-job...`);
  const killSuccess = worker1Child.kill("SIGKILL");
  console.log(`[+] process.kill(${worker1Pid}, 'SIGKILL') returned: ${killSuccess}`);

  await new Promise((resolve) => {
    worker1Child.on("exit", (code, signal) => {
      console.log(`[+] Worker 1 successfully terminated by OS (signal: ${signal}, code: ${code})\n`);
      resolve();
    });
  });

  // 4. Test immediate claim before lease expiry
  console.log("[STEP 4] Concurrency check: Worker 2 attempts claim while lease is active...");
  const earlyClaim = await claimNextJob("worker-proc-beta", 2000);
  console.log(`[+] Early claim result: ${earlyClaim === null ? "NULL (Lock strictly held by active lease)" : "UNEXPECTED"}`);
  if (earlyClaim !== null) {
    throw new Error("Concurrency failure: lock was violated before lease expiry!");
  }

  // 5. Wait for Worker 1's 2000ms lease to expire
  console.log("\n[STEP 5] Waiting 2200ms for Worker 1's lease to expire...");
  await new Promise((resolve) => setTimeout(resolve, 2200));
  const expiredJob = await AnalysisJob.findOne({ jobId });
  const isExpired = new Date() > new Date(expiredJob.leaseExpiresAt);
  console.log(`[+] Lease expired status: ${isExpired} (leaseExpiresAt: ${expiredJob.leaseExpiresAt.toISOString()})\n`);

  // 6. Worker 2 sweeps queue and reclaims abandoned job
  console.log("[STEP 6] Worker 2 claims next job: sweeping abandoned/expired processing jobs...");
  const reclaimedJob = await claimNextJob("worker-proc-beta", 5000);
  console.log(`[+] Worker 2 successfully reclaimed job: ${reclaimedJob.jobId}`);
  console.log(`[+] New lock owner: '${reclaimedJob.lockedBy}' (attempts incremented to: ${reclaimedJob.attempts})`);

  // 7. Worker 2 finishes analysis
  console.log("\n[STEP 7] Worker 2 completes processing and saves final result...");
  reclaimedJob.status = "completed";
  reclaimedJob.completedAt = new Date();
  reclaimedJob.result = {
    disease: "Malaria",
    confidence: 0.994,
    reclaimedAfterCrash: true,
  };
  await reclaimedJob.save();

  // 8. Final audit
  console.log("\n================================================================================");
  console.log("FINAL AUDIT & CONSISTENCY VERIFICATION");
  console.log("================================================================================");
  const finalJob = await AnalysisJob.findOne({ jobId });
  console.log(`Job ID:            ${finalJob.jobId}`);
  console.log(`Final Status:      ${finalJob.status}`);
  console.log(`Final Locked By:   ${finalJob.lockedBy}`);
  console.log(`Total Attempts:    ${finalJob.attempts} (1 before crash + 1 after recovery)`);
  console.log(`Primary Diagnosis: ${finalJob.result.disease} (Confidence: ${finalJob.result.confidence})`);

  const jobCount = await AnalysisJob.countDocuments({ jobId });
  console.log(`Total DB Records:  ${jobCount} (Strictly exactly 1 result, 0 duplicates)`);

  if (finalJob.status === "completed" && jobCount === 1 && finalJob.attempts === 2) {
    console.log("\nRESULT: VERIFIED — Real worker-kill mid-job and lease expiry reclamation passed.");
    process.exit(0);
  } else {
    console.error("\nRESULT: FAILED consistency check.");
    process.exit(1);
  }
}

if (process.argv[2] !== "--worker") {
  runWorkerKillTest().catch((err) => {
    console.error("Test error:", err);
    process.exit(1);
  });
}

