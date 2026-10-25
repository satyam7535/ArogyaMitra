import helmet from "helmet";
import rateLimit from "express-rate-limit";
import mongoSanitize from "express-mongo-sanitize";
import hpp from "hpp";

/**
 * Rate Limiter for Authentication Endpoints (Brute-force protection)
 * Limits each IP to 15 login/auth attempts per 15 minutes
 */
export const authRateLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 15,
  standardHeaders: true,
  legacyHeaders: false,
  message: {
    message: "Too many authentication attempts from this IP, please try again after 15 minutes.",
    code: "RATE_LIMIT_EXCEEDED",
  },
});

/**
 * General API Rate Limiter
 * Limits each IP to 150 requests per minute
 */
export const generalApiLimiter = rateLimit({
  windowMs: 60 * 1000, // 1 minute
  max: 150,
  standardHeaders: true,
  legacyHeaders: false,
  message: {
    message: "Too many requests from this IP, please try again shortly.",
    code: "RATE_LIMIT_EXCEEDED",
  },
});

/**
 * Configure standard security headers and sanitizers
 */
export const applySecurityMiddlewares = (app) => {
  // 1. Remove X-Powered-By
  app.disable("x-powered-by");

  // 2. Helmet Security Headers (HSTS, CSP, Frameguard, etc.)
  app.use(
    helmet({
      contentSecurityPolicy: {
        directives: {
          defaultSrc: ["'self'"],
          scriptSrc: ["'self'"],
          styleSrc: ["'self'", "'unsafe-inline'"],
          imgSrc: ["'self'", "data:", "https://res.cloudinary.com"],
          connectSrc: ["'self'", "http://localhost:8000", "http://localhost:8001"],
        },
      },
      crossOriginEmbedderPolicy: false,
      hsts: {
        maxAge: 31536000,
        includeSubDomains: true,
        preload: true,
      },
    })
  );

  // 3. NoSQL Injection Sanitization for Express 5 (strips keys containing $ or .)
  app.use((req, res, next) => {
    const sanitize = (obj) => {
      if (obj && typeof obj === "object") {
        for (const key of Object.keys(obj)) {
          if (key.startsWith("$") || key.includes(".")) {
            delete obj[key];
          } else {
            sanitize(obj[key]);
          }
        }
      }
    };
    if (req.body) sanitize(req.body);
    if (req.params) sanitize(req.params);
    next();
  });

  // 4. HTTP Parameter Pollution Protection
  app.use(hpp());
};
