import crypto from "crypto";

const SENSITIVE_KEYS = new Set([
  "password",
  "token",
  "refreshtoken",
  "authorization",
  "name",
  "patientname",
  "phonenumber",
  "address",
  "medicalhistory",
  "email",
  "resetpasswordtoken",
]);

/**
 * Recursively sanitize an object to strip or redact PII fields
 */
export const sanitizeForLogging = (data) => {
  if (!data || typeof data !== "object") return data;
  if (Array.isArray(data)) return data.map(sanitizeForLogging);

  const clean = {};
  for (const [key, value] of Object.entries(data)) {
    const lowerKey = key.toLowerCase();
    if (SENSITIVE_KEYS.has(lowerKey)) {
      clean[key] = "[REDACTED_PII]";
    } else if (value && typeof value === "object") {
      clean[key] = sanitizeForLogging(value);
    } else {
      clean[key] = value;
    }
  }
  return clean;
};

/**
 * Assign unique Request ID to each incoming HTTP request and set response header
 */
export const requestIdMiddleware = (req, res, next) => {
  const reqId = req.headers["x-request-id"] || crypto.randomUUID();
  req.id = reqId;
  res.setHeader("X-Request-Id", reqId);
  next();
};

/**
 * Structured PII-Free JSON logging middleware
 */
export const piiFreeLoggingMiddleware = (req, res, next) => {
  const start = Date.now();

  res.on("finish", () => {
    // Only log in non-test environments or when explicitly enabled
    if (process.env.NODE_ENV === "test" && !process.env.ENABLE_TEST_LOGS) return;

    const durationMs = Date.now() - start;
    const logEntry = {
      timestamp: new Date().toISOString(),
      requestId: req.id,
      method: req.method,
      path: req.originalUrl || req.url,
      statusCode: res.statusCode,
      durationMs,
      role: req.user?.role || "Anonymous",
      organization: req.user?.organization || null,
    };

    // If query parameters exist, sanitize before attaching
    if (req.query && Object.keys(req.query).length > 0) {
      logEntry.query = sanitizeForLogging(req.query);
    }

    console.log(JSON.stringify(logEntry));
  });

  next();
};

