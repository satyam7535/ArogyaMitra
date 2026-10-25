import express from "express";
import cors from "cors";
import cookieParser from "cookie-parser";
import connectDB from "./config/dbConfig.js";
import serverConfig from "./config/serverConfig.js";
import { applySecurityMiddlewares, generalApiLimiter } from "./middlewares/security.middleware.js";
import adminRouter from "./routes/admin.routes.js";
import workerRouter from "./routes/worker.routes.js";
import doctorRouter from "./routes/doctor.routes.js";
import patientRouter from "./routes/patient.routes.js";
import consultationRouter from "./routes/consultation.routes.js";

const app = express();

// 1. Security Middlewares (Helmet, NoSQL Sanitize, HPP, disable x-powered-by)
applySecurityMiddlewares(app);

// 2. CORS configuration
const allowedOrigins = [
  serverConfig.FRONTEND_URL,
  "http://localhost:5173",
  "http://127.0.0.1:5173",
  "http://localhost:8501", // Streamlit UI
  "http://127.0.0.1:8501",
];

app.use(
  cors({
    origin: (origin, callback) => {
      // Allow requests with no origin (e.g. mobile apps, curl, server-to-server)
      if (!origin || allowedOrigins.includes(origin)) {
        return callback(null, true);
      }
      return callback(new Error("CORS policy violation: origin not allowed"), false);
    },
    credentials: true,
    methods: ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allowedHeaders: ["Content-Type", "Authorization", "Cookie", "X-Requested-With"],
  })
);

// 3. Body Parsing & Rate Limiting
app.use(express.json({ limit: "5mb" }));
app.use(express.urlencoded({ extended: true, limit: "5mb" }));
app.use(cookieParser());
app.use(generalApiLimiter);

// 4. Health and Root Check
app.get("/", (req, res) => {
  res.json({ message: "ArogyaMitra Healthcare Decision Support API is active", status: "running" });
});

app.get("/health", (req, res) => {
  res.status(200).json({ status: "healthy", service: "backend" });
});

// 5. Versioned API Routes
app.use("/api/v1/admin", adminRouter);
app.use("/api/v1/worker", workerRouter);
app.use("/api/v1/doctor", doctorRouter);
app.use("/api/v1/patient", patientRouter);
app.use("/api/v1/consultation", consultationRouter);

// 6. Global 404 Handler
app.use((req, res) => {
  res.status(404).json({ message: "Endpoint not found" });
});

// 7. Global Error Handler
app.use((err, req, res, next) => {
  console.error("[SERVER ERROR]", err);
  const statusCode = err.status || 500;
  res.status(statusCode).json({
    message: err.message || "Internal server error",
    code: err.code || "INTERNAL_ERROR",
  });
});

export const startServer = async () => {
  await connectDB();
  return app.listen(serverConfig.PORT, () => {
    console.log(`Server is running on port ${serverConfig.PORT} in ${serverConfig.NODE_ENV} mode`);
  });
};

if (process.env.NODE_ENV !== "test") {
  startServer().catch((err) => {
    console.error("Failed to start server:", err);
  });
}

export default app;