"""
ArogyaMitra – LangGraph Pipeline HTTP Server
Run: python server.py
Listens on: http://localhost:8001

Endpoints:
  POST /analyze      → runs full pipeline, returns PDF bytes
  POST /analyze/json → runs full pipeline, returns JSON (ML + LLM results)
"""

import sys
import os
import io
import base64

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from graph import graph, PredictRequest

# ── Override ML_BASE_URL to use deployed HF Spaces endpoint ──────────────────
# The xai_node calls run_prediction() which is loaded from ML_Model/app.py.
# Since ML_Model/app.py loads the model locally (or downloads from HF Hub),
# the graph runs the model in-process — no need for HTTP calls here.
# The deployed HF Spaces URL is used only by the frontend for direct JSON queries.

app = FastAPI(title="ArogyaMitra Graph API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    symptoms: List[str]
    patientName: Optional[str] = "Patient"
    patientAge: Optional[int] = None
    patientGender: Optional[str] = None
    workerName: Optional[str] = "Healthcare Worker"
    location: Optional[str] = ""
    language: Optional[str] = "en"


@app.get("/")
def root():
    return {"message": "ArogyaMitra Graph API", "status": "running"}


@app.get("/health")
def health():
    return {"status": "healthy", "service": "graph"}


@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    """
    Runs the full LangGraph pipeline (ML → LLM → PDF).
    Returns the generated PDF as a downloadable binary response.
    """
    if not req.symptoms:
        raise HTTPException(status_code=400, detail="At least one symptom is required")

    predict_request = PredictRequest(
        symptoms=req.symptoms,
        patientName=req.patientName,
        patientAge=req.patientAge,
        patientGender=req.patientGender,
        workerName=req.workerName,
        location=req.location,
        language=req.language,
    )

    try:
        result = graph.invoke({"request": predict_request})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {str(e)}")

    pdf_bytes = result["pdf_bytes"]
    filename  = result["filename"]

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "X-Report-Filename": filename,
        },
    )


@app.post("/analyze/json")
def analyze_json(req: AnalyzeRequest):
    """
    Runs the full LangGraph pipeline (ML → LLM → PDF).
    Returns JSON with ML results, LLM summary, and base64-encoded PDF.
    The frontend can use the JSON to display results AND get the PDF.
    """
    if not req.symptoms:
        raise HTTPException(status_code=400, detail="At least one symptom is required")

    predict_request = PredictRequest(
        symptoms=req.symptoms,
        patientName=req.patientName,
        patientAge=req.patientAge,
        patientGender=req.patientGender,
        workerName=req.workerName,
        location=req.location,
        language=req.language,
    )

    try:
        result = graph.invoke({"request": predict_request})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {str(e)}")

    xai_output  = result.get("xai_output", {})
    llm_summary = result.get("llm_summary")
    pdf_bytes   = result["pdf_bytes"]
    filename    = result["filename"]

    return JSONResponse({
        "mlResult": {
            "disease":          xai_output.get("primaryDiagnosis"),
            "confidence":       xai_output.get("confidenceScore", 0) / 100,
            "severityScore":    xai_output.get("severityScore"),
            "topPredictions":   xai_output.get("topPredictions", []),
            "matchedSymptoms":  xai_output.get("matchedSymptoms", []),
            "precautions":      xai_output.get("precautions", []),
            "description":      xai_output.get("description", ""),
            "limeExplanation":  xai_output.get("limeExplanation", []),
        },
        "llmResult": llm_summary.model_dump() if llm_summary else {},
        "pdfBase64": base64.b64encode(pdf_bytes).decode("utf-8"),
        "filename":  filename,
    })


if __name__ == "__main__":
    import uvicorn
    # Use PORT environment variable if available (for HF Spaces), otherwise default to 8001 for local
    port = int(os.environ.get("PORT", 7860 if "SPACE_ID" in os.environ else 8001))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False)
