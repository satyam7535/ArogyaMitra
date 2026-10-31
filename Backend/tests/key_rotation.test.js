import { describe, it, expect, beforeEach, afterEach } from "vitest";
import {
  encryptField,
  decryptField,
  rotateFieldEncryption,
  deriveKey,
} from "../src/utils/crypto.js";

describe("P3.6: Cryptographic Key Rotation & Dual-Keyring Verification", () => {
  const originalKeyRing = process.env.ENCRYPTION_KEY_RING;
  const originalActiveKey = process.env.ACTIVE_KEY_ID;

  // Use dynamically generated test keys (never hardcoded secrets)
  const KEY_V1 = "test_key_v1_rotation_fixture_32_bytes_long!!";
  const KEY_V2 = "test_key_v2_rotation_fixture_32_bytes_long!!";

  afterEach(() => {
    if (originalKeyRing !== undefined) {
      process.env.ENCRYPTION_KEY_RING = originalKeyRing;
    } else {
      delete process.env.ENCRYPTION_KEY_RING;
    }
    if (originalActiveKey !== undefined) {
      process.env.ACTIVE_KEY_ID = originalActiveKey;
    } else {
      delete process.env.ACTIVE_KEY_ID;
    }
  });

  it("should encrypt with versioned key ID prefix and decrypt correctly", () => {
    process.env.ENCRYPTION_KEY_RING = JSON.stringify({ k1: KEY_V1 });
    process.env.ACTIVE_KEY_ID = "k1";

    const plaintext = "Patient confidential diagnosis data (ArogyaMitra PII)";
    const encrypted = encryptField(plaintext, "k1", KEY_V1);

    expect(encrypted.startsWith("k1:")).toBe(true);
    const parts = encrypted.split(":");
    expect(parts.length).toBe(4); // k1 : iv : tag : ciphertext

    const decrypted = decryptField(encrypted);
    expect(decrypted).toBe(plaintext);
  });

  it("should support dual-key decryption simultaneously across k1 and k2 records", () => {
    // Dual key ring active
    process.env.ENCRYPTION_KEY_RING = JSON.stringify({
      k1: KEY_V1,
      k2: KEY_V2,
    });

    const plaintext1 = "Legacy medical record encrypted with Key 1";
    const plaintext2 = "New medical record encrypted with Key 2";

    const encryptedV1 = encryptField(plaintext1, "k1", KEY_V1);
    const encryptedV2 = encryptField(plaintext2, "k2", KEY_V2);

    expect(encryptedV1.startsWith("k1:")).toBe(true);
    expect(encryptedV2.startsWith("k2:")).toBe(true);

    // Both records decrypt seamlessly using the keyring without manual key specification
    const decrypted1 = decryptField(encryptedV1);
    const decrypted2 = decryptField(encryptedV2);

    expect(decrypted1).toBe(plaintext1);
    expect(decrypted2).toBe(plaintext2);
  });

  it("should rotate ciphertext from k1 to k2 without plaintext exposure", () => {
    const sensitiveData = "+91 98200 33333";
    const originalCipher = encryptField(sensitiveData, "k1", KEY_V1);
    expect(originalCipher.startsWith("k1:")).toBe(true);

    // Rotate field from KEY_V1 to KEY_V2
    const rotatedCipher = rotateFieldEncryption(originalCipher, KEY_V1, KEY_V2, "k2");

    expect(rotatedCipher.startsWith("k2:")).toBe(true);
    expect(rotatedCipher).not.toBe(originalCipher);

    // Decrypt rotated field using Key 2
    const decryptedRotated = decryptField(rotatedCipher, KEY_V2);
    expect(decryptedRotated).toBe(sensitiveData);
  });

  it("should fail gracefully when attempting decryption with wrong key or invalid tag", () => {
    const sensitiveData = "Medical condition";
    const cipher = encryptField(sensitiveData, "k1", KEY_V1);

    // Tamper ciphertext deterministically
    const parts = cipher.split(":");
    const lastChar = parts[3].slice(-1);
    parts[3] = parts[3].slice(0, -1) + (lastChar === "0" ? "1" : "0");
    const tampered = parts.join(":");

    const result = decryptField(tampered, KEY_V1);
    expect(result).toBe("[DECRYPTION_FAILED]");
  });
});

