import { z } from "zod";

// MongoDB ObjectId 24-char hex string validator
const objectIdSchema = z.string().regex(/^[0-9a-fA-F]{24}$/, "Must be a valid 24-character hexadecimal ObjectId");

export const idParamSchema = z.object({
  id: objectIdSchema,
}).strict();

export const jobIdParamSchema = z.object({
  id: objectIdSchema,
  jobId: z.string().min(1, "Job ID is required"),
}).strict();

// ── Auth Schemas ─────────────────────────────────────────────────────────────
export const loginSchema = z.object({
  email: z.string().email("Valid email address is required"),
  password: z.string().min(1, "Password is required"),
}).strict();

export const refreshSchema = z.object({
  refreshToken: z.string().optional(),
}).strict();

export const forgotPasswordSchema = z.object({
  email: z.string().email("Valid email address is required"),
}).strict();

export const resetPasswordSchema = z.object({
  token: z.string().min(1, "Reset token is required"),
  newPassword: z.string().min(8, "Password must be at least 8 characters long"),
}).strict();

export const logoutSchema = z.object({
  refreshToken: z.string().optional(),
}).strict();

// ── Admin / User Management Schemas ──────────────────────────────────────────
export const createWorkerSchema = z.object({
  name: z.string().min(1, "Name is required").max(100),
  email: z.string().email("Valid email address is required"),
  phoneNumber: z.string().min(10, "Phone number must be at least 10 characters").max(20),
  password: z.string().min(8, "Password must be at least 8 characters long"),
}).strict();

export const createDoctorSchema = z.object({
  name: z.string().min(1, "Name is required").max(100),
  email: z.string().email("Valid email address is required"),
  phoneNumber: z.string().min(10, "Phone number must be at least 10 characters").max(20),
  password: z.string().min(8, "Password must be at least 8 characters long"),
  specialization: z.string().min(1, "Specialization is required"),
}).strict();

export const auditLogsQuerySchema = z.object({
  page: z.string().optional(),
  limit: z.string().optional(),
  action: z.string().optional(),
  resourceType: z.string().optional(),
  startDate: z.string().optional(),
  endDate: z.string().optional(),
}).strict();

// ── Patient Schemas ──────────────────────────────────────────────────────────
export const registerPatientSchema = z.object({
  name: z.string().min(1, "Patient name is required").max(100),
  age: z.union([z.number().int().min(0).max(130), z.string()]),
  gender: z.enum(["Male", "Female", "Other"]),
  phoneNumber: z.string().min(10, "Phone number must be at least 10 digits"),
  address: z.string().min(1, "Address is required"),
  medicalHistory: z.string().optional(),
  consentGiven: z.boolean().optional(),
  consentLanguage: z.enum(["en", "hi", "mr", "English", "Hindi", "Marathi"]).optional(),
  consentVersion: z.string().optional(),
  consentTimestamp: z.string().optional(),
  emergencyContact: z.object({
    name: z.string().optional(),
    phoneNumber: z.string().optional(),
    relationship: z.string().optional(),
  }).optional(),
}).strict();

export const withdrawConsentSchema = z.object({
  reason: z.string().min(1, "Withdrawal reason is required"),
}).strict();

// ── Consultation Schemas ─────────────────────────────────────────────────────
export const submitConsultationSchema = z.object({
  patientId: objectIdSchema,
  symptoms: z.union([z.array(z.string()), z.string()]),
  notes: z.string().optional(),
}).strict();

export const acceptConsultationSchema = z.object({
  notes: z.string().optional(),
  decisionOutcome: z.enum(["accepted", "referred_to_hospital"]).optional(),
  overrideReason: z.enum([
    "patient_improved",
    "referred_in_person",
    "doctor_unreachable",
    "patient_declined_referral",
    "other",
  ]).optional(),
  overrideNote: z.string().trim().min(10, "Override note must be at least 10 non-whitespace characters").optional(),
}).strict();

export const escalateConsultationSchema = z.object({
  reason: z.string().min(1, "Escalation reason is required"),
  doctorId: objectIdSchema.optional(),
  targetDoctorId: objectIdSchema.optional(),
}).strict();

export const respondConsultationSchema = z.object({
  diagnosis: z.string().optional(),
  recommendation: z.string().optional(),
  doctorNotes: z.string().optional(),
  prescription: z.array(z.any()).optional(),
  diagnosisConfirmed: z.boolean().optional(),
  version: z.number().int().optional(),
}).strict();

export const analyzeConsultationSchema = z.object({
  symptoms: z.array(z.string()).optional(),
  language: z.enum(["en", "hi", "mr"]).optional(),
}).strict();
