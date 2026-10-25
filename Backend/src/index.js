import express from "express";
import cors from "cors";
import cookieParser from "cookie-parser";
import connectDB from "./config/dbConfig.js";
import serverConfig from "./config/serverConfig.js";
import adminRouter from "./routes/admin.routes.js";
import workerRouter from "./routes/worker.routes.js";
import doctorRouter from "./routes/doctor.routes.js";
import patientRouter from "./routes/patient.routes.js";
import consultationRouter from "./routes/consultation.routes.js";

const app = express();

// Middlewares
app.use(cors({
    origin: ['http://localhost:5173', 'http://127.0.0.1:5173'],
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization', 'Cookie'],
}));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(cookieParser());

// Health check
app.get("/", (req, res) => {
    res.json({ message: "Healthcare Decision Support API is running" });
});

// Routes
app.use("/api/v1/admin", adminRouter);
app.use("/api/v1/worker", workerRouter);
app.use("/api/v1/doctor", doctorRouter);
app.use("/api/v1/patient", patientRouter);
app.use("/api/v1/consultation", consultationRouter);

// Start server after DB connects
connectDB().then(() => {
    app.listen(serverConfig.PORT, () => {
        console.log(`Server is running on port ${serverConfig.PORT}`);
    });
});