import crypto from "crypto";
import argon2 from "argon2";
import bcrypt from "bcrypt";
import serverConfig from "../config/serverConfig.js";

// Ensure a 32-byte key from ENCRYPTION_KEY
const getDerivedKey = () => {
  return crypto.createHash("sha256").update(serverConfig.ENCRYPTION_KEY).digest();
};

/**
 * AES-256-GCM Field-Level Encryption
 * Format: ivHex:authTagHex:encryptedHex
 */
export const encryptField = (plainText) => {
  if (!plainText) return plainText;
  const iv = crypto.randomBytes(12);
  const cipher = crypto.createCipheriv("aes-256-gcm", getDerivedKey(), iv);
  let encrypted = cipher.update(String(plainText), "utf8", "hex");
  encrypted += cipher.final("hex");
  const authTag = cipher.getAuthTag().toString("hex");
  return `${iv.toString("hex")}:${authTag}:${encrypted}`;
};

export const decryptField = (cipherText) => {
  if (!cipherText || typeof cipherText !== "string") return cipherText;
  const parts = cipherText.split(":");
  if (parts.length !== 3) {
    // Plaintext fallback (e.g. legacy data before encryption)
    return cipherText;
  }
  const [ivHex, authTagHex, encryptedHex] = parts;
  try {
    const decipher = crypto.createDecipheriv(
      "aes-256-gcm",
      getDerivedKey(),
      Buffer.from(ivHex, "hex")
    );
    decipher.setAuthTag(Buffer.from(authTagHex, "hex"));
    let decrypted = decipher.update(encryptedHex, "hex", "utf8");
    decrypted += decipher.final("utf8");
    return decrypted;
  } catch (err) {
    console.error("Failed to decrypt field:", err.message);
    return "[DECRYPTION_FAILED]";
  }
};

/**
 * Password Hashing with Argon2id & Backward-Compatible Bcrypt Fallback
 */
export const hashPassword = async (plainPassword) => {
  return await argon2.hash(plainPassword, {
    type: argon2.argon2id,
    memoryCost: 2 ** 16, // 64 MB
    timeCost: 3,
    parallelism: 1,
  });
};

export const verifyPassword = async (hashedPassword, plainPassword) => {
  if (!hashedPassword || !plainPassword) return false;
  // If it's an Argon2 hash ($argon2id$ or $argon2i$)
  if (hashedPassword.startsWith("$argon2")) {
    try {
      return await argon2.verify(hashedPassword, plainPassword);
    } catch {
      return false;
    }
  }
  // Fallback to bcrypt for legacy records
  try {
    return await bcrypt.compare(plainPassword, hashedPassword);
  } catch {
    return false;
  }
};

/**
 * Cryptographically Secure Token Generation & Hashing
 */
export const generateSecureToken = (bytes = 32) => {
  return crypto.randomBytes(bytes).toString("hex");
};

export const hashToken = (token) => {
  return crypto.createHash("sha256").update(token).digest("hex");
};
