"""
Test LLM Time Limits, Wall-Clock Timeout, Forced 429 Cascade, and Hard Cap
Exercises real TCP sockets, HTTP headers, OpenAI client with max_retries=0,
and wall-clock execution measurement.
"""

import http.server
import json
import os
import sys
import threading
import time
from typing import Any
from openai import OpenAI

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "graph"))

from llm import call_llm, LLMConclusion


class FakeOpenAIServer(http.server.HTTPServer):
    def __init__(self, mode="sleep_15s", sleep_sec=15.0):
        super().__init__(("127.0.0.1", 0), FakeOpenAIHandler)
        self.mode = mode
        self.sleep_sec = sleep_sec
        self.request_count = 0
        self.request_bodies = []


class FakeOpenAIHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_POST(self):
        server: FakeOpenAIServer = self.server
        server.request_count += 1
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        server.request_bodies.append(body)

        if server.mode == "sleep_15s":
            time.sleep(server.sleep_sec)
            self._send_valid_json()
        elif server.mode == "429_then_slow":
            if server.request_count == 1:
                self.send_response(429)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "error": {
                        "message": "Resource has been exhausted (quota exceeded).",
                        "type": "insufficient_quota",
                        "code": 429
                    }
                }).encode("utf-8"))
            else:
                time.sleep(server.sleep_sec)
                self._send_valid_json()
        elif server.mode == "banned_phrase_then_slow":
            if server.request_count == 1:
                banned_json = {
                    "diagnosis_summary": "Malaria diagnosed with high certainty based on chills and fever.",
                    "confidence_interpretation": "high certainty",
                    "severity_assessment": "Moderate severity.",
                    "key_contributing_factors": "Chills, vomiting, fever.",
                    "recommended_next_steps": "Rest and oral hydration.",
                    "referral_recommendation": "Refer to nearest PHC."
                }
                self._send_custom_json(banned_json)
            else:
                time.sleep(server.sleep_sec)
                self._send_valid_json()
        else:
            self._send_valid_json()

    def _send_valid_json(self):
        valid_json = {
            "diagnosis_summary": "Malaria model estimate based on fever and chills.",
            "confidence_interpretation": "Statistical model estimate.",
            "severity_assessment": "Moderate severity.",
            "key_contributing_factors": "Fever, chills.",
            "recommended_next_steps": "Rest and oral hydration.",
            "referral_recommendation": "Refer to nearest PHC."
        }
        self._send_custom_json(valid_json)

    def _send_custom_json(self, data_dict):
        openai_resp = {
            "id": "chatcmpl-test",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": "fake-gemini",
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": json.dumps(data_dict)
                },
                "finish_reason": "stop"
            }]
        }
        resp_bytes = json.dumps(openai_resp).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(resp_bytes)))
        self.end_headers()
        self.wfile.write(resp_bytes)


def run_server_in_thread(server: FakeOpenAIServer):
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return t


def test_scenario_1_server_sleeps_15s():
    print("=" * 70)
    print("SCENARIO 1: Fake Server Sleeps 15s (Wall-Clock Timeout & Hard Cap)")
    print("=" * 70)

    # Use 10s per-attempt timeout and 20s total cap
    os.environ["LLM_PER_ATTEMPT_TIMEOUT"] = "10.0"
    os.environ["LLM_TOTAL_TIMEOUT_CAP"] = "20.0"
    os.environ["LLM_MODELS"] = "gemini-3-flash-preview,gemini-3.5-flash,gemini-2.5-flash"

    server = FakeOpenAIServer(mode="sleep_15s", sleep_sec=15.0)
    port = server.server_address[1]
    run_server_in_thread(server)

    client = OpenAI(
        api_key="fake-test-key",
        base_url=f"http://127.0.0.1:{port}/v1",
        max_retries=0,
    )

    sample_xai = {
        "primaryDiagnosis": "Malaria",
        "confidenceScore": 88.5,
        "severityScore": 3.4,
        "matchedSymptoms": ["chills", "vomiting", "high_fever", "sweating", "headache"],
        "precautions": ["consult doctor immediately"],
        "description": "Malaria is a mosquito-borne disease."
    }

    t0 = time.time()
    result = call_llm(sample_xai, language="en", client=client)
    elapsed = time.time() - t0

    server.shutdown()
    server.server_close()

    print(f"Server received requests: {server.request_count}")
    print(f"Measured Total Seconds:  {elapsed:.3f} s")
    print(f"Result Type:             {type(result).__name__}")
    print(f"llmFallback:             {result.llmFallback}")
    print(f"Diagnosis Summary:       {result.diagnosis_summary[:70]}...")

    assert result.llmFallback is True, "Must engage fallback when server sleeps 15s"
    assert "Malaria" in result.diagnosis_summary
    # Wall clock must be bounded around the 20s cap (+ headroom for thread join/shutdown)
    assert 19.5 <= elapsed <= 23.0, f"Expected ~20s wall-clock duration, got {elapsed:.2f}s"
    print(f"[+] PASS: Scenario 1 verified in {elapsed:.3f}s (wall-clock ~20s, fallback engaged)")
    return elapsed


def test_scenario_2_server_429_then_slow():
    print("\n" + "=" * 70)
    print("SCENARIO 2: Fake Server Returns 429 Immediately, Then Slow")
    print("=" * 70)

    os.environ["LLM_PER_ATTEMPT_TIMEOUT"] = "10.0"
    os.environ["LLM_TOTAL_TIMEOUT_CAP"] = "20.0"
    os.environ["LLM_MODELS"] = "gemini-3-flash-preview,gemini-3.5-flash,gemini-2.5-flash"

    server = FakeOpenAIServer(mode="429_then_slow", sleep_sec=15.0)
    port = server.server_address[1]
    run_server_in_thread(server)

    client = OpenAI(
        api_key="fake-test-key",
        base_url=f"http://127.0.0.1:{port}/v1",
        max_retries=0,
    )

    sample_xai = {
        "primaryDiagnosis": "Malaria",
        "confidenceScore": 88.5,
        "severityScore": 3.4,
        "matchedSymptoms": ["chills", "vomiting", "high_fever", "sweating", "headache"],
        "precautions": ["consult doctor immediately"],
        "description": "Malaria is a mosquito-borne disease."
    }

    t0 = time.time()
    result = call_llm(sample_xai, language="en", client=client)
    elapsed = time.time() - t0

    server.shutdown()
    server.server_close()

    print(f"Server received requests: {server.request_count}")
    print(f"Measured Total Seconds:  {elapsed:.3f} s")
    print(f"llmFallback:             {result.llmFallback}")
    print(f"Diagnosis Summary:       {result.diagnosis_summary[:70]}...")

    assert result.llmFallback is True
    assert "Malaria" in result.diagnosis_summary
    assert 19.5 <= elapsed <= 23.0, f"Expected ~20s wall-clock duration, got {elapsed:.2f}s"
    print(f"[+] PASS: Scenario 2 verified in {elapsed:.3f}s (caught 429, cascaded to slow, capped at ~20s)")
    return elapsed


def test_scenario_3_regenerate_step_with_slow_server():
    print("\n" + "=" * 70)
    print("SCENARIO 3: Banned Confidence Phrase Triggering Regeneration, Then Slow")
    print("=" * 70)

    os.environ["LLM_PER_ATTEMPT_TIMEOUT"] = "10.0"
    os.environ["LLM_TOTAL_TIMEOUT_CAP"] = "20.0"
    os.environ["LLM_MODELS"] = "gemini-3.5-flash"

    server = FakeOpenAIServer(mode="banned_phrase_then_slow", sleep_sec=15.0)
    port = server.server_address[1]
    run_server_in_thread(server)

    client = OpenAI(
        api_key="fake-test-key",
        base_url=f"http://127.0.0.1:{port}/v1",
        max_retries=0,
    )

    sample_xai = {
        "primaryDiagnosis": "Malaria",
        "confidenceScore": 88.5,
        "severityScore": 3.4,
        "matchedSymptoms": ["chills", "vomiting", "high_fever", "sweating", "headache"],
        "precautions": ["consult doctor immediately"],
        "description": "Malaria is a mosquito-borne disease."
    }

    t0 = time.time()
    result = call_llm(sample_xai, language="en", client=client)
    elapsed = time.time() - t0

    server.shutdown()
    server.server_close()

    print(f"Server received requests: {server.request_count} (Request 1: banned phrase, Request 2: regenerate)")
    print(f"Measured Total Seconds:  {elapsed:.3f} s")
    print(f"llmFallback:             {result.llmFallback}")

    assert result.llmFallback is True
    assert "high certainty" not in result.diagnosis_summary.lower()
    # Regeneration request timed out at 10s per-attempt; total ~10s
    assert 9.5 <= elapsed <= 21.0, f"Expected ~10-20s duration, got {elapsed:.2f}s"
    print(f"[+] PASS: Scenario 3 verified in {elapsed:.3f}s (regenerate attempt timed out safely, fallback engaged)")
    return elapsed


def test_scenario_4_client_max_retries_zero():
    print("\n" + "=" * 70)
    print("SCENARIO 4: Confirm OpenAI Client max_retries=0 Is Enforced")
    print("=" * 70)

    client = OpenAI(api_key="fake", base_url="http://127.0.0.1:9/v1", max_retries=0)
    assert client.max_retries == 0, "max_retries must be explicitly 0 to prevent hidden retries outside budget"
    print(f"[+] PASS: OpenAI client max_retries confirmed: {client.max_retries}")


if __name__ == "__main__":
    t1 = test_scenario_1_server_sleeps_15s()
    t2 = test_scenario_2_server_429_then_slow()
    t3 = test_scenario_3_regenerate_step_with_slow_server()
    test_scenario_4_client_max_retries_zero()
    print("\n======================================================================")
    print("ALL 4 LLM TIMEOUT & WALL-CLOCK DEADLINE SCENARIOS PASSED")
    print(f"Measured Durations: Scenario 1 = {t1:.2f}s, Scenario 2 = {t2:.2f}s, Scenario 3 = {t3:.2f}s")
    print("======================================================================")
