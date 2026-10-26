"""
ArogyaMitra – LangGraph Pipeline CLI
Usage:
    python main.py --symptoms "fever,cough,chest pain" --name "Ravi Kumar" --age 45 --gender Male --worker "Anita" --location "Village PHC"

The generated PDF is saved in the current directory.
"""

import argparse
import os
import sys

# Add parent directory to path so we can import ML_Model
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graph import PredictRequest, graph


def main():
    parser = argparse.ArgumentParser(description="Run ArogyaMitra LangGraph analysis pipeline")
    parser.add_argument("--symptoms",  required=True, help="Comma-separated list of symptoms")
    parser.add_argument("--name",      default="Patient",           help="Patient name")
    parser.add_argument("--age",       type=int, default=None,      help="Patient age")
    parser.add_argument("--gender",    default=None,                help="Patient gender")
    parser.add_argument("--worker",    default="Healthcare Worker",  help="Worker name")
    parser.add_argument("--location",  default="",                  help="Location / PHC name")
    parser.add_argument("--output",    default=None,                help="Output PDF filename (optional)")

    args = parser.parse_args()

    symptoms = [s.strip() for s in args.symptoms.split(",") if s.strip()]

    predict_request = PredictRequest(
        symptoms=symptoms,
        patientName=args.name,
        patientAge=args.age,
        patientGender=args.gender,
        workerName=args.worker,
        location=args.location,
    )

    print(f"Running analysis for {args.name} with symptoms: {symptoms}")

    initial_state = {"request": predict_request}
    result = graph.invoke(initial_state)

    pdf_bytes = result["pdf_bytes"]
    filename  = args.output or result["filename"]

    with open(filename, "wb") as f:
        f.write(pdf_bytes)

    print(f"✅ PDF saved: {filename}")


if __name__ == "__main__":
    main()