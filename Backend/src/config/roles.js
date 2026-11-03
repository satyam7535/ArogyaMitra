/**
 * Canonical Role Definitions for ArogyaMitra
 * Single source of truth across JWT payloads, Mongoose schemas, and Route authorization guards.
 */

export const ROLES = Object.freeze({
  ADMIN: "Admin",
  WORKER: "Worker",
  DOCTOR: "Doctor",
});

export const ALL_ROLES = Object.freeze(Object.values(ROLES));

export default ROLES;

