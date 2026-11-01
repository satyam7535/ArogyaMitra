import { chromium } from "playwright";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { execSync } from "child_process";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, "..");
const screenshotDir = path.join(rootDir, "docs", "evidence", "ui_screenshots");
fs.mkdirSync(screenshotDir, { recursive: true });

async function main() {
  console.log("=== Resetting Demo Database to Pristine State ===");
  try {
    execSync("powershell -File scripts/reset_demo.ps1", { stdio: "inherit", cwd: rootDir });
  } catch (e) {
    console.error("Warning: reset_demo.ps1 returned error:", e.message);
  }

  const patientName = "Demo Patient A";
  const cardiacPatientName = "Demo Patient B";

  console.log(`Starting clean screenshot generation for report...`);
  const browser = await chromium.launch({
    headless: true,
    args: ["--ignore-certificate-errors", "--no-sandbox"],
  });

  const context = await browser.newContext({
    ignoreHTTPSErrors: true,
    viewport: { width: 1400, height: 950 },
  });

  const page = await context.newPage();

  try {
    // 1. Worker Triage Intake & Differential for Demo Patient A
    console.log("1. Worker Triage Intake for Demo Patient A...");
    await page.goto("https://localhost/Worker_Triage", { waitUntil: "networkidle", timeout: 45000 });
    await page.waitForSelector("[data-testid='stAppViewContainer']", { timeout: 30000 });

    const nameInput = page.locator("input").first();
    await nameInput.click();
    await nameInput.fill(patientName);
    await page.keyboard.press("Tab");
    await page.waitForTimeout(1500);

    const jaundicePreset = page.getByRole("button", { name: /Jaundice \/ Liver Case|Jaundice/i });
    await jaundicePreset.click();
    await page.waitForTimeout(1000);

    const runBtn = page.getByRole("button", { name: /Run AI Diagnostic Analysis|Run Analysis/i });
    await runBtn.click();
    await page.waitForSelector("div[data-testid='stMetricValue']:has-text('Jaundice')", { timeout: 35000 });
    await page.waitForTimeout(2000);

    // Save Panel A: Worker Result
    console.log("Saving clean 01_worker_result.png...");
    await page.screenshot({
      path: path.join(screenshotDir, "01_worker_result.png"),
      clip: { x: 0, y: 140, width: 1400, height: 750 },
    });

    // Escalate Demo Patient A
    console.log("Escalating Demo Patient A to doctor...");
    const escalateBtn = page.getByRole("button", { name: /Escalate to Doctor|Escalate/i });
    await escalateBtn.click();
    await page.waitForSelector("text=Case successfully escalated", { timeout: 15000 });
    await page.waitForTimeout(2000);

    // Save Panel C: Worker Escalated List
    console.log("Saving clean 06_worker_list_escalated.png...");
    const tableElem = page.locator("div[data-testid='stDataFrame']");
    await tableElem.screenshot({ path: path.join(screenshotDir, "06_worker_list_escalated.png") });

    // 2. Cardiac Emergency Red Flag for Demo Patient B
    console.log("2. Cardiac Red Flag Presentation for Demo Patient B...");
    await page.goto("https://localhost/Worker_Triage", { waitUntil: "networkidle", timeout: 45000 });
    await page.waitForSelector("[data-testid='stAppViewContainer']", { timeout: 30000 });

    const nameInput2 = page.locator("input").first();
    await nameInput2.click();
    await nameInput2.fill(cardiacPatientName);
    await page.keyboard.press("Tab");
    await page.waitForTimeout(1000);

    const cardiacBtn = page.getByRole("button", { name: /Cardiac Emergency \(Red Flag\)|Cardiac/i });
    await cardiacBtn.click();
    await page.waitForTimeout(1000);

    const runCardiacBtn = page.getByRole("button", { name: /Run AI Diagnostic Analysis|Run Analysis/i });
    await runCardiacBtn.click();
    await page.waitForSelector("div[data-testid='stMetricValue']:has-text('Heart attack')", { timeout: 35000 });
    await page.waitForTimeout(2000);

    // Save Panel B: Red Flag Block (HTTP 409 Intercept)
    console.log("Saving clean 04_redflag_block.png...");
    await page.screenshot({
      path: path.join(screenshotDir, "04_redflag_block.png"),
      clip: { x: 0, y: 220, width: 1400, height: 700 },
    });

    // 3. Doctor Review Workstation
    console.log("3. Doctor Review Workstation...");
    await page.goto("https://localhost/Doctor_Review", { waitUntil: "networkidle", timeout: 45000 });
    await page.waitForSelector("[data-testid='stAppViewContainer']", { timeout: 30000 });
    await page.waitForTimeout(2000);

    console.log("Saving clean 07_doctor_queue_real.png...");
    await page.screenshot({
      path: path.join(screenshotDir, "07_doctor_queue_real.png"),
      clip: { x: 0, y: 120, width: 1400, height: 750 },
    });

    // Submit Doctor Response for Demo Patient A
    const diagInput = page.locator("input[aria-label*='Physician Final Diagnosis'], input[aria-label*='निदान']").first();
    if (await diagInput.isVisible()) {
      await diagInput.fill("Confirmed Jaundice / Acute Hepatitis with clinical correlation.");
    }
    const rxInput = page.locator("textarea[aria-label*='Prescription / advice'], textarea[aria-label*='दवाएं']").first();
    if (await rxInput.isVisible()) {
      await rxInput.fill("Prescribed oral rehydration salts, complete bed rest, low-fat bland diet, and LFT follow-up in 5 days.");
    }

    const submitDocBtn = page.getByRole("button", { name: /Submit Second Opinion|सबमिट/i });
    await submitDocBtn.click();
    await page.waitForTimeout(3000);

    console.log("Saving clean 08_doctor_response.png...");
    await page.screenshot({
      path: path.join(screenshotDir, "08_doctor_response.png"),
      clip: { x: 0, y: 140, width: 1400, height: 750 },
    });

    // 4. Worker Sees Reviewed Case
    console.log("4. Worker verifying 'reviewed' case status...");
    await page.goto("https://localhost/Worker_Triage", { waitUntil: "networkidle", timeout: 45000 });
    await page.waitForSelector("[data-testid='stAppViewContainer']", { timeout: 30000 });
    await page.waitForTimeout(2500);

    console.log("Saving clean 09_worker_reviewed.png...");
    const reviewedTableElem = page.locator("div[data-testid='stDataFrame']");
    await reviewedTableElem.screenshot({ path: path.join(screenshotDir, "09_worker_reviewed.png") });

    // 5. Admin Dashboard with Live Telemetry
    console.log("5. Admin Dashboard with live data...");
    await page.goto("https://localhost/Admin_Dashboard", { waitUntil: "networkidle", timeout: 45000 });
    await page.waitForSelector("[data-testid='stAppViewContainer']", { timeout: 30000 });
    await page.waitForTimeout(3000);

    console.log("Saving clean admin_dashboard_real.png...");
    await page.screenshot({
      path: path.join(screenshotDir, "admin_dashboard_real.png"),
      clip: { x: 0, y: 80, width: 1400, height: 800 },
    });

    console.log("=== All clean report screenshots captured successfully! ===");
  } catch (err) {
    console.error("Screenshot capture error:", err);
  } finally {
    await browser.close();
  }
}

main();
