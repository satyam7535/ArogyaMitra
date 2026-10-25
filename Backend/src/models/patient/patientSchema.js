import mongoose from "mongoose";
import { encryptField, decryptField } from "../../utils/crypto.js";

const patientSchema = new mongoose.Schema(
  {
    name: {
      type: String,
      required: true,
      trim: true,
    },
    age: {
      type: Number,
      required: true,
    },
    gender: {
      type: String,
      enum: ["male", "female", "other"],
      required: true,
    },
    phoneNumber: {
      type: String, // Encrypted at rest via AES-256-GCM
    },
    address: {
      type: String, // Encrypted at rest via AES-256-GCM
    },
    medicalHistory: {
      type: String,
    },
    registeredBy: {
      type: mongoose.Schema.Types.ObjectId,
      ref: "Worker",
      required: true,
    },
    organization: {
      type: mongoose.Schema.Types.ObjectId,
      ref: "Organization",
      required: true,
      index: true,
    },
  },
  { timestamps: true }
);

// Encrypt sensitive PII before saving to MongoDB
patientSchema.pre("save", function () {
  if (this.isModified("phoneNumber") && this.phoneNumber) {
    this.phoneNumber = encryptField(this.phoneNumber);
  }
  if (this.isModified("address") && this.address) {
    this.address = encryptField(this.address);
  }
});

// Instance method to retrieve decrypted patient PII
patientSchema.methods.getDecrypted = function () {
  const obj = this.toObject();
  if (obj.phoneNumber) obj.phoneNumber = decryptField(obj.phoneNumber);
  if (obj.address) obj.address = decryptField(obj.address);
  return obj;
};

export default mongoose.model("Patient", patientSchema);
