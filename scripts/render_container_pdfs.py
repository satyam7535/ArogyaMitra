import os
import pypdfium2 as pdfium
from utils.pdf_generator import generate_pdf

sample_report_data = {
    "patientName": "Sunita Patil",
    "patientAge": 38,
    "patientGender": "Female",
    "workerName": "Asha Worker Rekha",
    "location": "Shirur Primary Health Centre, Pune",
    "primaryDiagnosis": "Fungal infection",
    "confidenceScore": 88.5,
    "severityScore": 3.4,
    "differentialDiagnoses": [
        {"disease": "Fungal infection", "probability": 0.885},
        {"disease": "Allergy", "probability": 0.082},
        {"disease": "GERD", "probability": 0.033},
    ],
    "matchedSymptoms": ["itching", "skin_rash", "nodal_skin_eruptions"],
    "severityDetails": [
        {"symptom": "itching", "weight": 1, "level": "Low"},
        {"symptom": "skin_rash", "weight": 3, "level": "Moderate"},
        {"symptom": "nodal_skin_eruptions", "weight": 4, "level": "Moderate"},
    ],
    "precautions": [
        "bath twice",
        "use dettol or neem in bathing water",
        "keep area dry and clean",
        "use clean cloths",
    ],
    "description": "Fungal infection is a common skin disease caused by fungi affecting superficial layers.",
    "redFlag": False,
    "risk": "Low",
    "symptomContributions": [
        {"feature": "itching present", "impact": 2.14, "direction": "Supports Diagnosis"},
        {"feature": "skin_rash present", "impact": 1.82, "direction": "Supports Diagnosis"},
        {"feature": "nodal_skin_eruptions present", "impact": 1.45, "direction": "Supports Diagnosis"},
    ],
    "llmConclusion": {
        "diagnosis_summary": "Classic presentation of superficial fungal dermatosis.",
        "confidence_interpretation": "High Bayesian certainty based on characteristic triad.",
        "severity_assessment": "Mild dermatological presentation, non-emergency.",
        "key_contributing_factors": "Itching, rash, and nodal lesions.",
        "recommended_next_steps": "Apply topical antifungal cream and observe hygiene precautions.",
        "referral_recommendation": "Routine PHC outpatient follow-up in 10 days.",
        "llmFallback": False,
    },
}

out_dir = "/app/output"
os.makedirs(out_dir, exist_ok=True)

for lang in ["hi", "mr"]:
    pdf_bytes = generate_pdf(sample_report_data, language=lang)
    assert pdf_bytes.startswith(b"%PDF-"), f"Invalid PDF bytes for {lang}"
    
    pdf_path = os.path.join(out_dir, f"report_{lang}.pdf")
    with open(pdf_path, "wb") as f:
        f.write(pdf_bytes)
    
    # Rasterize page 1 to PNG via pypdfium2 inside the container
    doc = pdfium.PdfDocument(pdf_bytes)
    page = doc[0]
    pixmap = page.render(scale=2.0)
    img = pixmap.to_pil()
    png_path = os.path.join(out_dir, f"report_{lang}_p1.png")
    img.save(png_path)
    print(f"[CONTAINER] Rendered {lang.upper()} PDF ({len(pdf_bytes)} bytes) -> {pdf_path} & {png_path}")

print("[CONTAINER] PDF and PNG generation inside arogya-graph complete.")
