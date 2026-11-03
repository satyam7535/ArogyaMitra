from typing import Any, TypedDict

from langgraph.graph import END, StateGraph
from llm import LLMConclusion
from nodes.llm_node import llm_node
from nodes.report_node import report_node
from nodes.xai_node import xai_node
from pydantic import BaseModel


class PredictRequest(BaseModel):
    symptoms: list[str]
    patientName: str | None = "Patient"
    patientAge: int | None = None
    patientGender: str | None = None
    workerName: str | None = "Healthcare Worker"
    location: str | None = ""
    language: str | None = "en"


class HealthcareState(TypedDict):
    request: PredictRequest
    xai_output: dict[str, Any]
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

