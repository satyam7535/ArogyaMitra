from langgraph.graph import StateGraph, END
from typing import TypedDict, Dict, Any, Optional, List
from pydantic import BaseModel
from nodes.xai_node import xai_node
from nodes.llm_node import llm_node
from nodes.report_node import report_node
from llm import LLMConclusion       
class PredictRequest(BaseModel):
    symptoms: List[str]
    patientName: Optional[str] = "Patient"
    patientAge: Optional[int] = None
    patientGender: Optional[str] = None
    workerName: Optional[str] = "Healthcare Worker"
    location: Optional[str] = ""
    language: Optional[str] = "en"


class HealthcareState(TypedDict):
    request: PredictRequest
    xai_output: Dict[str, Any]
    llm_summary: LLMConclusion
    final_report: str
    pdf_bytes: bytes
    filename: str


builder = StateGraph(HealthcareState)

builder.add_node("xai_node", xai_node)
builder.add_node("llm_node", llm_node)
builder.add_node("report_node", report_node)

builder.set_entry_point("xai_node")

builder.add_edge("xai_node", "llm_node")
builder.add_edge("llm_node", "report_node")
builder.add_edge("report_node", END)

graph = builder.compile()

