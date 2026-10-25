"""
ArogyaMitra – LangGraph Pipeline Microservice
Listens on: http://localhost:8001

Endpoints:
  GET  /health       → health check
  POST /analyze      → runs full pipeline, returns binary PDF
  POST /analyze/json → runs full pipeline, returns JSON (ML + LLM results + PDF base64)
"""

import sys
import os
import io
import base64
import logging
from typing import List, Optional
import jwt
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

from fastapi import FastAPI, HTTPException, Header, Depends, status
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from graph import graph, PredictRequest

logger = logging.getLogger("arogyamitra.graph_server")
logging.basicConfig(level=logging.INFO)

INTERNAL_SERVICE_SECRET = os.getenv("INTERNAL_SERVICE_SECRET", "arogyamitra_internal_service_token_secret_key_32chars!")
REQUIRE_AUTH = os.getenv("REQUIRE_INTERNAL_AUTH", "true").lower() in ("true", "1", "yes")

app = FastAPI(title="ArogyaMitra Graph API", version="1.1.0")

# Restrict CORS to backend and localhost origins
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5000,http://127.0.0.1:5000,http://localhost:5173,http://localhost:8501").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


def verify_service_token(
    x_internal_service_token: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None),
) -> dict:
    """
    Validates internal service tokens issued by the Node.js backend
    to prevent unauthorized external or client-side calls to the pipeline.
    """
    if not REQUIRE_AUTH:
        return {"service": "unauthenticated-dev"}

    token = x_internal_service_token if isinstance(x_internal_service_token, str) else None
    if not token and isinstance(authorization, str):
        parts = authorization.split(" ")
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing internal service authentication token.",
        )

    try:
        payload = jwt.decode(token, INTERNAL_SERVICE_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Internal service token has expired.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Invalid service token: {str(e)}",
        )


class AnalyzeRequest(BaseModel):
    symptoms: List[str] = Field(..., min_length=1, description="List of symptoms reported by patient")
    patientName: Optional[str] = "Patient"
    patientAge: Optional[int] = None
    patientGender: Optional[str] = None
    workerName: Optional[str] = "Healthcare Worker"
    location: Optional[str] = ""
    language: Optional[str] = "en"


@app.get("/")
def root():
    return {"message": "ArogyaMitra Graph Microservice", "status": "running", "version": "1.1.0"}


@app.get("/health")
def health():
    return {"status": "healthy", "service": "graph", "llmReady": True}


@app.post("/analyze")
def analyze(req: AnalyzeRequest, auth: dict = Depends(verify_service_token)):
    """
    Runs full LangGraph pipeline (ML inference → Safe LLM → Multilingual PDF).
    Returns PDF bytes as a streaming response.
    """
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
        logger.error(f"Pipeline error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {str(e)}")

    pdf_bytes = result["pdf_bytes"]
    filename = result["filename"]

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "X-Report-Filename": filename,
        },
    )


@app.post("/analyze/json")
def analyze_json(req: AnalyzeRequest, auth: dict = Depends(verify_service_token)):
    """
    Runs the full LangGraph pipeline (ML → LLM → PDF).
    Returns structured JSON with ML results, safe LLM summary, and base64-encoded PDF.
    """
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
        logger.error(f"Pipeline error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {str(e)}")

    xai_output = result.get("xai_output", {})
    llm_summary = result.get("llm_summary")
    pdf_bytes = result.get("pdf_bytes", b"")
    filename = result.get("filename", "report.pdf")

    # Adapt output fields cleanly
    confidence_val = xai_output.get("confidenceScore", 0)
    if confidence_val > 1.0:
        confidence_val = confidence_val / 100.0

    return JSONResponse({
        "mlResult": {
            "disease": xai_output.get("primaryDiagnosis") or xai_output.get("disease"),
            "confidence": round(float(confidence_val), 4),
            "severityScore": xai_output.get("severityScore"),
            "topPredictions": xai_output.get("topPredictions", []),
            "matchedSymptoms": xai_output.get("matchedSymptoms", []),
            "precautions": xai_output.get("precautions", []),
            "description": xai_output.get("description", ""),
            "shapExplanation": xai_output.get("shapExplanation") or xai_output.get("limeExplanation", []),
            "needsEscalation": xai_output.get("needsEscalation", False),
            "uncertaintyReason": xai_output.get("uncertaintyReason"),
        },
        "llmResult": llm_summary.model_dump() if hasattr(llm_summary, "model_dump") else (llm_summary.dict() if hasattr(llm_summary, "dict") else {}),
        "pdfBase64": base64.b64encode(pdf_bytes).decode("utf-8"),
        "filename": filename,
    })


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False)
