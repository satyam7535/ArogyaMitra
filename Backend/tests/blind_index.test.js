import { describe, it, expect } from "vitest";
import { computePhoneBlindIndex } from "../src/utils/crypto.js";
import { computePatientBlindIndex } from "../src/service/patient.service.js";

describe("HMAC Blind Index Phone Alignment (P3.10)", () => {
  const secretKey = "test_hmac_secret_key_32_bytes_long!!";

  it("should compute deterministic HMAC blind index for a phone number", () => {
    const idx1 = computePhoneBlindIndex("9876543210", secretKey);
    const idx2 = computePhoneBlindIndex("9876543210", secretKey);
    expect(idx1).toBeTypeOf("string");
    expect(idx1).toHaveLength(64); // SHA-256 hex
    expect(idx1).toBe(idx2);
  });

  it("should normalize phone numbers regardless of punctuation and formatting", () => {
    const raw = "9876543210";
    const formatted1 = "+91 98765 43210";
    const formatted2 = "(987) 654-3210";
    const formatted3 = "9876-543-210";

    const idxRaw = computePhoneBlindIndex(raw, secretKey);
    const idx1 = computePhoneBlindIndex(formatted1, secretKey);
    const idx2 = computePhoneBlindIndex(formatted2, secretKey);
    const idx3 = computePhoneBlindIndex(formatted3, secretKey);

    expect(idx1).toBe(idxRaw);
    expect(idx2).toBe(idxRaw);
    expect(idx3).toBe(idxRaw);
  });

  it("should strictly ignore patient name and only hash phone number", () => {
    const phone = "9876543210";
    const idxNameA = computePatientBlindIndex("Aarav Sharma", phone);
    const idxNameB = computePatientBlindIndex("Pooja Patel", phone);
    const idxDirect = computePhoneBlindIndex(phone);

    expect(idxNameA).toBe(idxNameB);
    expect(idxNameA).toBe(idxDirect);
  });

  it("should produce distinct hashes for different phone numbers", () => {
    const idx1 = computePhoneBlindIndex("9876543210", secretKey);
    const idx2 = computePhoneBlindIndex("9876543211", secretKey);
    expect(idx1).not.toBe(idx2);
  });

  it("should produce distinct hashes when keyed with different secret keys", () => {
    const phone = "9876543210";
    const idx1 = computePhoneBlindIndex(phone, "secret_key_1");
    const idx2 = computePhoneBlindIndex(phone, "secret_key_2");
    expect(idx1).not.toBe(idx2);
  });

  it("should return null for empty or null phone inputs", () => {
    expect(computePhoneBlindIndex(null)).toBeNull();
    expect(computePhoneBlindIndex("")).toBeNull();
    expect(computePhoneBlindIndex("   ")).toBeNull();
  });
});
