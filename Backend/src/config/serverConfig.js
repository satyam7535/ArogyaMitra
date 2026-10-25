import dotenv from "dotenv";
dotenv.config();
// dotenv.config({ quiet: true });


const config = {
  PORT: process.env.PORT || 5000,
  DB_URL: process.env.DB_URL,
  JWT_SECRET: process.env.JWT_SECRET || "your-secret-key",
  JWT_EXPIRY: process.env.JWT_EXPIRY,
  OTPEMAIL: process.env.OTPEMAIL,
  OTPPASSWORD: process.env.OTPPASSWORD,
  NODE_ENV: process.env.NODE_ENV,
};

export default config;
