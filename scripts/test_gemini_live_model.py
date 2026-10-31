import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv("graph/.env")
key = os.getenv("LLM_API_KEY") or os.getenv("GOOGLE_API_KEY")
if not key:
    load_dotenv(".env")
    key = os.getenv("LLM_API_KEY") or os.getenv("GOOGLE_API_KEY")

client = OpenAI(
    api_key=key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

test_models = ["gemini-2.5-flash", "gemini-flash-latest", "models/gemini-2.5-flash"]
success_model = None

for model in test_models:
    try:
        res = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": 'Respond with JSON {"status": "ok"}'}],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        print(f"Model '{model}' SUCCESS: {res.choices[0].message.content.strip()}")
        success_model = model
        break
    except Exception as e:
        print(f"Model '{model}' failed: {e}")

if success_model:
    print(f"\nSELECTED MODEL: {success_model}")

