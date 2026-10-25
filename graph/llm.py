import os
import json
import re
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

# LLM Provider Configuration (Google Gemini via OpenAI-compatible endpoint)
LLM_API_KEY = os.getenv("LLM_API_KEY") or os.getenv("GOOGLE_API_KEY") or os.getenv("OPENAI_API_KEY")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/")
LLM_MODEL = os.getenv("LLM_MODEL") or os.getenv("MODEL_NAME", "gemini-1.5-flash")

client = OpenAI(
    api_key=LLM_API_KEY or "missing-key",
    base_url=LLM_BASE_URL,
)

class LLMConclusion(BaseModel):
    diagnosis_summary: str
    confidence_interpretation: str
    severity_assessment: str
    key_contributing_factors: str
    recommended_next_steps: str
    referral_recommendation: str


def call_llm(prompt: str) -> LLMConclusion:
    few_shot_example = {
        "diagnosis_summary": "The patient exhibits classic signs of Jaundice, supported by a 42.5% confidence score from the ML model.",
        "confidence_interpretation": "Moderate confidence. While Jaundice is the leading prediction, other related conditions should be excluded.",
        "severity_assessment": "Moderate (Severity Score: 2.67). Requires monitoring and further diagnostic tests.",
        "key_contributing_factors": "High bilirubin levels, physical symptoms (Jaundice), and patient history.",
        "recommended_next_steps": "Blood count, liver function tests, and ultrasound of the abdomen.",
        "referral_recommendation": "Gastroenterologist for specialized review."
    }

    system_content = (
        "You are a clinical decision-support assistant. "
        "You MUST return ONLY valid JSON. "
        "Do NOT include any conversational text, headers, or markdown blocks. "
        "Your response must start with '{' and end with '}'.\n\n"
        "Strict Schema:\n"
        "{\n"
        "  \"diagnosis_summary\": \"string\",\n"
        "  \"confidence_interpretation\": \"string\",\n"
        "  \"severity_assessment\": \"string\",\n"
        "  \"key_contributing_factors\": \"string\",\n"
        "  \"recommended_next_steps\": \"string\",\n"
        "  \"referral_recommendation\": \"string\"\n"
        "}\n\n"
        f"Example Correct Output:\n{json.dumps(few_shot_example, indent=2)}\n\n"
        "Important: Return the raw JSON string starting with { and ending with }."
    )

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": f"Analyze this data and return only JSON matching the schema:\n\n{prompt}"}
        ],
        temperature=0.1,
    )

    response_content = response.choices[0].message.content.strip()

    # robustly extract JSON if the LLM added text around it
    try:
        # Search for the first { and last }
        match = re.search(r"(\{.*\})", response_content, re.DOTALL)
        if match:
            json_str = match.group(1)
        else:
            raise ValueError("The AI did not provide a JSON block.")

        if hasattr(LLMConclusion, "model_validate_json"):
            llm_conclusion = LLMConclusion.model_validate_json(json_str)
        else:
            llm_conclusion = LLMConclusion.parse_raw(json_str)
        return llm_conclusion
    except Exception as e:
        raise ValueError(f"LLM Response Error: {e}. Raw content: {response_content}")