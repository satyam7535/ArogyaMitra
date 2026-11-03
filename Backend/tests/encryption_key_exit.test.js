import { describe, it, expect } from "vitest";
import { spawnSync } from "child_process";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

describe("Production Startup Environment Validation", () => {
  it("must exit with non-zero code if ENCRYPTION_KEY is missing or invalid in production", () => {
    const indexPath = path.resolve(__dirname, "../src/index.js");
    const child = spawnSync(process.execPath, [indexPath], {
      cwd: path.resolve(__dirname, ".."),
      env: {
        ...process.env,
        NODE_ENV: "production",
        ENCRYPTION_KEY: "", // explicitly empty/missing
      },
      encoding: "utf8",
      timeout: 15000,
    });

    expect(child.status).toBe(1);
    expect(child.stderr).toContain("Environment validation failed");
    expect(child.stderr).toContain("ENCRYPTION_KEY");
  }, 20000);
});
