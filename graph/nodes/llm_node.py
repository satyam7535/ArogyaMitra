from llm import call_llm


def llm_node(state):
    xai_data = state["xai_output"]
    req = state.get("request")
    language = getattr(req, "language", "en") if req else "en"

    structured_summary = call_llm(xai_data, language=language)

    return {
        "llm_summary": structured_summary
    }