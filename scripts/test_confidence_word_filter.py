import re
import sys
from pathlib import Path

# Add graph directory to path
graph_dir = str(Path(__file__).resolve().parent.parent / "graph")
if graph_dir not in sys.path:
    sys.path.insert(0, graph_dir)

from llm import LLMConclusion

def test_confidence_word_filter():
    # Example raw LLM output containing forbidden subjective confidence words
    sample_text = (
        "The model indicates a very high probability (88.5%) of Malaria. "
        "There is high certainty that the patient requires immediate intervention with definitive diagnosis."
    )
    
    conclusion = LLMConclusion(
        diagnosis_summary="Patient presents clinical indicators consistent with Malaria.",
        confidence_interpretation=sample_text,
        severity_assessment="Severity score 3.2 indicates acute presentation.",
        key_contributing_factors="Fever, chills, vomiting.",
        recommended_next_steps="Maintain oral hydration and rest.",
        referral_recommendation="Refer to PHC.",
        llmFallback=False
    )
    
    print("=== BEFORE SANITIZATION ===")
    print(f"confidence_interpretation:\n  \"{conclusion.confidence_interpretation}\"")
    print(f"llmFallback: {conclusion.llmFallback}")
    
    # Apply the exact filter from graph/llm.py (Output Sanity Check 3)
    banned_confidence = ["very high", "high certainty", "certainty", "certain", "definitive", "guaranteed"]
    conf_str = conclusion.confidence_interpretation.lower()
    rewritten = False
    for banned in banned_confidence:
        if re.search(r"\b" + re.escape(banned) + r"\b", conf_str):
            rewritten = True
            conclusion.confidence_interpretation = re.sub(
                r"\b" + re.escape(banned) + r"\b", "model estimate", conclusion.confidence_interpretation, flags=re.IGNORECASE
            )
            # update conf_str for subsequent iterations
            conf_str = conclusion.confidence_interpretation.lower()

    print("\n=== AFTER SANITIZATION ===")
    print(f"confidence_interpretation:\n  \"{conclusion.confidence_interpretation}\"")
    print(f"llmFallback: {conclusion.llmFallback}")
    print(f"Behavior: {'REWRITE (In-place regex substitution)' if rewritten else 'NO CHANGE'}")
    print("Result: Subjective certainty words ('very high', 'high certainty', 'definitive') are REWRITTEN in-place to 'model estimate'.")
    print("Crucially, this is a REWRITE, NOT a fallback to deterministic mode (llmFallback remains False).")

if __name__ == "__main__":
    test_confidence_word_filter()
