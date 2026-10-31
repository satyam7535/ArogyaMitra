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
 * Keyring lookup supporting zero-downtime key rotation
 * Reads optional ENCRYPTION_KEY_RING environment JSON: {"k1":"secret1","k2":"secret2"}
 */
export const getKeyForKeyId = (keyId) => {
  if (keyId && process.env.ENCRYPTION_KEY_RING) {
    try {
      const ring = JSON.parse(process.env.ENCRYPTION_KEY_RING);
      if (ring[keyId]) {
        return deriveKey(ring[keyId]);
      }
    } catch {}
  }
  return getDerivedKey();
};

/**
 * AES-256-GCM Field-Level Encryption
 * Supports both standard 3-part (iv:authTag:encrypted) and versioned Key ID 4-part (keyId:iv:authTag:encrypted)
 */
export const encryptField = (plainText, keyId = null, keyString = null) => {
  if (!plainText) return plainText;
  const key = keyString ? deriveKey(keyString) : (keyId ? getKeyForKeyId(keyId) : getDerivedKey());
  const effectiveKeyId = keyId || (process.env.ACTIVE_KEY_ID || null);
  const iv = crypto.randomBytes(12);
  const cipher = crypto.createCipheriv("aes-256-gcm", key, iv);
  let encrypted = cipher.update(String(plainText), "utf8", "hex");
  encrypted += cipher.final("hex");
  const authTag = cipher.getAuthTag().toString("hex");
  if (effectiveKeyId) {
    return `${effectiveKeyId}:${iv.toString("hex")}:${authTag}:${encrypted}`;
  }
  return `${iv.toString("hex")}:${authTag}:${encrypted}`;
};

export const decryptField = (cipherText, overrideKey = null) => {
  if (!cipherText || typeof cipherText !== "string") return cipherText;
  const parts = cipherText.split(":");
  let ivHex, authTagHex, encryptedHex;
  let keyToUse = overrideKey ? deriveKey(overrideKey) : getDerivedKey();

  if (parts.length === 4) {
    // Versioned Key ID format: keyId:iv:authTag:encrypted
    const [keyId] = parts;
    [, ivHex, authTagHex, encryptedHex] = parts;
    if (!overrideKey) {
      keyToUse = getKeyForKeyId(keyId);
    }
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
      keyToUse,
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
 * Key Rotation Helper:
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
  if (hashedPassword.startsWith("$argon2")) {
    try {
      return await argon2.verify(hashedPassword, plainPassword);
    } catch {
      return false;
    }
  }
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

/**
 * HMAC Blind Index for privacy-preserving exact match / duplicate detection on phone number.
 * Normalizes phone number (digits only) and hashes via HMAC-SHA256 with key.
 * Strictly only the phone number is hashed with HMAC, not name.
 */
export const computePhoneBlindIndex = (phoneNumber, secretKey = null) => {
  if (!phoneNumber) return null;
  let normPhone = String(phoneNumber).replace(/[^0-9]/g, "").trim();
  if (normPhone.length > 10 && normPhone.startsWith("91")) {
    normPhone = normPhone.slice(-10);
  } else if (normPhone.length > 10 && normPhone.startsWith("0")) {
    normPhone = normPhone.slice(-10);
  }
  if (!normPhone) return null;
  const key = secretKey || serverConfig.ENCRYPTION_KEY || "default_hmac_secret_for_blind_index";
  return crypto.createHmac("sha256", key).update(normPhone).digest("hex");
};
