# ArogyaMitra Architecture & Design Decisions Log

This document records architectural, algorithmic, and engineering decisions following the format: Decision, Alternatives Considered, and Reasoning.

---

## DECISION-001: Model Selection — LightGBM with Dropout Augmentation and TreeSHAP
- **Date**: 2026-10-26
- **Status**: Accepted
- **Decision**: The core disease prediction model is LightGBM trained on symptom-dropout-augmented data, calibrated with probability calibration (isotonic or sigmoid based on ECE), and explained using TreeSHAP.
- **Alternatives Considered**:
  - *Random Forest*: Good baseline, robust to overfitting, but slower inference and less flexible for partial symptom dropouts compared to gradient boosted trees.
  - *XGBoost*: Strong competitor, but LightGBM offers faster training and native histogram-based splits that perform exceptionally well on sparse binary feature sets.
  - *LIME Explainer*: Perturbation-based explainer previously used in the notebook; slow, non-deterministic across calls, and can produce contradictory feature attributions.
- **Reasoning**: LightGBM provides fast, deterministic inference and pairs natively with TreeSHAP for exact, efficient Shapley value attribution. Augmented symptom dropout addresses the real-world reality where primary health workers observe only a subset of symptoms.

---

## DECISION-002: LLM Provider Configuration — Google Gemini via OpenAI-Compatible Endpoint
- **Date**: 2026-10-26
- **Status**: Accepted
- **Decision**: Exclusively use Google Gemini via its OpenAI-compatible endpoint (`https://generativelanguage.googleapis.com/v1beta/openai/`) using standardized environment variables: `LLM_API_KEY`, `LLM_BASE_URL`, and `LLM_MODEL`.
- **Alternatives Considered**:
  - *OpenAI*: Prohibited by project constraints and API cost requirements.
  - *Native google-genai SDK*: Viable, but standardizing on the OpenAI client interface allows uniform timeout, retry, structured JSON decoding, and mockability without extra SDK overhead.
- **Reasoning**: Adheres strictly to the user requirement for free-tier Gemini usage without OpenAI dependencies, while ensuring all automated tests mock LLM responses to conserve rate limits.

---

## DECISION-003: Removal of Client-Facing PDF Generator from ML Service
- **Date**: 2026-10-26
- **Status**: Accepted
- **Decision**: Remove PDF report generation from `ML_Model/app.py` and consolidate all PDF rendering within `graph/utils/pdf_generator.py`.
- **Alternatives Considered**:
  - *Duplicate PDF logic in both ML_Model and graph*: Redundant, error-prone, violates single source of truth.
- **Reasoning**: The ML service is dedicated to deterministic model inference, calibration, and explainability. PDF reporting requires clinical summaries from the LLM, making `graph/` (the orchestration service) the correct single home for report compilation.

---

## DECISION-004: Organization-Scoped Multi-Tenancy Architecture
- **Date**: 2026-10-26
- **Status**: Accepted (Planned for Phase 2)
- **Decision**: Direct `organization` (admin ID) field on all core collections (`Worker`, `Doctor`, `Patient`, `Consultation`) with central query-scoping middleware.
- **Alternatives Considered**:
  - *Relational joins / populated lookups*: Complex, fragile, prone to IDOR leaks if any lookup misses an org check.
  - *Separate database per tenant*: Overkill for a PHC decision-support system at this stage.
- **Reasoning**: Enforces strict authorization at the MongoDB query layer, preventing data leakage across healthcare centers.
