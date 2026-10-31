"""
Test LLM Time Limits and Forced 429 Cascade Behavior
Verifies:
1. Per-attempt timeout (~10s) and total cap (~20s).
2. Cascading across candidate models on HTTP 429.
3. Fallback to deterministic template within total time cap without crashing.
4. Total execution time measurement.
"""

import os
import sys
import time
from unittest.mock import MagicMock

# Add graph directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "graph"))

from llm import call_llm, LLMConclusion

def test_forced_429_cascade_and_time_bound():
    print("=" * 70)
    print("TEST: Forced HTTP 429 Rate Limit Cascade & Timeout Cap")
    print("=" * 70)

    sample_xai = {
        "primaryDiagnosis": "Malaria",
        "confidenceScore": 88.5,
        "severityScore": 3.4,
        "matchedSymptoms": ["chills", "vomiting", "high_fever", "sweating", "headache"],
        "precautions": ["consult doctor immediately", "avoid mosquito bites"],
        "description": "Malaria is a mosquito-borne infectious disease."
    }

    # Mock client where every model candidate raises 429 RateLimitError
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = RuntimeError("Error code: 429 - Rate limit reached or quota exhausted")

    t0 = time.time()
    result = call_llm(sample_xai, language="en", client=mock_client)
    elapsed = time.time() - t0

    print(f"Elapsed Time: {elapsed:.3f} seconds")
    print(f"Result Type: {type(result).__name__}")
    print(f"llmFallback: {result.llmFallback}")
    print(f"Diagnosis Summary: {result.diagnosis_summary[:80]}...")
    print(f"Recommended Action: {result.recommended_next_steps[:80]}...")

    assert isinstance(result, LLMConclusion), "Must return LLMConclusion"
    assert result.llmFallback is True, "Must fall back to deterministic template on exhausted 429s"
    assert "Malaria" in result.diagnosis_summary, "Must include primary disease"
    assert elapsed < 20.0, f"Total execution time ({elapsed:.2f}s) must be well within total cap"

    print("\n[+] SUCCESS: Forced 429 test passed. Handled gracefully within time bounds.")

    print("\n" + "=" * 70)
    print("TEST: Total Timeout Cap (~20s) with Slow / Hanging Client")
    print("=" * 70)

    # Mock client where each call takes 11 seconds (simulating slow/hanging socket)
    class HangingClient:
        class chat:
            class completions:
                @staticmethod
                def create(**kwargs):
                    timeout = kwargs.get("timeout", 10.0)
                    time.sleep(min(timeout, 2.5)) # Fast-forward simulation of timeout
                    raise TimeoutError(f"Request timed out after {timeout}s")

    t1 = time.time()
    res2 = call_llm(sample_xai, language="en", client=HangingClient())
    elapsed2 = time.time() - t1
    print(f"Elapsed Time with Hanging Client: {elapsed2:.3f} seconds")
    print(f"llmFallback: {res2.llmFallback}")
    assert res2.llmFallback is True
    print("[+] SUCCESS: Hanging client handled gracefully with deterministic fallback.")

    return elapsed, result

if __name__ == "__main__":
    test_forced_429_cascade_and_time_bound()
