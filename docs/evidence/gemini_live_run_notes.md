# Gemini Live Inference & Latency Profile — Analysis & Notes

**Script**: `scripts/run_live_gemini_inference.py`  
**Raw Command Output**: [`docs/evidence/gemini_live_run.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/gemini_live_run.txt)  
**Date**: 2026-10-31  

---

## 1. Measured Latency & Status

- **Configured Model**: `gemini-3-flash-preview` (configurable via `GEMINI_MODEL_NAME` or `LLM_MODEL`)
- **Measured Round-Trip Latency**: **2,790.93 ms**
- **Inference Status**: Google Gemini API returned **HTTP 429 RESOURCE_EXHAUSTED** (daily free-tier quota consumed: 20 req/day per project).
- **Fallback Verification**:
  - `graph/llm.py` safely caught the HTTP 429 exception without crashing the pipeline.
  - Activated deterministic clinical fallback engine (`llmFallback: true`).
  - Emitted disease-specific fallback guidance for Malaria containing oral hydration, mosquito nets, and zero unauthorized scheduled prescription drugs.

---

## 2. Subjective Confidence Word Filter Behavior

- **Implementation Location**: [`graph/llm.py`](file:///d:/Document/Projects/Internship/Arogyamitra/graph/llm.py) lines 382–394 (Output Sanity Check 3).
- **Mechanism**: **In-place regex rewrite** (does **NOT** engage fallback).
  - Banned terms: `["very high", "high certainty", "certainty", "certain", "definitive", "guaranteed"]`
  - Replacement: `"model estimate"`
  - `llmFallback` remains `False` if the JSON structure is valid.
  - Verified by [`scripts/test_confidence_word_filter.py`](file:///d:/Document/Projects/Internship/Arogyamitra/scripts/test_confidence_word_filter.py):
    - **Input**: `"The model indicates a very high probability (88.5%) of Malaria. There is high certainty that the patient requires immediate intervention with definitive diagnosis."`
    - **Output**: `"The model indicates a model estimate probability (88.5%) of Malaria. There is model estimate that the patient requires immediate intervention with model estimate diagnosis."`

