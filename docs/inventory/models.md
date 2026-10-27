# ArogyaMitra — Mongoose Data Models Inventory Map (`docs/inventory/models.md`)

This machine-readable map documents every Mongoose schema across `Backend/src/models/`, its defined fields, database indexes, field-level encryption, and concurrency versioning controls.

---

## Data Models Inventory

| Model Name | Source File | Key Fields | Database Indexes | Field-Level Encryption | Concurrency Versioning (OCC) | Compliance & Design Gaps |
| :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| **Organization** | [`organizationSchema.js`](file:///d:/Document/Projects/Internship/Arogyamitra/Backend/src/models/organization/organizationSchema.js) | `name`, `code`, `active` | `code` (Unique) | None | Default `__v` | None |
| **Admin** | [`adminSchema.js`](file:///d:/Document/Projects/Internship/Arogyamitra/Backend/src/models/admin/adminSchema.js) | `name`, `email`, `phoneNumber`, `location`, `organization`, `password`, `role`, `failedLoginAttempts`, `lockUntil`, `resetPasswordToken`, `resetPasswordExpires` | `email` (Unique)<br>`phoneNumber` (Unique)<br>`organization` (Index) | None (Password Argon2id hashed) | Default `__v` | No soft-delete flag (`isActive`/`deletedAt` missing). |
| **Worker** | [`workerSchema.js`](file:///d:/Document/Projects/Internship/Arogyamitra/Backend/src/models/worker/workerSchema.js) | `name`, `email`, `phoneNumber`, `password`, `role`, `organization`, `addedBy`, `failedLoginAttempts`, `lockUntil`, `resetPasswordToken`, `resetPasswordExpires` | `email` (Unique)<br>`phoneNumber` (Unique)<br>`organization` (Index) | None (Password Argon2id hashed) | Default `__v` | No soft-delete flag (admin deletes perform hard `findOneAndDelete`). |
| **Doctor** | [`doctorSchema.js`](file:///d:/Document/Projects/Internship/Arogyamitra/Backend/src/models/doctor/doctorSchema.js) | `name`, `email`, `phoneNumber`, `specialization`, `password`, `role`, `organization`, `addedBy`, `failedLoginAttempts`, `lockUntil`, `resetPasswordToken`, `resetPasswordExpires` | `email` (Unique)<br>`phoneNumber` (Unique)<br>`organization` (Index) | None (Password Argon2id hashed) | Default `__v` | No soft-delete flag (admin deletes perform hard `findOneAndDelete`). |
| **Patient** | [`patientSchema.js`](file:///d:/Document/Projects/Internship/Arogyamitra/Backend/src/models/patient/patientSchema.js) | `name`, `age`, `gender`, `phoneNumber`, `address`, `medicalHistory`, `registeredBy`, `organization` | `organization` (Index) | **AES-256-GCM** on:<br>- `phoneNumber`<br>- `address`<br>*(Note: `medicalHistory` is unencrypted)* | Default `__v`<br>*(OCC NOT enabled on Patient)* | - `medicalHistory` stored in cleartext (violates D8).<br>- No consent tracking fields (`consentCapturedAt`, `consentWithdrawn`).<br>- No duplicate detection hash. |
| **Consultation** | [`consultationSchema.js`](file:///d:/Document/Projects/Internship/Arogyamitra/Backend/src/models/consultation/consultationSchema.js) | `patient`, `submittedBy`, `assignedDoctor`, `organization`, `symptoms`, `notes`, `attachments`, `aiReport`, `analysisReport`, `mlAnalysis`, `llmAnalysis`, `finalVerdict`, `status`, `workerDecision`, `escalationReason`, `secondOpinion` | `organization` (Index) | None | **`optimisticConcurrency: true`** (Mongoose OCC enabled) | - No atomic state machine hooks enforcing valid status transitions (e.g., rejecting changes after `closed`).<br>- Compound index `{ organization: 1, status: 1 }` missing for high-volume queues. |
| **RefreshToken** | [`refreshTokenSchema.js`](file:///d:/Document/Projects/Internship/Arogyamitra/Backend/src/models/auth/refreshTokenSchema.js) | `tokenHash`, `userId`, `userModel`, `organization`, `familyId`, `isRevoked`, `expiresAt` | `tokenHash` (Unique)<br>`familyId` (Index)<br>`expiresAt` (TTL auto-purge `expires: 0`) | None (Token is SHA-256 hashed) | Default `__v` | None |
| **AuditLog** | [`auditLogSchema.js`](file:///d:/Document/Projects/Internship/Arogyamitra/Backend/src/models/audit/auditLogSchema.js) | `userId`, `userRole`, `action`, `resourceType`, `resourceId`, `organization`, `ipAddress`, `metadata` | `action` (Index)<br>`organization` (Index) | None | Default `__v` | Standard mutable MongoDB collection; no cryptographic chaining or admin read API. |

---

## Notable Data Layer Gaps

1. **`medicalHistory` Unencrypted**: Stored as raw plaintext in `Patient` schema, directly violating Requirement D8 (*"Field-level AES-256-GCM encryption for patient phone, address, medicalHistory, emergency contact"*).
2. **Missing Consent Tracking**: Zero DPDP consent fields on `Patient` schema (`consentCaptured`, `consentTimestamp`, `consentWithdrawn`).
3. **Hard Deletes**: Workers and Doctors are deleted using `findOneAndDelete` rather than soft-deactivation flags (`isActive: false`), destroying referential integrity with past consultations and audit history.
4. **No MongoDB Job Queue Collection**: Requirement E1 specifies a durable `jobs` collection in MongoDB. Currently, jobs are tracked strictly in an in-memory Node.js `Map()`.
