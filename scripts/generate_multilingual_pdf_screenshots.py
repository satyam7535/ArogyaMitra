import os
import base64
import httpx
import pypdfium2 as pdfium

os.environ["PYTHONHTTPSVERIFY"] = "0"

def generate_multilingual_reports():
    base_url = "https://localhost"
    client = httpx.Client(verify=False, timeout=30.0)

    # Login as worker
    login_res = client.post(f"{base_url}/api/v1/worker/login", json={
        "email": "worker@arogyamitra.gov.in",
        "password": "Worker@Arogya2026!"
    })
    if login_res.status_code != 200:
        raise RuntimeError(f"Worker login failed: {login_res.text}")
    
    token = login_res.json()["accessToken"]
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    languages = [("hi", "hindi"), ("mr", "marathi")]
    out_dir = "docs/evidence/ui_screenshots"
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs("docs/evidence", exist_ok=True)

    for lang_code, lang_name in languages:
        print(f"Generating clinical report for language: {lang_name} ({lang_code})...")
        triage_payload = {
            "symptoms": ["itching", "vomiting", "fatigue", "yellowish_skin"],
            "patientName": f"Rani Deshmukh ({lang_name.title()})",
            "patientAge": 38,
            "patientGender": "Female",
            "location": "Arogya Kendra, Pune",
            "workerName": "Sunita Patil (ASHA Worker)",
            "language": lang_code
        }
        res = client.post(f"{base_url}/api/v1/consultation/triage", json=triage_payload, headers=headers)
        if res.status_code != 200:
            raise RuntimeError(f"Triage request failed for {lang_code}: {res.text}")
        
        data = res.json()
        pdf_b64 = data.get("pdfBase64")
        if not pdf_b64:
            raise RuntimeError(f"Missing pdfBase64 in response for {lang_code}")
        
        pdf_bytes = base64.b64decode(pdf_b64)
        pdf_path = f"docs/evidence/report_{lang_name}.pdf"
        with open(pdf_path, "wb") as f:
            f.write(pdf_bytes)
        print(f"Saved PDF to {pdf_path} ({len(pdf_bytes)} bytes)")

        # Render Page 1 to PNG via pypdfium2
        pdf = pdfium.PdfDocument(pdf_bytes)
        page = pdf.get_page(0)
        image = page.render(scale=2.0).to_pil()
        png_path = os.path.join(out_dir, f"report_page1_{lang_name}.png")
        image.save(png_path)
        print(f"Saved rendered page 1 to {png_path}")

    print("Multilingual report generation complete.")

if __name__ == "__main__":
    generate_multilingual_reports()
