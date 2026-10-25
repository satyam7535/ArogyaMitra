from utils.pdf_generator import generate_pdf
from datetime import datetime

def report_node(state):
    xai_data = state["xai_output"]
    llm_summary = state["llm_summary"]
    req = state.get("request")
    language = getattr(req, "language", "en") if req else "en"

    patient_name = (
        getattr(req, "patientName", None)
        or xai_data.get("patientName")
        or "Patient"
    )

    combined_data = {
        **xai_data,
        "patientName": patient_name,
        "workerName": getattr(req, "workerName", "Healthcare Worker") if req else xai_data.get("workerName", "Healthcare Worker"),
        "location": getattr(req, "location", "") if req else xai_data.get("location", ""),
        "llmConclusion": llm_summary.model_dump() if hasattr(llm_summary, "model_dump") else (llm_summary.dict() if hasattr(llm_summary, "dict") else llm_summary)
    }

    pdf_bytes = generate_pdf(combined_data, language=language)

    filename = (
        f"ArogyaMitra_Report_"
        f"{patient_name.replace(' ','_')}_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    )

    return {
        "pdf_bytes": pdf_bytes,
        "filename": filename
    }