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
      enum: ["Male", "Female", "Other", "male", "female", "other"],
      required: true,
    },
    phoneNumber: {
      type: String, // Encrypted at rest via AES-256-GCM
    },
    blindIndex: {
      type: String, // Keyed HMAC blind index of (phone + name) for duplicate warning
      index: true,
    },
    address: {
      type: String, // Encrypted at rest via AES-256-GCM
    },
    medicalHistory: {
      type: String, // Encrypted at rest via AES-256-GCM (Stage 2 D8)
    },
    emergencyContact: {
      name: { type: String }, // Encrypted at rest
      phoneNumber: { type: String }, // Encrypted at rest
      relationship: { type: String },
    },
    consentGiven: {
      type: Boolean,
      default: true,
      required: true,
    },
    consentLanguage: {
      type: String,
      enum: ["en", "hi", "mr", "English", "Hindi", "Marathi"],
      default: "en",
      required: true,
    },
    consentVersion: {
      type: String,
      default: "1.0",
      required: true,
    },
    consentTimestamp: {
      type: Date,
      default: Date.now,
    },
    consentWithdrawnAt: {
      type: Date,
      default: null,
    },
    consentWithdrawalReason: {
      type: String,
      default: null,
    },
    exportApproved: {
      type: Boolean,
      default: false,
    },
    exportApprovedBy: {
      type: mongoose.Schema.Types.ObjectId,
      ref: "Admin",
      default: null,
    },
    deletionApproved: {
      type: Boolean,
      default: false,
    },
    deletionApprovedBy: {
      type: mongoose.Schema.Types.ObjectId,
      ref: "Admin",
      default: null,
    },
    revokedAt: {
      type: Date,
      default: null,
    },
    isDeleted: {
      type: Boolean,
      default: false,
    },
    deletedAt: {
      type: Date,
      default: null,
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

// Encrypt sensitive PII before saving to MongoDB (AES-256-GCM)
patientSchema.pre("save", function () {
  if (this.isModified("phoneNumber") && this.phoneNumber) {
    this.phoneNumber = encryptField(this.phoneNumber);
  }
  if (this.isModified("address") && this.address) {
    this.address = encryptField(this.address);
  }
  if (this.isModified("medicalHistory") && this.medicalHistory) {
    this.medicalHistory = encryptField(this.medicalHistory);
  }
  if (this.emergencyContact) {
    if (this.isModified("emergencyContact.name") && this.emergencyContact.name) {
      this.emergencyContact.name = encryptField(this.emergencyContact.name);
    }
    if (this.isModified("emergencyContact.phoneNumber") && this.emergencyContact.phoneNumber) {
      this.emergencyContact.phoneNumber = encryptField(this.emergencyContact.phoneNumber);
    }
  }
});

// Instance method to retrieve decrypted patient PII
patientSchema.methods.getDecrypted = function () {
  const obj = this.toObject();
  if (obj.phoneNumber) obj.phoneNumber = decryptField(obj.phoneNumber);
  if (obj.address) obj.address = decryptField(obj.address);
  if (obj.medicalHistory) obj.medicalHistory = decryptField(obj.medicalHistory);
  if (obj.emergencyContact) {
    if (obj.emergencyContact.name) {
      obj.emergencyContact.name = decryptField(obj.emergencyContact.name);
    }
    if (obj.emergencyContact.phoneNumber) {
      obj.emergencyContact.phoneNumber = decryptField(obj.emergencyContact.phoneNumber);
    }
  }
  return obj;
};

export default mongoose.model("Patient", patientSchema);
