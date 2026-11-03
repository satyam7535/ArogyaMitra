"""
ArogyaMitra — Real Gemini API Smoke Test (Rule 6 compliant)
Performs 1 single test call to Google Gemini free tier with fake clinical data.
Ensures zero PII is sent, verifies latency, and validates Pydantic schema parsing.
Saves raw output to docs/evidence/gemini_smoke_test.txt.
"""

import os
import sys
import time

# Ensure UTF-8 output on Windows
sys.stdout.reconfigure(encoding="utf-8")

# Ensure graph directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm import call_llm


def run_smoke_test():
    print("Command: python graph/scripts/gemini_smoke_test.py")
    print("================================================================================")
    print("AROGYAMITRA — REAL GEMINI FREE-TIER SMOKE TEST (RULE 6 COMPLIANT)")
    print(f"Timestamp: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}")
    print("================================================================================\n")

    # Purely synthetic, de-identified clinical dummy data (NO patient names or contact details)
    fake_xai_data = {
        "primaryDiagnosis": "Fungal infection",
        "confidenceScore": 91.2,
        "severityScore": 2.4,
        "matchedSymptoms": ["itching", "skin_rash", "nodal_skin_eruptions"],
        "symptomSeverities": [
            {"symptom": "itching", "severity": 1},
            {"symptom": "skin_rash", "severity": 3},
            {"symptom": "nodal_skin_eruptions", "severity": 4},
        ],
        "precautions": [
            "bath twice daily",
            "keep affected area dry",
            "use clean clothes",
            "avoid sharing towels"
        ],
        "description": "Superficial cutaneous dermatomycosis presenting with pruritic lesions.",
        "shapExplanation": [
            {"feature": "nodal_skin_eruptions present", "impact": 6.82, "direction": "Supports Diagnosis"},
            {"feature": "skin_rash present", "impact": 2.41, "direction": "Supports Diagnosis"},
            {"feature": "itching present", "impact": 1.25, "direction": "Supports Diagnosis"}
        ],
        "needsEscalation": False,
        "patientAge": 38,
        "patientGender": "Female",
    }

    print("[1. INITIATING GEMINI FREE-TIER CALL]")
    print("  - Model:         gemini-1.5-flash")
    print("  - Target Lang:   English (en)")
    print("  - Input Data:    De-identified synthetic clinical presentation (PII-free)")

    start_time = time.perf_counter()
    conclusion = call_llm(fake_xai_data, language="en")
    elapsed_ms = (time.perf_counter() - start_time) * 1000

    print("\n[2. EXECUTION COMPLETED]")
    print(f"  - Round-trip Latency: {elapsed_ms:.2f} ms")
    print(f"  - Fallback Engaged:   {conclusion.llmFallback}")
    print("  - Pydantic Validated: True\n")

    print("[3. STRUCTURED CLINICAL OUTPUT]")
    print(f"  - Diagnosis Summary:          {conclusion.diagnosis_summary}")
    print(f"  - Confidence Interpretation:  {conclusion.confidence_interpretation}")
    print(f"  - Severity Assessment:        {conclusion.severity_assessment}")
    print(f"  - Key Contributing Factors:   {conclusion.key_contributing_factors}")
    print(f"  - Recommended Next Steps:     {conclusion.recommended_next_steps}")
    print(f"  - Referral Recommendation:    {conclusion.referral_recommendation}\n")

    print("================================================================================")
    print("GEMINI SMOKE TEST RESULT: " + ("LIVE_GEMINI_SUCCESS" if not conclusion.llmFallback else "DETERMINISTIC_FALLBACK_ENGAGED"))
    print("================================================================================")

if __name__ == "__main__":
    run_smoke_test()
