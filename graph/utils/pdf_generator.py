import os
import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ── Translations ─────────────────────────────────────────────────────────────
TRANSLATIONS = {
    "en": {
        "title": "ArogyaMitra",
        "subtitle": "AI-Assisted Disease Prediction Report",
        "date": "Date",
        "worker": "Worker",
        "location": "Location",
        "patient_info": "Patient Information",
        "name": "Name",
        "age": "Age",
        "gender": "Gender",
        "symptoms_reported": "Symptoms Reported",
        "primary_diagnosis": "Primary Diagnosis",
        "condition": "Condition",
        "confidence": "Confidence",
        "severity": "Severity Score",
        "differential_diagnoses": "Differential Diagnoses (Top 3)",
        "disease": "Disease",
        "symptoms_table_title": "Reported Symptoms & Severity",
        "symptom": "Symptom",
        "level": "Level",
        "high": "High",
        "moderate": "Moderate",
        "low": "Low",
        "ai_explanation": "AI Explanation (LIME)",
        "lime_desc": "The following factors most influenced this prediction. Positive impact = supports the diagnosis. Negative impact = evidence against it.",
        "impact_score": "Impact Score",
        "direction": "Direction",
        "supports": "Supports Diagnosis",
        "against": "Against Diagnosis",
        "cdss_summary": "Clinical Decision Support Summary",
        "diag_summary": "Diagnosis Summary",
        "conf_interpretation": "Confidence Interpretation",
        "sev_assessment": "Severity Assessment",
        "next_steps": "Recommended Next Steps",
        "referral": "Referral Recommendation",
        "precautions": "Recommended Precautions",
        "disclaimer": "⚠️ <b>Disclaimer:</b> This report is AI-generated for decision support only. It does not replace a qualified doctor's diagnosis. If the healthcare worker is not confident in this result, please escalate to a doctor for a second opinion."
    },
    "hi": {
        "title": "आरोग्यमित्र",
        "subtitle": "AI-आधारित रोग भविष्यवाणी रिपोर्ट",
        "date": "दिनांक",
        "worker": "कार्यकर्ता",
        "location": "स्थान",
        "patient_info": "मरीज की जानकारी",
        "name": "नाम",
        "age": "उम्र",
        "gender": "लिंग",
        "symptoms_reported": "बताए गए लक्षण",
        "primary_diagnosis": "प्राथमिक निदान",
        "condition": "स्थिति",
        "confidence": "विश्वास",
        "severity": "गंभीरता स्कोर",
        "differential_diagnoses": "विभेदक निदान (शीर्ष 3)",
        "disease": "रोग",
        "symptoms_table_title": "बताए गए लक्षण और गंभीरता",
        "symptom": "लक्षण",
        "level": "स्तर",
        "high": "उच्च",
        "moderate": "मध्यम",
        "low": "कम",
        "ai_explanation": "AI स्पष्टीकरण (LIME)",
        "lime_desc": "निम्नलिखित कारकों ने इस भविष्यवाणी को सबसे अधिक प्रभावित किया। सकारात्मक प्रभाव = निदान का समर्थन करता है। नकारात्मक प्रभाव = इसके विरुद्ध साक्ष्य।",
        "impact_score": "प्रभाव स्कोर",
        "direction": "दिशा",
        "supports": "निदान का समर्थन करता है",
        "against": "निदान के विरुद्ध",
        "cdss_summary": "नैदानिक निर्णय समर्थन सारांश",
        "diag_summary": "निदान सारांश",
        "conf_interpretation": "विश्वास व्याख्या",
        "sev_assessment": "गंभीरता मूल्यांकन",
        "next_steps": "अनुशंसित अगले कदम",
        "referral": "रेफरल सिफारिश",
        "precautions": "अनुशंसित सावधानियां",
        "disclaimer": "⚠️ <b>अस्वीकरण:</b> यह रिपोर्ट केवल निर्णय समर्थन के लिए AI-जनित है। यह एक योग्य डॉक्टर के निदान की जगह नहीं लेती है। यदि स्वास्थ्य कार्यकर्ता इस परिणाम में आश्वस्त नहीं है, तो कृपया दूसरी राय के लिए डॉक्टर को भेजें।"
    },
    "mr": {
        "title": "आरोग्यमित्र",
        "subtitle": "AI-आधारित रोग भविष्यवाणी अहवाल",
        "date": "तारीख",
        "worker": "कार्यकर्ता",
        "location": "स्थान",
        "patient_info": "रुग्णाची माहिती",
        "name": "नाव",
        "age": "वय",
        "gender": "लिंग",
        "symptoms_reported": "नोंदवलेली लक्षणे",
        "primary_diagnosis": "प्राथमिक निदान",
        "condition": "स्थिती",
        "confidence": "विश्वास",
        "severity": "गंभीरता स्कोर",
        "differential_diagnoses": "विभेदक निदान (शीर्ष ३)",
        "disease": "रोग",
        "symptoms_table_title": "नोंदवलेली लक्षणे आणि गंभीरता",
        "symptom": "लक्षण",
        "level": "स्तर",
        "high": "उच्च",
        "moderate": "मध्यम",
        "low": "कमी",
        "ai_explanation": "AI स्पष्टीकरण (LIME)",
        "lime_desc": "खालील घटकांनी या भविष्यवाणीवर सर्वात जास्त प्रभाव टाकला. सकारात्मक प्रभाव = निदानाचे समर्थन करतो. नकारात्मक प्रभाव = त्याविरुद्ध पुरावा.",
        "impact_score": "प्रभाव स्कोर",
        "direction": "दिशा",
        "supports": "निदानाचे समर्थन करतो",
        "against": "निदानाच्या विरुद्ध",
        "cdss_summary": "क्लिनिकल निर्णय समर्थन सारांश",
        "diag_summary": "निदान सारांश",
        "conf_interpretation": "विश्वास व्याख्या",
        "sev_assessment": "गंभीरता मूल्यांकन",
        "next_steps": "शिफारस केलेली पुढील पावले",
        "referral": "रेफरल शिफारस",
        "precautions": "शिफारस केलेल्या सावधगिरी",
        "disclaimer": "⚠️ <b>अस्वीकरण:</b> हा अहवाल केवळ निर्णय समर्थनासाठी AI-व्युत्पन्न आहे. हे पात्र डॉक्टरांच्या निदानाची जागा घेत नाही. आरोग्य सेवक या निकालाबाबत खात्री नसल्यास, कृपया दुसऱ्या मतासाठी डॉक्टरांकडे पाठवा."
    }
}

# Try to register a font that supports Devanagari
try:
    # On most Ubuntu/Debian systems (like Hugging Face)
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" 
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont('DejaVu', font_path))
        DEFAULT_FONT = 'DejaVu'
    else:
        # Fallback for Windows or systems without DejaVu
        import platform
        if platform.system() == "Windows":
            font_path = "C:/Windows/Fonts/arial.ttf"
            nirmala = "C:/Windows/Fonts/nirmala.ttf"
            if os.path.exists(nirmala):
                pdfmetrics.registerFont(TTFont('Nirmala', nirmala))
                DEFAULT_FONT = 'Nirmala'
            elif os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont('Arial', font_path))
                DEFAULT_FONT = 'Arial'
            else:
                DEFAULT_FONT = 'Helvetica'
        else:
            DEFAULT_FONT = 'Helvetica'
except Exception as e:
    DEFAULT_FONT = 'Helvetica'

# ── PDF Generator ──────────────────────────────────────────────────────────────
def generate_pdf(data: dict, language: str = "en") -> bytes:
    lang = language if language in TRANSLATIONS else "en"
    t = TRANSLATIONS[lang]
    font_name = DEFAULT_FONT if lang != "en" else "Helvetica"
    font_bold = DEFAULT_FONT if lang != "en" else "Helvetica-Bold"

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )

    # Color palette
    PRIMARY    = colors.HexColor('#1B4F72')
    ACCENT     = colors.HexColor('#2E86C1')
    SUCCESS    = colors.HexColor('#1E8449')
    WARNING    = colors.HexColor('#B7950B')
    DANGER     = colors.HexColor('#922B21')
    LIGHT_BG   = colors.HexColor('#EBF5FB')
    LIGHT_GRAY = colors.HexColor('#F2F3F4')
    WHITE      = colors.white

    styles = getSampleStyleSheet()

    def style(name, **kwargs):
        return ParagraphStyle(name, **kwargs)

    title_style    = style('Title',    fontSize=22, textColor=WHITE, alignment=TA_CENTER, fontName=font_bold, spaceAfter=4)
    subtitle_style = style('Subtitle', fontSize=11, textColor=colors.HexColor('#D6EAF8'), alignment=TA_CENTER, fontName=font_name)
    section_style  = style('Section',  fontSize=13, textColor=PRIMARY, fontName=font_bold, spaceBefore=14, spaceAfter=6)
    body_style     = style('Body',     fontSize=10, textColor=colors.HexColor('#2C3E50'), fontName=font_name, leading=16)
    label_style    = style('Label',    fontSize=9,  textColor=WHITE, fontName=font_bold, alignment=TA_CENTER)

    story = []

    # ── Header Banner ────────────────────────────────────────
    header_data = [
        [Paragraph(t["title"], title_style)],
        [Paragraph(t["subtitle"], subtitle_style)],
    ]
    header_table = Table(header_data, colWidths=[17*cm])
    header_table.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (0,0), PRIMARY),
        ('BACKGROUND',    (0,1), (0,1), ACCENT),
        ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING',    (0,0), (0,0), 20),
        ('BOTTOMPADDING', (0,0), (0,0), 20),
        ('TOPPADDING',    (0,1), (0,1), 8),
        ('BOTTOMPADDING', (0,1), (0,1), 10),
        ('LEFTPADDING',   (0,0), (-1,-1), 0),
        ('RIGHTPADDING',  (0,0), (-1,-1), 0),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 12))

    # ── Meta Info Row ─────────────────────────────────────────
    now = datetime.now().strftime("%B %d, %Y  %I:%M %p")
    meta_data = [[
        Paragraph(f"<b>{t['date']}:</b> {now}", body_style),
        Paragraph(f"<b>{t['worker']}:</b> {data.get('workerName', 'Healthcare Worker')}", body_style),
        Paragraph(f"<b>{t['location']}:</b> {data.get('location','—')}", body_style),
    ]]
    meta_table = Table(meta_data, colWidths=[5.6*cm, 5.6*cm, 5.8*cm])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0),(-1,-1), LIGHT_GRAY),
        ('TOPPADDING',    (0,0),(-1,-1), 8),
        ('BOTTOMPADDING', (0,0),(-1,-1), 8),
        ('LEFTPADDING',   (0,0),(-1,-1), 10),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 14))

    # ── Patient Information ───────────────────────────────────
    story.append(Paragraph(t["patient_info"], section_style))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT))
    story.append(Spacer(1, 8))

    gender  = str(data.get('patientGender') or '—').capitalize()
    age     = str(data.get('patientAge') or '—')
    patient_data = [
        [Paragraph(f'<b>{t["name"]}</b>', body_style),    Paragraph(data['patientName'], body_style),
         Paragraph(f'<b>{t["age"]}</b>', body_style),     Paragraph(age, body_style)],
        [Paragraph(f'<b>{t["gender"]}</b>', body_style),  Paragraph(gender, body_style),
         Paragraph(f'<b>{t["symptoms_reported"]}</b>', body_style), Paragraph(str(len(data.get('matchedSymptoms', []))), body_style)],
    ]
    pt = Table(patient_data, colWidths=[3.5*cm, 5*cm, 4.5*cm, 4*cm])
    pt.setStyle(TableStyle([
        ('BACKGROUND',    (0,0),(-1,-1), LIGHT_BG),
        ('TOPPADDING',    (0,0),(-1,-1), 7),
        ('BOTTOMPADDING', (0,0),(-1,-1), 7),
        ('LEFTPADDING',   (0,0),(-1,-1), 8),
        ('GRID',          (0,0),(-1,-1), 0.5, colors.HexColor('#AED6F1')),
    ]))
    story.append(pt)
    story.append(Spacer(1, 14))

    # ── Primary Diagnosis ─────────────────────────────────────
    story.append(Paragraph(t["primary_diagnosis"], section_style))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT))
    story.append(Spacer(1, 8))

    conf = data.get('confidenceScore', 0)
    conf_color = SUCCESS if conf >= 75 else WARNING if conf >= 50 else DANGER
    sev = data.get('severityScore', 0)
    sev_color  = DANGER if sev >= 5 else WARNING if sev >= 3 else SUCCESS

    diag_data = [
        [Paragraph(f'<b>{t["condition"]}</b>', label_style),
         Paragraph(f'<b>{t["confidence"]}</b>', label_style),
         Paragraph(f'<b>{t["severity"]}</b>', label_style)],
        [Paragraph(data.get('primaryDiagnosis', 'Unknown'), ParagraphStyle('dp', fontSize=13, fontName=font_bold, textColor=PRIMARY, alignment=TA_CENTER)),
         Paragraph(f"{conf}%", ParagraphStyle('cp', fontSize=13, fontName=font_bold, textColor=conf_color, alignment=TA_CENTER)),
         Paragraph(f"{sev} / 7", ParagraphStyle('sp', fontSize=13, fontName=font_bold, textColor=sev_color, alignment=TA_CENTER))],
    ]
    dt = Table(diag_data, colWidths=[6*cm, 5.5*cm, 5.5*cm])
    dt.setStyle(TableStyle([
        ('BACKGROUND',    (0,0),(-1,0), PRIMARY),
        ('BACKGROUND',    (0,1),(-1,1), LIGHT_BG),
        ('TOPPADDING',    (0,0),(-1,-1), 10),
        ('BOTTOMPADDING', (0,0),(-1,-1), 10),
        ('GRID',          (0,0),(-1,-1), 0.5, colors.HexColor('#AED6F1')),
    ]))
    story.append(dt)
    story.append(Spacer(1, 8))

    # Description
    story.append(Paragraph(f"<i>{data.get('description', '')}</i>", body_style))
    story.append(Spacer(1, 14))

    # ── Alternative Diagnoses ─────────────────────────────────
    story.append(Paragraph(t["differential_diagnoses"], section_style))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT))
    story.append(Spacer(1, 8))

    alt_headers = [[
        Paragraph('#', label_style),
        Paragraph(t["disease"], label_style),
        Paragraph(f'{t["confidence"]} (%)', label_style),
    ]]
    alt_rows = [
        [Paragraph(str(i+1), body_style),
         Paragraph(p['disease'], body_style),
         Paragraph(f"{p['confidence']}%", body_style)]
        for i, p in enumerate(data.get('topPredictions', []))
    ]
    if not alt_rows:
        alt_rows = [[Paragraph("-", body_style), Paragraph("-", body_style), Paragraph("-", body_style)]]

    alt_table = Table(alt_headers + alt_rows, colWidths=[1.5*cm, 10*cm, 5.5*cm])
    alt_table.setStyle(TableStyle([
        ('BACKGROUND',    (0,0),(-1,0), PRIMARY),
        ('BACKGROUND',    (0,1),(-1,-1), LIGHT_GRAY),
        ('ROWBACKGROUNDS',(0,1),(-1,-1), [LIGHT_BG, WHITE]),
        ('TOPPADDING',    (0,0),(-1,-1), 7),
        ('BOTTOMPADDING', (0,0),(-1,-1), 7),
        ('LEFTPADDING',   (0,0),(-1,-1), 8),
        ('GRID',          (0,0),(-1,-1), 0.5, colors.HexColor('#AED6F1')),
    ]))
    story.append(alt_table)
    story.append(Spacer(1, 14))

    # ── Symptoms & Severity ───────────────────────────────────
    story.append(Paragraph(t["symptoms_table_title"], section_style))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT))
    story.append(Spacer(1, 8))

    sev_headers = [[
        Paragraph(t["symptom"], label_style),
        Paragraph(f'{t["severity"]} (1–7)', label_style),
        Paragraph(t["level"], label_style),
    ]]
    def sev_label_text(s):
        if s >= 6: return t['high']
        if s >= 3: return t['moderate']
        return t['low']
    def sev_row_color(s):
        if s >= 6: return colors.HexColor('#FDEDEC')
        if s >= 3: return colors.HexColor('#FEF9E7')
        return colors.HexColor('#EAFAF1')

    symptom_sevs = data.get('symptomSeverities', [])
    sev_rows = [
        [Paragraph(sv['symptom'], body_style),
         Paragraph(str(sv['severity']), body_style),
         Paragraph(sev_label_text(sv['severity']), body_style)]
        for sv in symptom_sevs
    ]
    if not sev_rows:
        sev_rows = [[Paragraph("-", body_style), Paragraph("-", body_style), Paragraph("-", body_style)]]

    sev_table = Table(sev_headers + sev_rows, colWidths=[8*cm, 5*cm, 4*cm])
    row_styles = [
        ('BACKGROUND', (0, i+1), (-1, i+1), sev_row_color(symptom_sevs[i]['severity']))
        for i in range(len(symptom_sevs))
    ]
    sev_table.setStyle(TableStyle([
        ('BACKGROUND',    (0,0),(-1,0), PRIMARY),
        ('TOPPADDING',    (0,0),(-1,-1), 7),
        ('BOTTOMPADDING', (0,0),(-1,-1), 7),
        ('LEFTPADDING',   (0,0),(-1,-1), 8),
        ('GRID',          (0,0),(-1,-1), 0.5, colors.HexColor('#AED6F1')),
    ] + row_styles))
    story.append(sev_table)
    story.append(Spacer(1, 14))

    # ── LIME Explanation ──────────────────────────────────────
    story.append(Paragraph(t["ai_explanation"], section_style))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT))
    story.append(Spacer(1, 6))
    story.append(Paragraph(t["lime_desc"], body_style))
    story.append(Spacer(1, 8))

    lime_headers = [[
        Paragraph(f'{t["condition"]} / {t["symptom"]}', label_style),
        Paragraph(t["impact_score"], label_style),
        Paragraph(t["direction"], label_style),
    ]]
    lime_exps = data.get('limeExplanation', [])
    lime_rows = [
        [Paragraph(l['feature'], body_style),
         Paragraph(str(l['impact']), body_style),
         Paragraph(t['supports'] if 'Supports' in l['direction'] else t['against'], ParagraphStyle('dir', fontSize=10,
             textColor=SUCCESS if 'Supports' in l['direction'] else DANGER,
             fontName=font_bold))]
        for l in lime_exps
    ]
    if not lime_rows:
         lime_rows = [[Paragraph("-", body_style), Paragraph("-", body_style), Paragraph("-", body_style)]]

    lime_table = Table(lime_headers + lime_rows, colWidths=[8*cm, 4.5*cm, 4.5*cm])
    lime_table.setStyle(TableStyle([
        ('BACKGROUND',    (0,0),(-1,0), PRIMARY),
        ('ROWBACKGROUNDS',(0,1),(-1,-1), [LIGHT_BG, WHITE]),
        ('TOPPADDING',    (0,0),(-1,-1), 7),
        ('BOTTOMPADDING', (0,0),(-1,-1), 7),
        ('LEFTPADDING',   (0,0),(-1,-1), 8),
        ('GRID',          (0,0),(-1,-1), 0.5, colors.HexColor('#AED6F1')),
    ]))
    story.append(lime_table)
    story.append(Spacer(1, 14))

    # ── Clinical Conclusion (LLM) ─────────────────────────────
    story.append(Paragraph(t["cdss_summary"], section_style))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT))
    story.append(Spacer(1, 8))

    llm = data.get("llmConclusion", {})

    story.append(Paragraph(t["diag_summary"], section_style))
    story.append(Paragraph(llm.get("diagnosis_summary", ""), body_style))

    story.append(Paragraph(t["conf_interpretation"], section_style))
    story.append(Paragraph(llm.get("confidence_interpretation", ""), body_style))

    story.append(Paragraph(t["sev_assessment"], section_style))
    story.append(Paragraph(llm.get("severity_assessment", ""), body_style))

    story.append(Paragraph(t["next_steps"], section_style))
    story.append(Paragraph(llm.get("recommended_next_steps", ""), body_style))

    story.append(Paragraph(t["referral"], section_style))
    story.append(Paragraph(llm.get("referral_recommendation", ""), body_style))

    # ── Precautions ───────────────────────────────────────────
    story.append(KeepTogether([
        Paragraph(t["precautions"], section_style),
        HRFlowable(width="100%", thickness=1, color=ACCENT),
        Spacer(1, 8),
    ]))
    for i, p in enumerate(data.get('precautions', []), 1):
        story.append(Paragraph(f"&nbsp;&nbsp;{i}.  {p.capitalize()}", body_style))
        story.append(Spacer(1, 4))
    story.append(Spacer(1, 14))

    # ── Disclaimer ────────────────────────────────────────────
    disclaimer_data = [[Paragraph(t["disclaimer"],
        ParagraphStyle('disc', fontSize=9, textColor=colors.HexColor('#7D6608'),
                       fontName=font_name, leading=14)
    )]]
    disc_table = Table(disclaimer_data, colWidths=[17*cm])
    disc_table.setStyle(TableStyle([
        ('BACKGROUND',    (0,0),(-1,-1), colors.HexColor('#FEF9E7')),
        ('BOX',           (0,0),(-1,-1), 1, colors.HexColor('#F0B27A')),
        ('TOPPADDING',    (0,0),(-1,-1), 10),
        ('BOTTOMPADDING', (0,0),(-1,-1), 10),
        ('LEFTPADDING',   (0,0),(-1,-1), 12),
        ('RIGHTPADDING',  (0,0),(-1,-1), 12),
    ]))
    story.append(disc_table)

    doc.build(story)
    buffer.seek(0)
    return buffer.read()
