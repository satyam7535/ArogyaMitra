import helmet from "helmet";

import rateLimit from "express-rate-limit";

import hpp from "hpp";



/**

 * Rate Limiter for Authentication Endpoints (Brute-force protection)

 * Limits each IP to 15 login/auth attempts per 15 minutes

 */

/**

 * Resolves the effective rate limit ceiling.

 * Production limits are strictly enforced: Auth: 15 req/15min, General API: 150 req/min.

 * Any relaxation (ALLOW_LOAD_TEST / DISABLE_RATE_LIMIT) is strictly rejected in production.

 */

export const resolveRateLimit = (type, defaultLimit) => {

  // Fail hard if relaxation is requested in production
  if (
    process.env.NODE_ENV === "production" &&
    (process.env.ALLOW_LOAD_TEST_RATE_LIMIT === "true" ||
      process.env.ALLOW_LOAD_TEST === "true" ||
      process.env.DISABLE_RATE_LIMIT === "true")
  ) {
    throw new Error(
      `SECURITY_VIOLATION: Rate limiter relaxation for ${type} is strictly forbidden in production mode (NODE_ENV=production).`
    );
  }

  const isLoadTestAllowed =
    process.env.NODE_ENV === "test" &&
    (process.env.ALLOW_LOAD_TEST_RATE_LIMIT === "true" ||
      process.env.ALLOW_LOAD_TEST === "true");

  if (isLoadTestAllowed) {

    if (process.env.NODE_ENV === "production") {

      throw new Error(

        `SECURITY_VIOLATION: Rate limiter relaxation for ${type} is strictly forbidden in production mode (NODE_ENV=production).`

      );

    }

    const envVar = type === "auth" ? process.env.LOAD_TEST_AUTH_MAX : process.env.LOAD_TEST_API_MAX;

    return envVar ? parseInt(envVar, 10) : 10000;

  }

  return defaultLimit;

};



export const createAuthLimiter = (max) => {

  const effectiveMax = max !== undefined ? max : resolveRateLimit("auth", 15);

  return rateLimit({

    windowMs: 15 * 60 * 1000, // 15 minutes

    max: effectiveMax,

    standardHeaders: true,

    legacyHeaders: false,

    keyGenerator: (req) => req.headers["x-forwarded-for"] || req.ip,

    message: {

      message: "Too many authentication attempts from this IP, please try again after 15 minutes.",

      code: "RATE_LIMIT_EXCEEDED",

    },

  });

};



export const createGeneralApiLimiter = (max) => {

  const effectiveMax = max !== undefined ? max : resolveRateLimit("general", 150);

  return rateLimit({

    windowMs: 60 * 1000, // 1 minute

    max: effectiveMax,

    standardHeaders: true,

    legacyHeaders: false,

    keyGenerator: (req) => req.headers["x-forwarded-for"] || req.ip,

    message: {

      message: "Too many requests from this IP, please try again shortly.",

      code: "RATE_LIMIT_EXCEEDED",

    },

  });

};



export const authRateLimiter = createAuthLimiter();

export const generalApiLimiter = createGeneralApiLimiter();



/**

 * CSRF Protection for state-mutating requests

 * Safe methods (GET, HEAD, OPTIONS) are exempt.

 * API calls with Authorization: Bearer <token> header are exempt (stateless, immune to ambient cookie CSRF).

 * Cookie-authenticated requests (where token or refreshToken cookie is present) MUST provide custom header

 * X-Requested-With or X-CSRF-Token.

 */

export const csrfProtectionMiddleware = (req, res, next) => {

  if (["GET", "HEAD", "OPTIONS"].includes(req.method)) {

    return next();

  }



  const authHeader = req.headers.authorization;

  if (authHeader && authHeader.startsWith("Bearer ")) {

    return next();

  }



  // If request relies on cookie authentication, enforce anti-CSRF custom header

  if (req.cookies && (req.cookies.token || req.cookies.refreshToken)) {

    const csrfHeader = req.headers["x-requested-with"] || req.headers["x-csrf-token"];

    if (!csrfHeader) {

      return res.status(403).json({

        message: "CSRF protection triggered: missing custom header (X-Requested-With or X-CSRF-Token)",

        code: "CSRF_ERROR",

      });

    }

  }



  next();

};



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



  // 5. CSRF Protection for ambient cookie-authenticated mutations

  app.use(csrfProtectionMiddleware);

};

