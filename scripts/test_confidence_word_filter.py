import sys
from pathlib import Path

# Add graph directory to path
graph_dir = str(Path(__file__).resolve().parent.parent / "graph")
if graph_dir not in sys.path:
    sys.path.insert(0, graph_dir)

from llm import (
    LLMConclusion,
    check_banned_confidence_phrases,
    generate_deterministic_fallback,
    BANNED_CONFIDENCE_PHRASES,
)

def test_confidence_filter():
    print("================================================================================")
    print("VERIFICATION: Confidence Filter Replacement & Non-Garbled Output Test")
    print("================================================================================")
    print(f"Banned Phrases Monitored: {BANNED_CONFIDENCE_PHRASES}\n")

    # Case 1: Legitimate clinical use of the word 'certain' (e.g., 'certain symptoms', 'certain markers')
    # Must NOT be flagged now that standalone 'certain' was dropped in favor of 'certain diagnosis'
    valid_text_with_certain = LLMConclusion(
        diagnosis_summary="Patient exhibits certain clinical indicators consistent with Malaria.",
        confidence_interpretation="Statistical decision-support estimate indicates 88.5% probability.",
        severity_assessment="Severity score 3.2 indicates acute presentation requiring observation.",
        key_contributing_factors="Fever, chills, vomiting.",
        recommended_next_steps="Maintain oral hydration and rest.",
        referral_recommendation="Refer to PHC.",
        llmFallback=False
    )
    flagged_valid = check_banned_confidence_phrases(valid_text_with_certain)
    print("Test 1: Legitimate clinical use of 'certain' (e.g. 'certain clinical indicators'):")
    print(f"  Diagnosis text: \"{valid_text_with_certain.diagnosis_summary}\"")
    print(f"  Flagged: {flagged_valid} (Expected: None)")
    assert flagged_valid is None, f"Should not flag legitimate 'certain': got {flagged_valid}"
    print("  RESULT: PASS - Standalone 'certain' correctly permitted.\n")

    # Case 2: Presence of banned phrase 'very high' across summary fields
    banned_text = LLMConclusion(
        diagnosis_summary="Patient presents clinical indicators consistent with Malaria.",
        confidence_interpretation="The model indicates a very high probability (88.5%) of Malaria.",
        severity_assessment="Severity score 3.2 indicates elevated risk.",
        key_contributing_factors="Fever, chills, vomiting.",
        recommended_next_steps="Maintain oral hydration.",
        referral_recommendation="Refer to PHC.",
        llmFallback=False
    )
    flagged_banned = check_banned_confidence_phrases(banned_text)
    print("Test 2: Detection of banned phrase 'very high':")
    print(f"  Confidence text: \"{banned_text.confidence_interpretation}\"")
    print(f"  Flagged: '{flagged_banned}' (Expected: 'very high')")
    assert flagged_banned == "very high"
    print("  RESULT: PASS - Correctly flagged across summary fields.\n")

    # Case 3: Verify fallback behavior on non-compliant retry
    # When regeneration still contains a banned phrase, the pipeline engages the deterministic fallback
    xai_data = {
        "primaryDiagnosis": "Malaria",
        "confidenceScore": 0.885,
        "severityScore": 3.2,
        "matchedSymptoms": ["chills", "vomiting", "high_fever", "sweating", "headache"],
        "precautions": ["Drink boiled water", "Use mosquito bed nets", "Rest"]
    }
    fallback_output = generate_deterministic_fallback(xai_data, language="en")
    print("Test 3: Non-compliant retry fallback output verification:")
    print(f"  Fallback Engaged: {fallback_output.llmFallback} (Expected: True)")
    print(f"  diagnosis_summary: \"{fallback_output.diagnosis_summary}\"")
    print(f"  confidence_interpretation: \"{fallback_output.confidence_interpretation}\"")
    print(f"  recommended_next_steps: \"{fallback_output.recommended_next_steps}\"")
    
    # Assert NO garbled text exists
    assert "model estimate that the patient requires" not in fallback_output.confidence_interpretation
    assert "model estimate probability" not in fallback_output.confidence_interpretation
    print("  RESULT: PASS - Output is clean, pristine clinical template without any garbled text substitutions.")
    print("================================================================================")

if __name__ == "__main__":
    test_confidence_filter()
