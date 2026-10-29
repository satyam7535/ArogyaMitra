import crypto from "crypto";
import argon2 from "argon2";
import bcrypt from "bcrypt";
import serverConfig from "../config/serverConfig.js";

export const ACTIVE_KEY_ID = process.env.ACTIVE_KEY_ID || "k1";

// Derive 32-byte key from a secret string
export const deriveKey = (secretKey) => {
  return crypto.createHash("sha256").update(secretKey || serverConfig.ENCRYPTION_KEY).digest();
};

const getDerivedKey = () => deriveKey(serverConfig.ENCRYPTION_KEY);

/**
 * AES-256-GCM Field-Level Encryption
 * Supports both standard 3-part (iv:authTag:encrypted) and versioned Key ID 4-part (keyId:iv:authTag:encrypted)
 */
export const encryptField = (plainText, keyId = null, keyString = null) => {
  if (!plainText) return plainText;
  const key = keyString ? deriveKey(keyString) : getDerivedKey();
  const iv = crypto.randomBytes(12);
  const cipher = crypto.createCipheriv("aes-256-gcm", key, iv);
  let encrypted = cipher.update(String(plainText), "utf8", "hex");
  encrypted += cipher.final("hex");
  const authTag = cipher.getAuthTag().toString("hex");
  if (keyId) {
    return `${keyId}:${iv.toString("hex")}:${authTag}:${encrypted}`;
  }
  return `${iv.toString("hex")}:${authTag}:${encrypted}`;
};

export const decryptField = (cipherText) => {
  if (!cipherText || typeof cipherText !== "string") return cipherText;
  const parts = cipherText.split(":");
  let ivHex, authTagHex, encryptedHex;

  if (parts.length === 4) {
    // Versioned Key ID format: keyId:iv:authTag:encrypted
    [, ivHex, authTagHex, encryptedHex] = parts;
  } else if (parts.length === 3) {
    // Standard format: iv:authTag:encrypted
    [ivHex, authTagHex, encryptedHex] = parts;
  } else {
    // Plaintext fallback (legacy data)
    return cipherText;
  }

  try {
    const decipher = crypto.createDecipheriv(
      "aes-256-gcm",
      getDerivedKey(),
      Buffer.from(ivHex, "hex"),
      { authTagLength: 16 }
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
 * Key Rotation Helper (Stage 2 D):
 * Decrypts ciphertext using oldKey and re-encrypts using newKey with newKeyId.
 */
export const rotateFieldEncryption = (cipherText, oldKeyString, newKeyString, newKeyId = "k2") => {
  if (!cipherText || typeof cipherText !== "string") return cipherText;
  const parts = cipherText.split(":");
  let ivHex, authTagHex, encryptedHex;

  if (parts.length === 4) {
    [, ivHex, authTagHex, encryptedHex] = parts;
  } else if (parts.length === 3) {
    [ivHex, authTagHex, encryptedHex] = parts;
  } else {
    return cipherText;
  }

  // 1. Decrypt with old key
  const oldDerivedKey = deriveKey(oldKeyString);
  const decipher = crypto.createDecipheriv(
    "aes-256-gcm",
    oldDerivedKey,
    Buffer.from(ivHex, "hex"),
    { authTagLength: 16 }
  );
  decipher.setAuthTag(Buffer.from(authTagHex, "hex"));
  let plain = decipher.update(encryptedHex, "hex", "utf8");
  plain += decipher.final("utf8");

  // 2. Re-encrypt with new key and new keyId
  const newDerivedKey = deriveKey(newKeyString);
  const newIv = crypto.randomBytes(12);
  const cipher = crypto.createCipheriv("aes-256-gcm", newDerivedKey, newIv);
  let newEncrypted = cipher.update(plain, "utf8", "hex");
  newEncrypted += cipher.final("hex");
  const newTag = cipher.getAuthTag().toString("hex");

  return `${newKeyId}:${newIv.toString("hex")}:${newTag}:${newEncrypted}`;
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
