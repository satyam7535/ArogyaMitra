from utils.pdf_generator import generate_pdf
from datetime import datetime

def report_node(state):
    xai_data = state["xai_output"]
    llm_summary = state["llm_summary"]
    language = state["request"].language or "en"

    combined_data = {
        **xai_data,
        "llmConclusion": llm_summary.model_dump()
    }

    pdf_bytes = generate_pdf(combined_data, language=language)

    filename = (
        f"ArogyaMitra_Report_"
        f"{xai_data['patientName'].replace(' ','_')}_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    )

    return {
        "pdf_bytes": pdf_bytes,
        "filename": filename
    }