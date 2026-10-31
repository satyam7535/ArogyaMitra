import os
import sys
import time
import json
from pathlib import Path

# Add graph directory to path
graph_dir = str(Path(__file__).resolve().parent.parent / "graph")
if graph_dir not in sys.path:
    sys.path.insert(0, graph_dir)

from dotenv import load_dotenv
load_dotenv(Path(graph_dir) / ".env")
load_dotenv(".env")

# Ensure LLM is enabled for this verification measurement
os.environ["LLM_ENABLED"] = "true"

from llm import call_llm, LLM_MODEL

def main():
    payload = {
        "primaryDiagnosis": "Malaria",
        "confidenceScore": 0.885,
        "severityScore": 3.2,
        "matchedSymptoms": [
            "chills",
            "vomiting",
            "high_fever",
            "sweating",
            "headache"
        ],
        "precautions": [
            "Drink boiled water",
            "Use mosquito bed nets",
            "Rest"
        ]
    }

    t0 = time.perf_counter()
    conclusion = call_llm(payload, language="en")
    elapsed_ms = (time.perf_counter() - t0) * 1000

    output = {
        "model": LLM_MODEL,
        "latencyMs": round(elapsed_ms, 2),
        "llmFallback": conclusion.llmFallback,
        "diagnosis_summary": conclusion.diagnosis_summary,
        "confidence_interpretation": conclusion.confidence_interpretation,
        "severity_assessment": conclusion.severity_assessment,
        "key_contributing_factors": conclusion.key_contributing_factors,
        "recommended_next_steps": conclusion.recommended_next_steps,
        "referral_recommendation": conclusion.referral_recommendation
    }

    raw_text = json.dumps(output, indent=2)
    print(raw_text)

    # Write pure command output to evidence file
    evidence_path = Path("docs/evidence/gemini_live_run.txt")
    with open(evidence_path, "w", encoding="utf-8") as f:
        f.write(raw_text + "\n")

if __name__ == "__main__":
    main()
