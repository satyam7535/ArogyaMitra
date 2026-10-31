"""
ArogyaMitra — Report Front Matter Builder
Generates Cover Page, Bonafide Certificate, Undertaking, Conflict of Interest,
Acknowledgements, Abstract, Table of Contents, List of Figures, and List of Tables.
"""

from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from report_styles import add_p, add_h1, add_h2, add_caption, set_cell_margins, set_table_borders, NAVY_BLUE, SLATE_BLUE, MUTED_GREY, DARK_GREY

def add_cover_page(doc):
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_before = Pt(12)
    p_inst.paragraph_format.space_after = Pt(2)
    r = p_inst.add_run("INDIAN INSTITUTE OF INFORMATION TECHNOLOGY, PUNE")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(15)
    r.bold = True
    r.font.color.rgb = NAVY_BLUE
    
    p_dept = doc.add_paragraph()
    p_dept.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_dept.paragraph_format.space_after = Pt(36)
    r = p_dept.add_run("Department of Computer Science and Engineering")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12)
    r.bold = True
    r.font.color.rgb = SLATE_BLUE
    
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(24)
    p_title.paragraph_format.space_after = Pt(18)
    p_title.paragraph_format.line_spacing = 1.25
    r = p_title.add_run("ArogyaMitra: A Secure, Explainable, Fail-Closed AI-Assisted Primary-Healthcare Decision Support System")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(18)
    r.bold = True
    r.font.color.rgb = NAVY_BLUE
    
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(18)
    p_sub.paragraph_format.space_after = Pt(36)
    r = p_sub.add_run("A Project Report Submitted in Partial Fulfillment of the Requirements\nfor the Degree of Bachelor of Technology in Computer Science and Engineering")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(11.5)
    r.font.italic = True
    r.font.color.rgb = MUTED_GREY
    
    # Metadata Table
    table = doc.add_table(rows=2, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.columns[0].width = Inches(3.2)
    table.columns[1].width = Inches(3.2)
    
    # Student cell
    c0 = table.cell(0, 0)
    p0 = c0.paragraphs[0]
    p0.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p0.paragraph_format.line_spacing = 1.15
    r = p0.add_run("Submitted By:\n")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(11)
    r.bold = True
    r = p0.add_run("Satyam Keshari\n")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12)
    r.bold = True
    r = p0.add_run("MIS: 112315168\nB.Tech CSE (Semester VII)")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(11)
    
    # Supervisor cell
    c1 = table.cell(0, 1)
    p1 = c1.paragraphs[0]
    p1.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p1.paragraph_format.line_spacing = 1.15
    r = p1.add_run("Under the Guidance of:\n")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(11)
    r.bold = True
    r = p1.add_run("Dr. Ashish Singh\n")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12)
    r.bold = True
    r = p1.add_run("Assistant Professor\nDept. of Computer Science & Engineering")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(11)
    
    # Empty second row for spacing
    c2 = table.cell(1, 0)
    c3 = table.cell(1, 1)
    
    p_footer = doc.add_paragraph()
    p_footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_footer.paragraph_format.space_before = Pt(72)
    p_footer.paragraph_format.space_after = Pt(0)
    p_footer.paragraph_format.line_spacing = 1.15
    r = p_footer.add_run("Department of Computer Science and Engineering\nIndian Institute of Information Technology, Pune\nNovember 2026 (Academic Year 2026–2027)")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(11)
    r.bold = True
    r.font.color.rgb = DARK_GREY

def add_bonafide_certificate(doc):
    doc.add_page_break()
    p_h = doc.add_paragraph()
    p_h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_h.paragraph_format.space_before = Pt(18)
    p_h.paragraph_format.space_after = Pt(6)
    r = p_h.add_run("INDIAN INSTITUTE OF INFORMATION TECHNOLOGY, PUNE")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(14)
    r.bold = True
    r.font.color.rgb = NAVY_BLUE
    
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(24)
    r = p_sub.add_run("Department of Computer Science and Engineering")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12)
    r.bold = True
    
    p_cert = doc.add_paragraph()
    p_cert.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cert.paragraph_format.space_before = Pt(12)
    p_cert.paragraph_format.space_after = Pt(18)
    r = p_cert.add_run("BONAFIDE CERTIFICATE")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(15)
    r.bold = True
    r.underline = True
    r.font.color.rgb = NAVY_BLUE
    
    add_p(doc, "This is to certify that the project report entitled \"ArogyaMitra: A Secure, Explainable, Fail-Closed AI-Assisted Primary-Healthcare Decision Support System\" submitted by Satyam Keshari (MIS: 112315168) in partial fulfillment of the requirements for the award of the degree of Bachelor of Technology in Computer Science and Engineering at the Indian Institute of Information Technology, Pune, is a bonafide record of the work carried out by him under my supervision and guidance during the academic year 2026–2027.", space_before=12, space_after=12)
    
    add_p(doc, "The matter embodied in this report has not been submitted to any other University or Institute for the award of any degree or diploma. To the best of my knowledge and belief, the project adheres to all academic integrity, software safety, and institutional verification standards.", space_before=6, space_after=36)
    
    # Signature blocks
    table = doc.add_table(rows=1, cols=3)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.columns[0].width = Inches(2.2)
    table.columns[1].width = Inches(2.2)
    table.columns[2].width = Inches(2.2)
    
    # Col 0: Guide
    c0 = table.cell(0, 0)
    p0 = c0.paragraphs[0]
    p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p0.paragraph_format.line_spacing = 1.15
    r = p0.add_run("_____________________\n")
    r = p0.add_run("Dr. Ashish Singh\nProject Supervisor\nAssistant Professor, CSE\nIIIT Pune")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(10)
    
    # Col 1: HoD
    c1 = table.cell(0, 1)
    p1 = c1.paragraphs[0]
    p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p1.paragraph_format.line_spacing = 1.15
    r = p1.add_run("_____________________\n")
    r = p1.add_run("[CONFIRM HOD NAME]\nHead of Department\nDept. of CSE\nIIIT Pune")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(10)
    
    # Col 2: External
    c2 = table.cell(0, 2)
    p2 = c2.paragraphs[0]
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p2.paragraph_format.line_spacing = 1.15
    r = p2.add_run("_____________________\n")
    r = p2.add_run("External Examiner\nEvaluation Committee\nIIIT Pune")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(10)

def add_undertaking(doc):
    doc.add_page_break()
    p_cert = doc.add_paragraph()
    p_cert.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cert.paragraph_format.space_before = Pt(18)
    p_cert.paragraph_format.space_after = Pt(24)
    r = p_cert.add_run("DECLARATION & PLAGIARISM UNDERTAKING")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(14)
    r.bold = True
    r.underline = True
    r.font.color.rgb = NAVY_BLUE
    
    add_p(doc, "I, Satyam Keshari (MIS: 112315168), student of Bachelor of Technology in Computer Science and Engineering, Semester VII, Indian Institute of Information Technology, Pune, hereby declare that the work presented in this project report entitled \"ArogyaMitra: A Secure, Explainable, Fail-Closed AI-Assisted Primary-Healthcare Decision Support System\" is entirely my original research and engineering implementation carried out under the supervision of Dr. Ashish Singh.", space_before=12, space_after=12)
    
    add_p(doc, "I solemnly affirm that:", space_before=6, space_after=6, bold=True)
    add_p(doc, "1. This report does not contain any work or text copied from any other project, thesis, dissertation, journal article, or published material without formal citation and explicit attribution.", space_before=2, space_after=4)
    add_p(doc, "2. All software components, algorithmic pipelines, mathematical derivations, container definitions, and empirical validation suites described herein were engineered directly within the repository codebase.", space_before=2, space_after=4)
    add_p(doc, "3. All reported empirical metrics, including cross-validation accuracies, log-likelihood ratios, calibration errors, throughput measurements, and security scan outputs, correspond directly to verifiable execution logs in the repository evidence ledger (docs/evidence/). No figures have been fabricated, smoothed, or extrapolated.", space_before=2, space_after=4)
    add_p(doc, "4. Any generative AI tools utilized during system design or drafting were employed strictly in accordance with institutional guidelines for coding assistance and syntactic refactoring, with all intellectual architecture, analytical deductions, and system verification remaining my own.", space_before=2, space_after=18)
    
    p_sign = doc.add_paragraph()
    p_sign.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_sign.paragraph_format.space_before = Pt(36)
    p_sign.paragraph_format.line_spacing = 1.15
    r = p_sign.add_run("______________________________\n")
    r = p_sign.add_run("Satyam Keshari\n")
    r.bold = True
    r = p_sign.add_run("MIS: 112315168\nDepartment of CSE, IIIT Pune\nDate: November 01, 2026")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(11)

def add_conflict_of_interest(doc):
    doc.add_page_break()
    p_cert = doc.add_paragraph()
    p_cert.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cert.paragraph_format.space_before = Pt(18)
    p_cert.paragraph_format.space_after = Pt(24)
    r = p_cert.add_run("CONFLICT OF INTEREST STATEMENT")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(14)
    r.bold = True
    r.underline = True
    r.font.color.rgb = NAVY_BLUE
    
    add_p(doc, "The author declares that there are no financial, commercial, or personal conflicts of interest that could be perceived as improperly influencing or biasing the research, design, implementation, or empirical findings presented in this report.", space_before=12, space_after=12)
    add_p(doc, "The ArogyaMitra system was engineered strictly as an academic research and engineering prototype in primary-healthcare clinical decision support. No commercial sponsorship, hardware subsidy, or proprietary corporate data was accepted during the development of this project.", space_before=6, space_after=12)
    add_p(doc, "The machine learning models described herein were trained and benchmarked exclusively on synthetic clinical symptom datasets. The system has not been deployed on live human patients, has not accessed identifiable protected health information (PHI) of any living individual, and is not certified as a medical device by the Central Drugs Standard Control Organisation (CDSCO) or the United States Food and Drug Administration (FDA).", space_before=6, space_after=24)
    
    p_sign = doc.add_paragraph()
    p_sign.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_sign.paragraph_format.space_before = Pt(24)
    r = p_sign.add_run("Satyam Keshari\nMIS: 112315168")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(11)

def add_acknowledgements(doc):
    doc.add_page_break()
    p_cert = doc.add_paragraph()
    p_cert.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cert.paragraph_format.space_before = Pt(18)
    p_cert.paragraph_format.space_after = Pt(24)
    r = p_cert.add_run("ACKNOWLEDGEMENTS")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(14)
    r.bold = True
    r.underline = True
    r.font.color.rgb = NAVY_BLUE
    
    add_p(doc, "I express my deepest gratitude to my project supervisor, Dr. Ashish Singh, Assistant Professor, Department of Computer Science and Engineering, IIIT Pune, for his indispensable guidance, intellectual rigor, and constant encouragement throughout the design and realization of ArogyaMitra. His uncompromising insistence on empirical verification, probabilistic rigor, and fail-closed safety principles transformed this work from a conventional machine learning demonstration into an academically rigorous, multi-layered clinical decision support prototype.", space_before=12, space_after=12)
    
    add_p(doc, "I extend my sincere appreciation to the Head of Department, [CONFIRM HOD NAME], Department of Computer Science and Engineering, and Dr. [CONFIRM DIRECTOR NAME], Director, IIIT Pune, for providing the institutional infrastructure, computing facilities, and scholarly environment essential for completing this B.Tech capstone project.", space_before=6, space_after=12)
    
    add_p(doc, "I also thank the faculty members of the Department of Computer Science and Engineering for their insightful feedback during intermediate project reviews, which directly shaped our multi-tier microservice architecture, cryptographic isolation boundaries, and rigorous threat modeling methodology.", space_before=6, space_after=12)
    
    add_p(doc, "Finally, I owe an immeasurable debt of gratitude to my family and peers for their unwavering patience, support, and sacrifices during numerous late-night debugging and benchmarking sessions.", space_before=6, space_after=24)
    
    p_sign = doc.add_paragraph()
    p_sign.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r = p_sign.add_run("Satyam Keshari\nMIS: 112315168")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(11)

def add_abstract(doc):
    doc.add_page_break()
    p_cert = doc.add_paragraph()
    p_cert.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cert.paragraph_format.space_before = Pt(18)
    p_cert.paragraph_format.space_after = Pt(24)
    r = p_cert.add_run("ABSTRACT")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(14)
    r.bold = True
    r.underline = True
    r.font.color.rgb = NAVY_BLUE
    
    add_p(doc, "In primary healthcare settings across rural and semi-urban India, Accredited Social Health Activists (ASHAs) and community health workers operate at the frontlines of patient intake under severe resource constraints, high patient-to-physician ratios, and geographic isolation. While digital symptom checkers have emerged to assist frontline triage, recent clinical meta-analyses (notably Wallace et al., npj Digital Medicine 2022) demonstrate that commercial symptom checkers suffer from low diagnostic accuracy (19–37.9%) and align failure modes in a 'Swiss-cheese' configuration that poses catastrophic patient safety hazards. Furthermore, theoretical machine learning literature (Niculescu-Mizil & Caruana, ICML 2005) proves that common classifiers, particularly Naive Bayes, produce severely distorted, overconfident posterior estimates due to feature independence assumptions, while post-hoc calibration methods like Platt scaling overfit and degrade on scarce clinical data.", space_before=12, space_after=10)
    
    add_p(doc, "To address these systemic vulnerabilities, this project presents ArogyaMitra, a secure, explainable, fail-closed AI-assisted primary-healthcare decision support system prototype. ArogyaMitra is architected around four core engineering pillars: (1) an explainable, stateless Bernoulli Naive Bayes classification engine operating across 41 disease classes and 131 symptoms, accompanied by machine-precision additive log-odds feature attributions; (2) a deterministic, rule-based clinical red-flag screening layer that irrevocably overrides machine learning predictions whenever life-threatening symptoms are detected; (3) a multi-tier Large Language Model (LLM) narrative layer utilizing Google Gemini with ordered model fallbacks, hard time caps (10s per-attempt, 20s total cap), and whole-phrase confidence filtering backed by pre-compiled clinical templates; and (4) an audited, defense-in-depth security infrastructure enforcing mutual container isolation, TLS 1.3 encryption, Argon2id credential hashing, field-level AES-256-GCM data encryption, and optimistic concurrency controls.", space_before=6, space_after=10)
    
    add_p(doc, "Empirical evaluation on a rigorously deduplicated benchmark (304 unique rows from 4,920 raw records, eliminating a 93.8% synthetic duplication artifact) via 5x3 repeated stratified k-fold cross-validation demonstrates BernoulliNB outperforming tuned tree ensembles under symptom dropout: achieving 1.000 ± 0.000 at 0% dropout, 0.989 ± 0.014 at 30% dropout, and 0.919 ± 0.023 at 50% dropout, compared to Tuned LightGBM (0.989, 0.864, 0.683) and Tuned XGBoost (0.984, 0.868, 0.720). Load testing across 2,400 standardized requests established system throughput reaching 14.7 req/s under 50 concurrent users with zero unhandled exceptions, while database index projection reduced worker consultation list latency by 60.5% (p50: 193.0 ms to 76.2 ms). The entire prototype is validated across 321 automated tests, 20 golden clinical cases, 11 end-to-end Playwright journeys, and zero unfixed High-severity container vulnerabilities, providing a transparent, verifiable architectural blueprint for safe, AI-assisted primary healthcare triage.", space_before=6, space_after=16)
    
    p_kw = doc.add_paragraph()
    p_kw.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r_kwh = p_kw.add_run("Keywords: ")
    r_kwh.font.name = 'Times New Roman'
    r_kwh.font.size = Pt(11)
    r_kwh.bold = True
    r_kwt = p_kw.add_run("Clinical Decision Support Systems, Primary Healthcare Triage, Bernoulli Naive Bayes, Probabilistic Calibration, Fail-Closed Architecture, Large Language Models, Defense-in-Depth Security, Rural Telemedicine.")
    r_kwt.font.name = 'Times New Roman'
    r_kwt.font.size = Pt(11)
    r_kwt.font.italic = True

def add_table_of_contents_pages(doc):
    doc.add_page_break()
    p_h = doc.add_paragraph()
    p_h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_h.paragraph_format.space_before = Pt(18)
    p_h.paragraph_format.space_after = Pt(20)
    r = p_h.add_run("TABLE OF CONTENTS")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(15)
    r.bold = True
    r.underline = True
    r.font.color.rgb = NAVY_BLUE
    
    toc_items = [
        ("Bonafide Certificate", "ii"),
        ("Declaration & Plagiarism Undertaking", "iii"),
        ("Conflict of Interest Statement", "iv"),
        ("Acknowledgements", "v"),
        ("Abstract", "vi"),
        ("List of Figures", "ix"),
        ("List of Tables", "xi"),
        ("List of Abbreviations", "xii"),
        ("Chapter 1: Introduction & Literature Review", "1"),
        ("    1.1 Motivation & Primary Healthcare Challenges in Rural India", "1"),
        ("    1.2 Comprehensive Literature Review", "3"),
        ("        1.2.1 Review of Symptom Checkers, Clinical Decision Support Systems, and Calibration in Medicine", "3"),
        ("        1.2.2 Comparison with Existing Work", "8"),
        ("    1.3 Problem Statement & Design Objectives", "10"),
        ("    1.4 Faculty Guidance & Architectural Evolution", "12"),
        ("    1.5 Report Outline & Organization", "14"),
        ("Chapter 2: System Requirements & Threat Modeling", "15"),
        ("    2.1 Functional Requirements (FR-1 to FR-10)", "15"),
        ("    2.2 Non-Functional Requirements (NFR-1 to NFR-8)", "18"),
        ("    2.3 Threat Model & Security Analysis (STRIDE Matrix)", "20"),
        ("    2.4 Clinical Safety & Ethics Requirements", "23"),
        ("Chapter 3: System Architecture & Design", "25"),
        ("    3.1 Architectural Overview & Container Topology", "25"),
        ("    3.2 Machine Learning Inference & Calibration Engine", "28"),
        ("        3.2.1 Bernoulli Naive Bayes Mathematical Formulation", "28"),
        ("        3.2.2 Feature Engineering & Vocabulary Alignment", "30"),
        ("        3.2.3 Explainability via Top-Feature Attribution", "31"),
        ("        3.2.4 Calibration Theoretical Background & Analysis", "33"),
        ("        3.2.5 Comparative Model Selection", "35"),
        ("    3.3 Rule-Based Clinical Red-Flag Override System", "37"),
        ("    3.4 Multi-Tier LLM Explanation & Resilient Fallback Layer", "39"),
        ("    3.5 End-to-End Clinical Consultation Workflow", "42"),
        ("    3.6 Security Architecture & Cryptographic Implementation", "45"),
        ("    3.7 Database Design, Concurrency & Data Integrity", "48"),
        ("Chapter 4: Empirical Evaluation & Experimental Results", "51"),
        ("    4.1 Dataset Profile & Methodological Integrity", "51"),
        ("    4.2 Machine Learning Performance & Robustness", "53"),
        ("    4.3 Load Testing, Concurrency & System Throughput", "57"),
        ("    4.4 Automated Testing & Verification Suite", "61"),
        ("    4.5 Security Vulnerability & Dependency Auditing", "64"),
        ("    4.6 Literature-Linked Discussion & Analysis", "66"),
        ("    4.7 Limitations & Threats to Validity", "68"),
        ("Chapter 5: Conclusion & Future Scope", "70"),
        ("    5.1 Project Summary & Achievements", "70"),
        ("    5.2 Lessons Learned & Engineering Insights", "71"),
        ("    5.3 Future Work & Roadmap", "72"),
        ("References", "74"),
        ("Appendix A: Engineering Challenges, Root Causes, and Architectural Remediation Fixes", "77"),
        ("Appendix B: Reproduction Commands & Verification Playbook", "83"),
        ("Appendix C: Complete Prototype Test Suite Inventory", "86"),
    ]
    
    for title, page in toc_items:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.15
        
        # Determine bolding for chapter level
        is_major = not title.startswith("    ") and not title.startswith("        ")
        r1 = p.add_run(title)
        r1.font.name = 'Times New Roman'
        r1.font.size = Pt(10.5 if not is_major else 11)
        r1.bold = is_major
        if is_major and "Chapter" in title:
            r1.font.color.rgb = NAVY_BLUE
            
        # Leader dots
        num_dots = max(5, 75 - len(title))
        dots_str = " " + ". " * (num_dots // 2) + " "
        r2 = p.add_run(dots_str)
        r2.font.name = 'Times New Roman'
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = MUTED_GREY
        
        r3 = p.add_run(page)
        r3.font.name = 'Times New Roman'
        r3.font.size = Pt(10.5 if not is_major else 11)
        r3.bold = is_major

def add_list_of_figures_and_tables(doc):
    doc.add_page_break()
    p_h = doc.add_paragraph()
    p_h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_h.paragraph_format.space_before = Pt(18)
    p_h.paragraph_format.space_after = Pt(16)
    r = p_h.add_run("LIST OF FIGURES")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(14)
    r.bold = True
    r.underline = True
    r.font.color.rgb = NAVY_BLUE
    
    figures = [
        ("Figure 3.1", "Microservice Container Topology & Trust Boundaries", "26"),
        ("Figure 3.2", "Docker Bridge Network Isolation & Persistent Volumes", "27"),
        ("Figure 3.3", "Hierarchical LLM Request Timeout Cascade & Guardrail Budgets", "40"),
        ("Figure 3.4", "End-to-End Clinical Consultation Sequence Workflow", "43"),
        ("Figure 3.5", "Consultation Lifecycle State Machine & Decision Gate B", "44"),
        ("Figure 3.6", "Five-Layer Defense-in-Depth Security Architecture", "46"),
        ("Figure 3.7", "Packet Interception Analysis: Cleartext HTTP vs Encrypted TLS 1.3", "47"),
        ("Figure 4.1", "Dataset Profile: Raw Kaggle Duplication vs Deduplicated Cohort", "52"),
        ("Figure 4.2", "Classification Accuracy Across Symptom Dropout Rates (0%, 30%, 50%)", "54"),
        ("Figure 4.3", "Expected Calibration Error (ECE) Across Dropout Rates", "56"),
        ("Figure 4.4", "Load Test Throughput & Latency Distributions (C=1, 10, 50)", "58"),
        ("Figure 4.5", "Worker List Latency Before vs After Index Projection Optimization", "60"),
        ("Figure 4.6", "Test Suite Distribution Across Prototype Architectural Layers (321 Tests)", "61"),
        ("Figure 4.7", "User Interface: Primary Health Worker Consultation Intake & Accept Journey", "62"),
        ("Figure 4.8", "User Interface: Red-Flag Emergency Detection & Blocked Direct Triage", "63"),
        ("Figure 4.9", "User Interface: Server-Side Consultation Pagination & Historical Record Review", "63"),
        ("Figure 4.10", "User Interface: Fail-Closed Resilient Error State on ML Service Outage", "64"),
    ]
    
    for f_id, f_desc, f_page in figures:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.15
        
        r1 = p.add_run(f"{f_id}: {f_desc}")
        r1.font.name = 'Times New Roman'
        r1.font.size = Pt(10)
        
        num_dots = max(5, 78 - len(f"{f_id}: {f_desc}"))
        dots_str = " " + ". " * (num_dots // 2) + " "
        r2 = p.add_run(dots_str)
        r2.font.name = 'Times New Roman'
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = MUTED_GREY
        
        r3 = p.add_run(f_page)
        r3.font.name = 'Times New Roman'
        r3.font.size = Pt(10)
        r3.bold = True
        
    doc.add_page_break()
    p_h2 = doc.add_paragraph()
    p_h2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_h2.paragraph_format.space_before = Pt(18)
    p_h2.paragraph_format.space_after = Pt(16)
    r = p_h2.add_run("LIST OF TABLES")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(14)
    r.bold = True
    r.underline = True
    r.font.color.rgb = NAVY_BLUE
    
    tables = [
        ("Table 1.1", "Comprehensive Literature Review Summary Matrix", "5"),
        ("Table 1.2", "Systematic Comparison: Clinical Concerns vs ArogyaMitra Implementations", "9"),
        ("Table 2.1", "System Functional Requirements Specification (FR-1 to FR-10)", "16"),
        ("Table 2.2", "System Non-Functional Requirements Specification (NFR-1 to NFR-8)", "19"),
        ("Table 2.3", "STRIDE Threat Model & Architectural Security Controls", "21"),
        ("Table 3.1", "Rule-Based Emergency Red-Flag Trigger Conditions (DRAFT Status)", "38"),
        ("Table 4.1", "Stratified Repeated Cross-Validation Performance Across Dropout Levels", "54"),
        ("Table 4.2", "Expected Calibration Error (ECE) and Probabilistic Evaluation", "56"),
        ("Table 4.3", "Comprehensive Multi-Tier Load Test Performance (2,400 Requests)", "58"),
        ("Table 4.4", "Worker Consultation List Endpoint Profiling: Full Scan vs Pagination", "60"),
        ("Table 4.5", "Automated Prototype Test Suite Breakdown Across Services", "62"),
        ("Table 4.6", "OWASP ZAP Dynamic Security Baseline Scan Dispositions", "65"),
        ("Table A.1", "Engineering Challenges, Root Causes, and Architectural Remediation Fixes", "78"),
        ("Table C.1", "Detailed Inventory of 321 Prototype Automated Test Cases", "87"),
    ]
    
    for t_id, t_desc, t_page in tables:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.15
        
        r1 = p.add_run(f"{t_id}: {t_desc}")
        r1.font.name = 'Times New Roman'
        r1.font.size = Pt(10)
        
        num_dots = max(5, 78 - len(f"{t_id}: {t_desc}"))
        dots_str = " " + ". " * (num_dots // 2) + " "
        r2 = p.add_run(dots_str)
        r2.font.name = 'Times New Roman'
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = MUTED_GREY
        
        r3 = p.add_run(t_page)
        r3.font.name = 'Times New Roman'
        r3.font.size = Pt(10)
        r3.bold = True
