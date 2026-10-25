from llm import call_llm
import json

def llm_node(state):
    xai_data = state["xai_output"]
    language = state["request"].language or "en"

    lang_map = {
        "en": "English",
        "hi": "Hindi",
        "mr": "Marathi"
    }
    target_lang = lang_map.get(language, "English")

    prompt = f"""
    Below is structured output from a trained Explainable AI model.

    Rules:
    - Do NOT modify predicted disease.
    - Do NOT introduce new diagnoses.
    - Use only the provided data.
    - IMPORTANT: The 'conclusion', 'patientAdvice', and 'recommendations' MUST be in {target_lang}.

    XAI Output:
    {json.dumps(xai_data, indent=2)}
    """

    structured_summary = call_llm(prompt)

    return {
        "llm_summary": structured_summary
    }