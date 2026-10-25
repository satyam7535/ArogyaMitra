import mongoose from "mongoose";
import serverConfig from "../config/serverConfig.js";
import Organization from "../models/organization/organizationSchema.js";
import Admin from "../models/admin/adminSchema.js";

const seedAdmin = async () => {
  try {
    console.log("[SEED] Connecting to database:", serverConfig.DB_URL);
    await mongoose.connect(serverConfig.DB_URL);
    console.log("[SEED] MongoDB connected successfully.");

    // 1. Ensure default Organization exists
    let org = await Organization.findOne({ code: "PHC_CENTRAL" });
    if (!org) {
      org = await Organization.create({
        name: "Central Primary Health Centre",
        code: "PHC_CENTRAL",
        active: true,
      });
      console.log("[SEED] Created default Organization:", org.name, `(${org.code})`);
    } else {
      console.log("[SEED] Default Organization exists:", org.name);
    }

    // 2. Ensure default Admin exists
    const adminEmail = process.env.ADMIN_EMAIL || "admin@arogyamitra.gov.in";
    const adminPassword = process.env.ADMIN_PASSWORD || "Admin@ArogyaMitra2026!";
    const adminPhone = process.env.ADMIN_PHONE || "+919876543210";

    let admin = await Admin.findOne({ email: adminEmail });
    if (!admin) {
      admin = await Admin.create({
        name: "District Medical Officer (Admin)",
        email: adminEmail,
        phoneNumber: adminPhone,
        location: "Gaya District PHC",
        organization: org._id,
        password: adminPassword, // Pre-save hook hashes with Argon2id
        role: "Admin",
      });
      console.log("[SEED] Admin account seeded successfully!");
      console.log("--------------------------------------------------");
      console.log("  Email:    ", adminEmail);
      console.log("  Password: ", adminPassword);
      console.log("  Org Code: ", org.code);
      console.log("--------------------------------------------------");
    } else {
      console.log("[SEED] Admin already exists with email:", adminEmail);
    }

    await mongoose.disconnect();
    console.log("[SEED] Database connection closed.");
    process.exit(0);
  } catch (err) {
    console.error("[SEED ERROR]", err);
    process.exit(1);
  }
};

seedAdmin();
