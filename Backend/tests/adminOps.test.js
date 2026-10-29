import { describe, it, expect, vi } from "vitest";
import { sanitizeCsvField, exportConsultationsCsv } from "../src/service/admin.service.js";

describe("WP5 — Step 13: Admin Overview, Operations & CSV Injection Protection", () => {
  describe("5.3 CSV Formula Injection Neutralization", () => {
    it("should prepend single quote to formula trigger characters (=, +, -, @)", () => {
      expect(sanitizeCsvField("=SUM(A1:A10)")).toBe("'=SUM(A1:A10)");
      expect(sanitizeCsvField("+cmd|' /C calc'!A0")).toBe("'+cmd|' /C calc'!A0");
      expect(sanitizeCsvField("-10+20")).toBe("'-10+20");
      expect(sanitizeCsvField("@SUM(1,2)")).toBe("'@SUM(1,2)");
    });

    it("should leave benign text unchanged", () => {
      expect(sanitizeCsvField("Fungal Infection")).toBe("Fungal Infection");
      expect(sanitizeCsvField("Patient Aarav Sharma")).toBe("Patient Aarav Sharma");
      expect(sanitizeCsvField("Normal note")).toBe("Normal note");
    });

    it("should handle null and undefined safely", () => {
      expect(sanitizeCsvField(null)).toBe("");
      expect(sanitizeCsvField(undefined)).toBe("");
    });
  });
});
