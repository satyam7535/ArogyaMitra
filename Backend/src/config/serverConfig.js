import dotenv from "dotenv";
import { z } from "zod";

dotenv.config();

const envSchema = z.object({
  PORT: z.coerce.number().default(5000),
  DB_URL: z.string().min(1, "DB_URL is required"),
  JWT_SECRET: z.string().min(32, "JWT_SECRET must be at least 32 characters long for cryptographic security"),
  JWT_EXPIRY: z.string().default("15m"),
  REFRESH_TOKEN_EXPIRY: z.string().default("7d"),
  NODE_ENV: z.enum(["development", "production", "test"]).default("development"),
  FRONTEND_URL: z.string().default("http://localhost:5173"),
  ML_API_URL: z.string().default("http://localhost:8000"),
  GRAPH_API_URL: z.string().default("http://localhost:8001"),
  ENCRYPTION_KEY: z.string().min(32, "ENCRYPTION_KEY must be at least 32 characters for AES-256-GCM").default("arogyamitra_aes_256_secret_key_32bytes!"),
  OTPEMAIL: z.string().optional(),
  OTPPASSWORD: z.string().optional(),
  CLOUDINARY_CLOUD_NAME: z.string().optional(),
  CLOUDINARY_API_KEY: z.string().optional(),
  CLOUDINARY_API_SECRET: z.string().optional(),
});

const parsed = envSchema.safeParse(process.env);

if (!parsed.success) {
  console.error("FATAL: Environment validation failed:");
  console.error(JSON.stringify(parsed.error.format(), null, 2));
  if (process.env.NODE_ENV !== "test") {
    process.exit(1);
  }
}

const config = parsed.success ? parsed.data : {
  PORT: 5000,
  DB_URL: process.env.DB_URL || "mongodb://127.0.0.1:27017/arogyamitra_test",
  JWT_SECRET: process.env.JWT_SECRET || "arogyamitra_local_dev_secret_key_minimum_32_characters_length",
  JWT_EXPIRY: "15m",
  REFRESH_TOKEN_EXPIRY: "7d",
  NODE_ENV: "test",
  FRONTEND_URL: "http://localhost:5173",
  ML_API_URL: "http://localhost:8000",
  GRAPH_API_URL: "http://localhost:8001",
  ENCRYPTION_KEY: "arogyamitra_aes_256_secret_key_32bytes!",
};

export default config;
