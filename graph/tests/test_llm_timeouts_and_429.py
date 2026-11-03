"""
Pytest integration for LLM Timeouts, Wall-Clock Deadlines, 429 Cascades, and max_retries=0.
Executes against local loopback HTTP fake servers.
"""

import http.server
import json
import os
import sys
import threading
import time

from openai import OpenAI

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from llm import call_llm


class FakeOpenAIServer(http.server.HTTPServer):
    def __init__(self, mode="sleep", sleep_sec=1.5):
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

        if server.mode == "sleep":
            time.sleep(server.sleep_sec)
            self._send_valid_json()
        elif server.mode == "429_then_slow":
            if server.request_count == 1:
                self.send_response(429)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "error": {
                        "message": "Resource exhausted (quota exceeded).",
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
                    "diagnosis_summary": "Malaria diagnosed with high certainty based on chills.",
                    "confidence_interpretation": "high certainty",
                    "severity_assessment": "Moderate severity.",
                    "key_contributing_factors": "Chills, vomiting.",
                    "recommended_next_steps": "Rest and hydration.",
                    "referral_recommendation": "Refer to PHC."
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
        try:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(resp_bytes)))
            self.end_headers()
            self.wfile.write(resp_bytes)
        except Exception:
            pass


def run_server_in_thread(server: FakeOpenAIServer):
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return t


def test_llm_wall_clock_timeout_fake_server_sleep():
    os.environ["LLM_PER_ATTEMPT_TIMEOUT"] = "0.5"
    os.environ["LLM_TOTAL_TIMEOUT_CAP"] = "1.0"
    os.environ["LLM_MODELS"] = "gemini-3-flash-preview,gemini-3.5-flash"

    server = FakeOpenAIServer(mode="sleep", sleep_sec=1.2)
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
        "matchedSymptoms": ["chills", "fever"],
        "precautions": ["consult doctor"],
        "description": "Malaria description."
    }

    t0 = time.time()
    result = call_llm(sample_xai, language="en", client=client)
    elapsed = time.time() - t0

    server.shutdown()
    server.server_close()

    assert result.llmFallback is True
    assert "Malaria" in result.diagnosis_summary
    assert elapsed >= 0.5


def test_llm_429_cascade_then_slow_fake_server():
    os.environ["LLM_PER_ATTEMPT_TIMEOUT"] = "0.5"
    os.environ["LLM_TOTAL_TIMEOUT_CAP"] = "1.0"
    os.environ["LLM_MODELS"] = "gemini-3-flash-preview,gemini-3.5-flash"

    server = FakeOpenAIServer(mode="429_then_slow", sleep_sec=1.5)
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
        "matchedSymptoms": ["chills", "fever"],
        "precautions": ["consult doctor"],
        "description": "Malaria description."
    }

    result = call_llm(sample_xai, language="en", client=client)

    server.shutdown()
    server.server_close()

    assert result.llmFallback is True
    assert server.request_count >= 2


def test_llm_banned_phrase_regeneration_step_slow():
    os.environ["LLM_PER_ATTEMPT_TIMEOUT"] = "0.5"
    os.environ["LLM_TOTAL_TIMEOUT_CAP"] = "1.0"
    os.environ["LLM_MODELS"] = "gemini-3.5-flash"

    server = FakeOpenAIServer(mode="banned_phrase_then_slow", sleep_sec=1.5)
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
        "matchedSymptoms": ["chills", "fever"],
        "precautions": ["consult doctor"],
        "description": "Malaria description."
    }

    result = call_llm(sample_xai, language="en", client=client)

    server.shutdown()
    server.server_close()

    assert result.llmFallback is True
    assert "high certainty" not in result.diagnosis_summary.lower()


def test_llm_client_max_retries_enforced_zero():
    client = OpenAI(api_key="fake", base_url="http://127.0.0.1:9/v1", max_retries=0)
    assert client.max_retries == 0
