import dotenv from "dotenv";
import path from "path";
import { fileURLToPath } from "url";
import { z } from "zod";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
// Prioritize Backend/.env, fallback to process.cwd()/.env
dotenv.config({ path: path.resolve(__dirname, "../../.env") });
dotenv.config();

export const envSchema = z.object({
  PORT: z.coerce.number().default(5000),
  DB_URL: z.string().min(1, "DB_URL is required"),
  JWT_SECRET: z.string().min(32, "JWT_SECRET must be at least 32 characters long for cryptographic security"),
  JWT_EXPIRY: z.string().default("15m"),
  REFRESH_TOKEN_EXPIRY: z.string().default("7d"),
  NODE_ENV: z.enum(["development", "production", "test"]).default("development"),
  FRONTEND_URL: z.string().default("http://localhost:5173"),
  ML_API_URL: z.string().default("http://localhost:8000"),
  GRAPH_API_URL: z.string().default("http://localhost:8001"),
  INTERNAL_SERVICE_SECRET: z.string().min(32, "INTERNAL_SERVICE_SECRET must be at least 32 characters"),
  ENCRYPTION_KEY: z.string().min(32, "ENCRYPTION_KEY must be at least 32 characters for AES-256-GCM"),
  OTPEMAIL: z.string().optional(),
  OTPPASSWORD: z.string().optional(),
  CLOUDINARY_CLOUD_NAME: z.string().optional(),
  CLOUDINARY_API_KEY: z.string().optional(),
  CLOUDINARY_API_SECRET: z.string().optional(),
});

const parsed = envSchema.safeParse(process.env);

if (!parsed.success) {
  console.error("FATAL: Environment validation failed. System refusing to start:");
  console.error(JSON.stringify(parsed.error.format(), null, 2));
  if (process.env.NODE_ENV !== "test") {
    process.exit(1);
  }
  throw new Error(`Environment validation failed: ${JSON.stringify(parsed.error.format())}`);
}

const serverConfig = parsed.data;

export default serverConfig;
