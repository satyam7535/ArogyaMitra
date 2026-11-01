"""
ArogyaMitra — Report Front Matter Builder (Item 16, 18, 19 Compliant)
Builds:
1. Cover Page (with [CONFIRM TITLE] Ashish Singh, ECE dept)
2. Bonafide Certificate
3. Merged Declaration & Conflict of Interest (Single Page)
4. Acknowledgements (Guidance and periodic review only)
5. Abstract ("zero fixable Critical/High (Trivy --ignore-unfixed)")
6. Table of Contents
7. Merged List of Figures & List of Tables (Single Page)
8. List of Abbreviations
"""

from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from report_styles import add_p, add_h1, add_h2, set_cell_margins, set_table_borders, NAVY_BLUE, MUTED_GREY, DARK_GREY

def add_cover_page(doc):
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_before = Pt(8)
    p_inst.paragraph_format.space_after = Pt(2)
    r = p_inst.add_run("INDIAN INSTITUTE OF INFORMATION TECHNOLOGY, PUNE")
    r.font.name = 'Times New Roman'; r.font.size = Pt(14); r.bold = True; r.font.color.rgb = NAVY_BLUE
    
    p_dept = doc.add_paragraph()
    p_dept.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_dept.paragraph_format.space_after = Pt(28)
    r = p_dept.add_run("Department of Computer Science and Engineering")
    r.font.name = 'Times New Roman'; r.font.size = Pt(11.5); r.bold = True
    
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(16)
    p_title.paragraph_format.space_after = Pt(14)
    p_title.paragraph_format.line_spacing = 1.2
    r = p_title.add_run("ArogyaMitra: A Secure, Explainable, Fail-Closed AI-Assisted Primary-Healthcare Decision Support System")
    r.font.name = 'Times New Roman'; r.font.size = Pt(16); r.bold = True; r.font.color.rgb = NAVY_BLUE
    
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(12)
    p_sub.paragraph_format.space_after = Pt(28)
    r = p_sub.add_run("A Project Report Submitted in Partial Fulfillment of the Requirements\nfor the Degree of Bachelor of Technology in Computer Science and Engineering")
    r.font.name = 'Times New Roman'; r.font.size = Pt(11); r.font.italic = True; r.font.color.rgb = MUTED_GREY
    
    # Metadata Table
    table = doc.add_table(rows=1, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.columns[0].width = Inches(3.3)
    table.columns[1].width = Inches(3.3)
    
    # Student cell
    c0 = table.cell(0, 0)
    p0 = c0.paragraphs[0]
    p0.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p0.paragraph_format.line_spacing = 1.15
    r = p0.add_run("Submitted By:\n")
    r.font.name = 'Times New Roman'; r.font.size = Pt(10.5); r.bold = True
    r = p0.add_run("Satyam Keshari\n")
    r.font.name = 'Times New Roman'; r.font.size = Pt(11); r.bold = True
    r = p0.add_run("MIS: 112315168\nB.Tech CSE (Semester VII)\nDept. of Computer Science & Engineering")
    r.font.name = 'Times New Roman'; r.font.size = Pt(10)
    
    # Supervisor cell (Item 16: ECE Dept)
    c1 = table.cell(0, 1)
    p1 = c1.paragraphs[0]
    p1.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p1.paragraph_format.line_spacing = 1.15
    r = p1.add_run("Under the Guidance of:\n")
    r.font.name = 'Times New Roman'; r.font.size = Pt(10.5); r.bold = True
    r = p1.add_run("[CONFIRM TITLE] Ashish Singh\n")
    r.font.name = 'Times New Roman'; r.font.size = Pt(11); r.bold = True
    r = p1.add_run("Adjunct Assistant Professor\nDept. of Electronics & Communication Engineering\nIIIT Pune")
    r.font.name = 'Times New Roman'; r.font.size = Pt(10)
    
    p_footer = doc.add_paragraph()
    p_footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_footer.paragraph_format.space_before = Pt(50)
    p_footer.paragraph_format.space_after = Pt(0)
    p_footer.paragraph_format.line_spacing = 1.15
    r = p_footer.add_run("Department of Computer Science and Engineering\nIndian Institute of Information Technology, Pune\nNovember 2026 (Academic Year 2026–2027)")
    r.font.name = 'Times New Roman'; r.font.size = Pt(10.5); r.bold = True; r.font.color.rgb = DARK_GREY

def add_bonafide_certificate(doc):
    doc.add_page_break()
    p_h = doc.add_paragraph()
    p_h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_h.paragraph_format.space_before = Pt(12)
    p_h.paragraph_format.space_after = Pt(4)
    r = p_h.add_run("INDIAN INSTITUTE OF INFORMATION TECHNOLOGY, PUNE")
    r.font.name = 'Times New Roman'; r.font.size = Pt(13); r.bold = True; r.font.color.rgb = NAVY_BLUE
    
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(16)
    r = p_sub.add_run("Department of Computer Science and Engineering")
    r.font.name = 'Times New Roman'; r.font.size = Pt(11); r.bold = True
    
    p_cert = doc.add_paragraph()
    p_cert.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cert.paragraph_format.space_before = Pt(8)
    p_cert.paragraph_format.space_after = Pt(14)
    r = p_cert.add_run("BONAFIDE CERTIFICATE")
    r.font.name = 'Times New Roman'; r.font.size = Pt(13); r.bold = True; r.underline = True; r.font.color.rgb = NAVY_BLUE
    
    add_p(doc, "This is to certify that the project report entitled \"ArogyaMitra: A Secure, Explainable, Fail-Closed AI-Assisted Primary-Healthcare Decision Support System\" submitted by Satyam Keshari (MIS: 112315168) in partial fulfillment of the requirements for the award of the degree of Bachelor of Technology in Computer Science and Engineering at the Indian Institute of Information Technology, Pune, is a bonafide record of the work carried out under my supervision during the academic year 2026–2027.", space_before=8, space_after=10)
    
    add_p(doc, "The matter embodied in this report has not been submitted to any other University or Institute for the award of any degree or diploma. The system was designed and benchmarked as an academic decision support prototype in accordance with institutional guidelines.", space_before=4, space_after=32)
    
    # Signature blocks
    table = doc.add_table(rows=1, cols=3)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.columns[0].width = Inches(2.2)
    table.columns[1].width = Inches(2.2)
    table.columns[2].width = Inches(2.2)
    
    # Col 0: Guide
    c0 = table.cell(0, 0)
    p0 = c0.paragraphs[0]; p0.alignment = WD_ALIGN_PARAGRAPH.CENTER; p0.paragraph_format.line_spacing = 1.15
    r = p0.add_run("_____________________\n[CONFIRM TITLE] Ashish Singh\nProject Supervisor\nAdjunct Assistant Professor, ECE\nIIIT Pune")
    r.font.name = 'Times New Roman'; r.font.size = Pt(9.5)
    
    # Col 1: HoD
    c1 = table.cell(0, 1)
    p1 = c1.paragraphs[0]; p1.alignment = WD_ALIGN_PARAGRAPH.CENTER; p1.paragraph_format.line_spacing = 1.15
    r = p1.add_run("_____________________\n[CONFIRM HOD NAME]\nHead of Department\nDept. of CSE\nIIIT Pune")
    r.font.name = 'Times New Roman'; r.font.size = Pt(9.5)
    
    # Col 2: External
    c2 = table.cell(0, 2)
    p2 = c2.paragraphs[0]; p2.alignment = WD_ALIGN_PARAGRAPH.CENTER; p2.paragraph_format.line_spacing = 1.15
    r = p2.add_run("_____________________\nExternal Examiner\nEvaluation Committee\nIIIT Pune")
    r.font.name = 'Times New Roman'; r.font.size = Pt(9.5)

def add_declaration_and_conflict_page(doc):
    """Merged Declaration & Conflict of Interest on a single page (Item 18)."""
    doc.add_page_break()
    p_cert = doc.add_paragraph()
    p_cert.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cert.paragraph_format.space_before = Pt(12)
    p_cert.paragraph_format.space_after = Pt(12)
    r = p_cert.add_run("DECLARATION & PLAGIARISM UNDERTAKING")
    r.font.name = 'Times New Roman'; r.font.size = Pt(12.5); r.bold = True; r.underline = True; r.font.color.rgb = NAVY_BLUE
    
    add_p(doc, "I, Satyam Keshari (MIS: 112315168), student of Bachelor of Technology in Computer Science and Engineering, Semester VII, IIIT Pune, hereby declare that the work presented in this project report entitled \"ArogyaMitra: A Secure, Explainable, Fail-Closed AI-Assisted Primary-Healthcare Decision Support System\" is my original engineering implementation.", space_before=4, space_after=6)
    
    add_p(doc, "I affirm that: (1) All components, pipelines, container definitions, and test suites were engineered directly within the repository; (2) All reported empirical metrics (cross-validation accuracies, ECE, throughput, test counts, vulnerability scans) correspond to verifiable logs in docs/evidence/ and are cited with file:line; (3) Generative AI tools (LLM assistants) were used for code refactoring, test script scaffolding, and document formatting; all architectural decisions, mathematical derivations, bug discoveries, and empirical verifications were performed directly by the student.", space_before=2, space_after=10)
    
    p_coi = doc.add_paragraph()
    p_coi.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_coi.paragraph_format.space_before = Pt(8)
    p_coi.paragraph_format.space_after = Pt(8)
    r = p_coi.add_run("CONFLICT OF INTEREST STATEMENT")
    r.font.name = 'Times New Roman'; r.font.size = Pt(12); r.bold = True; r.underline = True; r.font.color.rgb = NAVY_BLUE
    
    add_p(doc, "The author declares that there are no financial, commercial, or personal conflicts of interest. The ArogyaMitra system was engineered strictly as an academic research and engineering prototype in clinical decision support. No commercial sponsorship was accepted.", space_before=4, space_after=6)
    add_p(doc, "The machine learning models were trained and benchmarked exclusively on synthetic clinical symptom datasets (304 unique rows). The system has not been tested on live human patients, has not accessed identifiable protected health information, and is not certified as a medical device by CDSCO or the FDA.", space_before=2, space_after=18)
    
    p_sign = doc.add_paragraph()
    p_sign.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_sign.paragraph_format.line_spacing = 1.15
    r = p_sign.add_run("______________________________\nSatyam Keshari (MIS: 112315168)\nDept. of CSE, IIIT Pune | Date: November 01, 2026")
    r.font.name = 'Times New Roman'; r.font.size = Pt(10)

def add_acknowledgements(doc):
    """Acknowledgements thanking supervisor for guidance and periodic review only (Item 16)."""
    doc.add_page_break()
    p_cert = doc.add_paragraph()
    p_cert.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cert.paragraph_format.space_before = Pt(14)
    p_cert.paragraph_format.space_after = Pt(16)
    r = p_cert.add_run("ACKNOWLEDGEMENTS")
    r.font.name = 'Times New Roman'; r.font.size = Pt(13); r.bold = True; r.underline = True; r.font.color.rgb = NAVY_BLUE
    
    add_p(doc, "I express my sincere gratitude to my project supervisor, [CONFIRM TITLE] Ashish Singh, Adjunct Assistant Professor, Department of Electronics and Communication Engineering, IIIT Pune, for his guidance, periodic review, and valuable feedback throughout the course of this project. His reviews helped ensure that the engineering milestones and project goals remained on track.", space_before=10, space_after=10)
    
    add_p(doc, "I extend my appreciation to the Head of Department, [CONFIRM HOD NAME], Department of Computer Science and Engineering, and [CONFIRM DIRECTOR NAME], Director, IIIT Pune, for providing the institutional computing facilities and academic environment essential for completing this B.Tech capstone project.", space_before=4, space_after=10)
    
    add_p(doc, "I also thank the faculty members of the Department of Computer Science and Engineering for their evaluation and questions during project reviews, which helped refine the system requirements and testing approach.", space_before=4, space_after=10)
    
    add_p(doc, "Finally, I thank my family and peers for their continuous support and patience throughout the duration of this work.", space_before=4, space_after=20)
    
    p_sign = doc.add_paragraph()
    p_sign.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r = p_sign.add_run("Satyam Keshari\nMIS: 112315168")
    r.font.name = 'Times New Roman'; r.font.size = Pt(10.5)

def add_abstract(doc):
    """Abstract with 'zero fixable Critical/High (Trivy --ignore-unfixed)' and neutral tone (Item 2, 14)."""
    doc.add_page_break()
    p_cert = doc.add_paragraph()
    p_cert.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cert.paragraph_format.space_before = Pt(14)
    p_cert.paragraph_format.space_after = Pt(16)
    r = p_cert.add_run("ABSTRACT")
    r.font.name = 'Times New Roman'; r.font.size = Pt(13); r.bold = True; r.underline = True; r.font.color.rgb = NAVY_BLUE
    
    add_p(doc, "In primary healthcare settings across rural and semi-urban India, community health workers such as Accredited Social Health Activists (ASHAs) conduct patient intake under limited diagnostic resources and high patient loads. Digital symptom checkers have been proposed to assist triage, but systematic reviews (notably Wallace et al. [1]) show that digital symptom checkers exhibit low primary diagnostic accuracy (19–37.9%) and variable triage accuracy (48.8–90.1%), with an alignment of errors that can create patient safety hazards. Furthermore, theoretical machine learning literature (Niculescu-Mizil & Caruana [2]) demonstrates that Naive Bayes classifiers push predicted probabilities toward 0 and 1 due to conditional feature independence assumptions, producing uncalibrated estimates.", space_before=10, space_after=8)
    
    add_p(doc, "To address these operational risks, this project implements ArogyaMitra, a decision support prototype designed for frontline health workers. The system incorporates: (1) a stateless Bernoulli Naive Bayes classifier trained across 41 disease classes and 131 symptoms, accompanied by closed-form additive log-odds feature attributions; (2) a deterministic red-flag screening layer that overrides model predictions when emergency symptoms are present; (3) a guarded Large Language Model narrative layer with ordered model cascade, a 10-second per-attempt timeout, a 20-second hard cap, and whole-phrase confidence filtering backed by pre-compiled fallback templates; and (4) a containerized architecture with TLS 1.2/1.3, Argon2id password hashing, field-level AES-256-GCM encryption, and optimistic concurrency controls.", space_before=4, space_after=8)
    
    add_p(doc, "Empirical evaluation on a deduplicated benchmark of 304 unique rows (derived by removing 4,616 exact duplicate rows from a 4,920-row dataset) using 5x3 repeated stratified cross-validation showed BernoulliNB achieving Top-1 accuracy of 1.000 ± 0.000 at 0% dropout, 0.989 ± 0.014 at 30% dropout, and 0.919 ± 0.023 at 50% dropout, compared to Tuned LightGBM (0.989, 0.864, 0.683) and Tuned XGBoost (0.984, 0.868, 0.720). Load testing across 2,400 requests in test mode showed system throughput reaching 14.7 req/s under 50 concurrent users with 100% HTTP 200 responses, while server-side pagination and projection reduced worker list p50 latency from 193.0 ms to 76.2 ms. Automated test suites verify 322 prototype test cases, 20 golden cases, 11 Playwright journeys, and zero fixable Critical/High (Trivy --ignore-unfixed) container vulnerabilities.", space_before=4, space_after=12)
    
    p_kw = doc.add_paragraph()
    p_kw.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r_kwh = p_kw.add_run("Keywords: ")
    r_kwh.font.name = 'Times New Roman'; r_kwh.font.size = Pt(10); r_kwh.bold = True
    r_kwt = p_kw.add_run("Clinical Decision Support, Primary Healthcare Triage, Bernoulli Naive Bayes, Uncalibrated Posterior Estimation, Fail-Closed Architecture, Large Language Models, Container Security.")
    r_kwt.font.name = 'Times New Roman'; r_kwt.font.size = Pt(10); r_kwt.font.italic = True

def add_table_of_contents_pages(doc):
    doc.add_page_break()
    p_h = doc.add_paragraph()
    p_h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_h.paragraph_format.space_before = Pt(8)
    p_h.paragraph_format.space_after = Pt(8)
    r = p_h.add_run("TABLE OF CONTENTS")
    r.font.name = 'Times New Roman'; r.font.size = Pt(12.5); r.bold = True; r.underline = True; r.font.color.rgb = NAVY_BLUE
    
    toc_items = [
        ("Bonafide Certificate", "ii"),
        ("Declaration & Conflict of Interest", "iii"),
        ("Acknowledgements", "iv"),
        ("Abstract", "v"),
        ("List of Figures & List of Tables", "vi"),
        ("List of Abbreviations", "vii"),
        ("Chapter 1: Introduction & Literature Review", "1"),
        ("    1.1 Motivation & Primary Healthcare Challenges in Rural India", "1"),
        ("    1.2 Comprehensive Literature Review", "2"),
        ("        1.2.1 Review of Symptom Checkers, Decision Support, and Calibration", "2"),
        ("        1.2.2 Comparison with Existing Work", "3"),
        ("    1.3 Problem Statement & Design Objectives", "4"),
        ("    1.4 Design Evolution", "4"),
        ("    1.5 Report Outline & Organization", "5"),
        ("Chapter 2: System Requirements & Threat Modeling", "6"),
        ("    2.1 Functional Requirements (FR-1 to FR-10)", "6"),
        ("    2.2 Non-Functional Requirements (NFR-1 to NFR-8)", "6"),
        ("    2.3 Threat Model & Security Analysis (STRIDE Matrix)", "7"),
        ("    2.4 Clinical Safety & Ethics Requirements", "7"),
        ("Chapter 3: System Architecture & Design", "9"),
        ("    3.1 Architectural Overview & Container Topology", "9"),
        ("    3.2 Machine Learning Inference & Calibration Engine", "10"),
        ("        3.2.1 Bernoulli Naive Bayes Mathematical Formulation", "10"),
        ("        3.2.2 Feature Engineering & Vocabulary Alignment", "11"),
        ("        3.2.3 Explainability via Top-Feature Attribution", "11"),
        ("        3.2.4 Calibration Theoretical Background & Analysis", "11"),
        ("        3.2.5 Comparative Model Selection", "12"),
        ("    3.3 Rule-Based Clinical Red-Flag Override System", "12"),
        ("    3.4 Multi-Tier LLM Explanation & Resilient Fallback Layer", "13"),
        ("    3.5 End-to-End Clinical Consultation Workflow", "14"),
        ("    3.6 Security Architecture & Cryptographic Implementation", "14"),
        ("    3.7 Database Design, Concurrency & Data Integrity", "15"),
        ("    3.8 Logging and Audit System", "15"),
        ("Chapter 4: Empirical Evaluation & Experimental Results", "16"),
        ("    4.1 Dataset Profile & Methodological Integrity", "16"),
        ("    4.2 Machine Learning Performance & Robustness", "16"),
        ("    4.3 Load Testing, Concurrency & System Throughput", "17"),
        ("    4.4 Automated Testing & Verification Suite", "19"),
        ("    4.5 Security Vulnerability & Dependency Auditing", "20"),
        ("    4.6 Literature-Linked Discussion & Analysis", "21"),
        ("    4.7 Limitations & Threats to Validity", "21"),
        ("Chapter 5: Conclusion & Future Scope", "23"),
        ("    5.1 Project Summary & Achievements", "23"),
        ("    5.2 Lessons Learned & Engineering Insights", "23"),
        ("    5.3 Future Work & Roadmap", "23"),
        ("References", "25"),
        ("Appendix A: Engineering Challenges, Root Causes, and Architectural Fixes", "26"),
        ("Appendix B: Reproduction Commands Playbook", "28"),
    ]
    
    for title, page in toc_items:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(0.5)
        p.paragraph_format.space_after = Pt(0.5)
        p.paragraph_format.line_spacing = 1.05
        
        is_major = not title.startswith("    ") and not title.startswith("        ")
        r1 = p.add_run(title)
        r1.font.name = 'Times New Roman'
        r1.font.size = Pt(8.5 if not is_major else 9.0)
        r1.bold = is_major
        if is_major and "Chapter" in title:
            r1.font.color.rgb = NAVY_BLUE
            
        num_dots = max(4, 78 - len(title))
        dots_str = " " + ". " * (num_dots // 2) + " "
        r2 = p.add_run(dots_str)
        r2.font.name = 'Times New Roman'; r2.font.size = Pt(7.5); r2.font.color.rgb = MUTED_GREY
        
        r3 = p.add_run(page)
        r3.font.name = 'Times New Roman'; r3.font.size = Pt(8.5 if not is_major else 9.0); r3.bold = is_major

def add_merged_list_of_figures_and_tables(doc):
    """List of Figures and List of Tables together on one page (Item 18)."""
    doc.add_page_break()
    p_h = doc.add_paragraph()
    p_h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_h.paragraph_format.space_before = Pt(12)
    p_h.paragraph_format.space_after = Pt(8)
    r = p_h.add_run("LIST OF FIGURES")
    r.font.name = 'Times New Roman'; r.font.size = Pt(12); r.bold = True; r.underline = True; r.font.color.rgb = NAVY_BLUE
    
    figures = [
        ("Figure 3.1", "Container Topology, Network Boundaries, and Data Tiers", "9"),
        ("Figure 3.2", "Consultation Lifecycle State Machine and Decision Gates", "14"),
        ("Figure 3.3", "Hierarchical Request Timeout Budgets and Guardrail Cascade", "14"),
        ("Figure 4.1", "Top-1 Accuracy and Expected Calibration Error (ECE) vs. Dropout", "17"),
        ("Figure 4.2", "Dataset Provenance: Raw 4,920 Rows vs. 304 Deduplicated Unique Rows", "16"),
        ("Figure 4.3", "Gateway Throughput and Percentile Latencies Across Concurrency", "18"),
        ("Figure 4.4", "Worker List Latency Before vs. After Pagination and Projection", "18"),
        ("Figure 4.5", "User Interface Journeys: Worker Intake, Red-Flag Block, Pagination, Outage", "19"),
    ]
    
    for f_id, f_desc, f_page in figures:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(1); p.paragraph_format.space_after = Pt(1); p.paragraph_format.line_spacing = 1.15
        r1 = p.add_run(f"{f_id}: {f_desc}")
        r1.font.name = 'Times New Roman'; r1.font.size = Pt(9)
        num_dots = max(4, 76 - len(f"{f_id}: {f_desc}"))
        r2 = p.add_run(" " + ". " * (num_dots // 2) + " ")
        r2.font.name = 'Times New Roman'; r2.font.size = Pt(8); r2.font.color.rgb = MUTED_GREY
        r3 = p.add_run(f_page)
        r3.font.name = 'Times New Roman'; r3.font.size = Pt(9); r3.bold = True

    p_h2 = doc.add_paragraph()
    p_h2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_h2.paragraph_format.space_before = Pt(14)
    p_h2.paragraph_format.space_after = Pt(8)
    r = p_h2.add_run("LIST OF TABLES")
    r.font.name = 'Times New Roman'; r.font.size = Pt(12); r.bold = True; r.underline = True; r.font.color.rgb = NAVY_BLUE
    
    tables = [
        ("Table 1.1", "Comprehensive Literature Review Summary Matrix", "2"),
        ("Table 1.2", "Systematic Comparison: Clinical Concerns vs. ArogyaMitra Implementations", "3"),
        ("Table 2.1", "System Functional Requirements Specification (FR-1 to FR-10)", "6"),
        ("Table 2.2", "System Non-Functional Requirements: Targets vs. Measured Results", "6"),
        ("Table 2.3", "STRIDE Threat Model and Architectural Security Controls", "7"),
        ("Table 3.1", "Emergency Red-Flag Trigger Symptoms (config/red_flags.yaml)", "12"),
        ("Table 3.2", "Container Technology Stack and Component Allocation", "9"),
        ("Table 4.1", "Repeated Stratified 5x3 Cross-Validation Accuracy Across Dropout", "17"),
        ("Table 4.2", "Expected Calibration Error (ECE) Across Dropout Rates", "17"),
        ("Table 4.3", "Load Test Benchmark Results Across Concurrency Levels (2,400 Requests)", "18"),
        ("Table 4.4", "Worker List Latency Before vs. After Pagination and Projection", "18"),
        ("Table 4.5", "Automated Test Suite Summary from Actual Test Runners (322 Tests)", "19"),
        ("Table 4.6", "OWASP ZAP Dynamic Security Baseline Scan Dispositions (6 Alerts)", "20"),
        ("Table A.1", "Engineering Challenges, Root Causes, and Architectural Remediation Fixes", "26"),
    ]
    
    for t_id, t_desc, t_page in tables:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(1); p.paragraph_format.space_after = Pt(1); p.paragraph_format.line_spacing = 1.15
        r1 = p.add_run(f"{t_id}: {t_desc}")
        r1.font.name = 'Times New Roman'; r1.font.size = Pt(9)
        num_dots = max(4, 76 - len(f"{t_id}: {t_desc}"))
        r2 = p.add_run(" " + ". " * (num_dots // 2) + " ")
        r2.font.name = 'Times New Roman'; r2.font.size = Pt(8); r2.font.color.rgb = MUTED_GREY
        r3 = p.add_run(t_page)
        r3.font.name = 'Times New Roman'; r3.font.size = Pt(9); r3.bold = True

def add_abbreviations(doc):
    doc.add_page_break()
    p_h = doc.add_paragraph()
    p_h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_h.paragraph_format.space_before = Pt(12)
    p_h.paragraph_format.space_after = Pt(12)
    r = p_h.add_run("LIST OF ABBREVIATIONS")
    r.font.name = 'Times New Roman'; r.font.size = Pt(13); r.bold = True; r.underline = True; r.font.color.rgb = NAVY_BLUE
    
    abbrevs = [
        ("ABDM", "Ayushman Bharat Digital Mission"),
        ("AES-GCM", "Advanced Encryption Standard in Galois/Counter Mode"),
        ("ANM", "Auxiliary Nurse Midwife"),
        ("ASHA", "Accredited Social Health Activist"),
        ("CDSCO", "Central Drugs Standard Control Organisation (India)"),
        ("CSP", "Content Security Policy"),
        ("CV", "Cross-Validation"),
        ("DPDP", "Digital Personal Data Protection Act, 2023 (India)"),
        ("ECE", "Expected Calibration Error"),
        ("FHIR", "Fast Healthcare Interoperability Resources"),
        ("HSTS", "HTTP Strict Transport Security"),
        ("HWC", "Health and Wellness Centre"),
        ("JWT", "JSON Web Token"),
        ("LLM", "Large Language Model"),
        ("MAP", "Maximum A Posteriori"),
        ("ML", "Machine Learning"),
        ("NB", "Naive Bayes"),
        ("NFR", "Non-Functional Requirement"),
        ("OCC", "Optimistic Concurrency Control"),
        ("PHC", "Primary Health Centre"),
        ("PII", "Personally Identifiable Information"),
        ("QUADAS-2", "Quality Assessment of Diagnostic Accuracy Studies 2"),
        ("RBAC", "Role-Based Access Control"),
        ("STRIDE", "Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege"),
        ("TLS", "Transport Layer Security"),
        ("UI", "User Interface"),
        ("ZAP", "Zed Attack Proxy (OWASP)")
    ]
    
    for short, full in abbrevs:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(1); p.paragraph_format.space_after = Pt(1); p.paragraph_format.line_spacing = 1.15
        r1 = p.add_run(short)
        r1.font.name = 'Times New Roman'; r1.font.size = Pt(9.5); r1.bold = True; r1.font.color.rgb = NAVY_BLUE
        r2 = p.add_run(f"  —  {full}")
        r2.font.name = 'Times New Roman'; r2.font.size = Pt(9.5)
