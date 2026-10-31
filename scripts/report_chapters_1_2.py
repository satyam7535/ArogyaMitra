"""
ArogyaMitra — Report Chapters 1 & 2 Builder (Item 1, 9, 14, 16, 17, 18, 19 Compliant)
Builds Chapter 1 (Introduction & Literature Review) and Chapter 2 (Requirements & Threat Modeling).
"""

from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from report_styles import (
    add_p, add_h1, add_h2, add_h3, add_table_caption, add_callout,
    set_cell_margins, set_cell_shading, set_table_borders,
    NAVY_BLUE, MUTED_GREY, DARK_GREY
)
from report_data import LITERATURE_SUMMARY, COMPARISON_WITH_EXISTING_WORK

def add_chapter_1(doc):
    add_h1(doc, "Chapter 1: Introduction & Literature Review", page_break=False)
    
    add_h2(doc, "1.1 Motivation & Primary Healthcare Challenges in Rural India")
    add_p(doc, "In developing healthcare systems with wide geographic dispersion, delivering consistent primary healthcare remains a fundamental public health challenge. In India, the primary healthcare pyramid relies heavily on community-level frontline workers, primarily Accredited Social Health Activists (ASHAs) and Auxiliary Nurse Midwives (ANMs) stationed across Health and Wellness Centres (HWCs) and Sub-Centres. These frontline workers operate under severe operational constraints: high patient-to-physician ratios that frequently exceed 1:10,000 in rural districts, rudimentary diagnostic infrastructure, and significant travel distances separating peripheral villages from referral hospitals.")
    
    add_p(doc, "When rural patients present with acute symptoms, the frontline health worker must make high-stakes triage decisions: determining whether an individual can be safely managed with supportive care, requires scheduled primary health centre (PHC) physician evaluation, or demands immediate emergency transfer to a district hospital. Errors in this triage process carry severe clinical consequences. Under-triage of acute conditions—such as myocardial infarction presenting as epigastric discomfort—leads to preventable mortality. Conversely, systematic over-triage congests secondary and tertiary facilities, imposing travel and consultation costs on rural households.")
    
    add_p(doc, "While digital health initiatives under the Ayushman Bharat Digital Mission (ABDM) have expanded electronic health record adoption, decision support tools for community health workers remain limited. Commercial symptom checkers and diagnostic mobile applications often fail in this operating environment. They are typically engineered as consumer tools that require continuous broadband connectivity, provide no interpretable clinical rationales, and lack fail-closed safety designs. When an underlying algorithmic service experiences network timeout or server failure, such systems frequently crash or return empty screens, leaving frontline workers without guidance.")
    
    add_p(doc, "In this project, I address these challenges by engineering ArogyaMitra, a secure, explainable, and fail-closed AI-assisted clinical decision support system prototype tailored for community healthcare workers. The system does not attempt to replace physician diagnosis. Instead, it serves as an assistive screening aid that provides differential disease estimation, enforces deterministic safety overrides for emergencies, operates with bounded latency, and protects patient privacy through containerized security.")

    # Primer Box for ECE Evaluator (Item 17)
    primer_text = (
        "1. Bernoulli Naive Bayes Classifier: Treats each presenting symptom as a binary indicator variable (present or absent) "
        "across 131 clinical features and 41 disease classes. By assuming conditional independence among symptoms given the disease, "
        "the model computes log-posterior class scores by summing log-likelihood ratios. This avoids matrix inversions and yields "
        "inference times of approximately 1.8 ms on commodity CPUs.\n\n"
        "2. Probabilistic Calibration: In statistical learning, a classifier is well-calibrated if a predicted score of 0.8 corresponds "
        "to an empirical 80% event frequency. Naive Bayes violates this condition because multiplying correlated symptom likelihoods "
        "artificially inflates the posterior odds, pushing scores toward 0 and 1. Post-hoc calibration methods (such as Platt scaling) "
        "can overfit on scarce clinical datasets; in my experiments on 304 unique rows, Platt scaling worsened log loss from 0.0061 to 0.1643. "
        "Consequently, ArogyaMitra explicitly displays scores as uncalibrated estimates.\n\n"
        "3. Deterministic Red-Flag Triage Layer: Because statistical classifiers can err when presented with rare or atypical symptom combinations, "
        "ArogyaMitra decouples emergency detection from machine learning. A deterministic rule engine scans for life-threatening symptoms "
        "(e.g., chest pain, coma, breathlessness) before the model runs. If triggered, it immediately locks the triage output to EMERGENCY, "
        "preventing model misclassification from causing clinical under-triage."
    )
    add_callout(doc, primer_text, "Primer for Evaluation: Naive Bayes, Probabilistic Calibration, and Clinical Triage")

    add_h2(doc, "1.2 Comprehensive Literature Review")
    add_h3(doc, "1.2.1 Review of Symptom Checkers, Decision Support, and Calibration")
    add_p(doc, "The academic literature evaluating algorithmic decision support and symptom checking tools reveals important discrepancies between theoretical predictive accuracy and clinical safety. A systematic review by Wallace et al. (2022) [1] analyzed 10 studies evaluating 48 digital symptom checkers using the Quality Assessment of Diagnostic Accuracy Studies (QUADAS-2) methodology. Their key findings include:")
    
    add_p(doc, "1. Diagnostic Accuracy: Across evaluated platforms, primary diagnostic accuracy was low, ranging between 19.0% and 37.9%. Even when evaluating top-3 or top-5 differential accuracy, symptom checkers showed limited precision compared to practicing general practitioners.", space_after=3)
    add_p(doc, "2. Triage Accuracy: Triage decision accuracy (determining urgency) ranged from 48.8% to 90.1%, but exhibited wide variation across different commercial checkers evaluating identical clinical vignettes.", space_after=3)
    add_p(doc, "3. Safety Hazards and Swiss-Cheese Failure Model: Wallace et al. noted that symptom checkers present patient safety hazards when errors align across stages—such as an incorrect primary diagnosis cascading into an inappropriately delayed triage recommendation.", space_after=3)
    add_p(doc, "4. Need for Independent Evaluation: The authors concluded that digital symptom checkers require independent clinical validation on real-world data and formal medical device regulation before deployment in public healthcare.", space_after=8)

    add_p(doc, "Complementing clinical triage evaluations, the theoretical behavior of probabilistic classifier calibration was investigated by Niculescu-Mizil & Caruana (2005) [2] across 10 supervised learning families. They showed that:")
    
    add_p(doc, "1. Distortion in Naive Bayes Estimators: Naive Bayes pushes predicted probabilities toward 0 and 1 because its conditional independence assumption multiplies marginal likelihoods, causing redundant evidence to inflate posterior log-odds.", space_after=3)
    add_p(doc, "2. Data Scarcity and Isotonic Regression: The authors demonstrated that non-parametric calibration (Isotonic regression) requires substantial validation data and performs worse than parametric Platt scaling when data is scarce.", space_after=8)

    add_p(doc, "Table 1.1 summarizes six seminal contributions across clinical symptom checking, Bayesian classification, interpretability, and natural language generation that directly informed the design of ArogyaMitra.")

    # Table 1.1 (6 rows, Item 18)
    add_table_caption(doc, "Table 1.1: Comprehensive Literature Review Summary Matrix")
    t11 = doc.add_table(rows=len(LITERATURE_SUMMARY)+1, cols=4)
    t11.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t11)
    col_widths = [Inches(1.4), Inches(1.1), Inches(2.3), Inches(2.2)]
    
    headers = ["Author & Ref", "Venue", "Methodological Summary", "Relevance to ArogyaMitra"]
    for j, h in enumerate(headers):
        cell = t11.cell(0, j); cell.width = col_widths[j]
        set_cell_shading(cell, "154360"); set_cell_margins(cell, top=80, bottom=80, left=80, right=80)
        p = cell.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h); r.font.name = 'Times New Roman'; r.font.size = Pt(9); r.bold = True; r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        
    for i, row in enumerate(LITERATURE_SUMMARY):
        row_cells = t11.rows[i+1].cells
        for j, w in enumerate(col_widths):
            row_cells[j].width = w; set_cell_margins(row_cells[j], top=60, bottom=60, left=70, right=70)
            if i % 2 == 1: set_cell_shading(row_cells[j], "F4F6F7")
        
        p0 = row_cells[0].paragraphs[0]; r = p0.add_run(f"{row['author']} {row['cite_num']}"); r.font.name = 'Times New Roman'; r.font.size = Pt(8.5); r.bold = True
        p1 = row_cells[1].paragraphs[0]; r = p1.add_run(row["venue"]); r.font.name = 'Times New Roman'; r.font.size = Pt(8.5); r.italic = True
        p2 = row_cells[2].paragraphs[0]; r = p2.add_run(row["method"]); r.font.name = 'Times New Roman'; r.font.size = Pt(8)
        p3 = row_cells[3].paragraphs[0]; r = p3.add_run(row["relevance"]); r.font.name = 'Times New Roman'; r.font.size = Pt(8)

    add_h3(doc, "1.2.2 Comparison with Existing Work")
    add_p(doc, "To clarify the technical positioning and safety boundaries of ArogyaMitra, Table 1.2 contrasts specific clinical concerns documented in literature against conventional symptom checkers and the verifiable implementations within this repository.")

    add_table_caption(doc, "Table 1.2: Systematic Comparison: Clinical Concerns vs. ArogyaMitra Implementations")
    t12 = doc.add_table(rows=len(COMPARISON_WITH_EXISTING_WORK)+1, cols=4)
    t12.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t12)
    cw12 = [Inches(1.8), Inches(1.2), Inches(2.3), Inches(1.7)]
    
    h12 = ["Clinical / Technical Concern", "Literature Citation", "ArogyaMitra Implementation", "Unvalidated Boundary"]
    for j, h in enumerate(h12):
        cell = t12.cell(0, j); cell.width = cw12[j]
        set_cell_shading(cell, "1B4F72"); set_cell_margins(cell, top=80, bottom=80, left=80, right=80)
        p = cell.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h); r.font.name = 'Times New Roman'; r.font.size = Pt(9); r.bold = True; r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        
    for i, row in enumerate(COMPARISON_WITH_EXISTING_WORK):
        row_cells = t12.rows[i+1].cells
        for j, w in enumerate(cw12):
            row_cells[j].width = w; set_cell_margins(row_cells[j], top=60, bottom=60, left=70, right=70)
            if i % 2 == 1: set_cell_shading(row_cells[j], "F4F6F7")
        
        p0 = row_cells[0].paragraphs[0]; r = p0.add_run(row["concern"]); r.font.name = 'Times New Roman'; r.font.size = Pt(8); r.bold = True
        p1 = row_cells[1].paragraphs[0]; r = p1.add_run(row["source"]); r.font.name = 'Times New Roman'; r.font.size = Pt(8); r.italic = True
        p2 = row_cells[2].paragraphs[0]; r = p2.add_run(row["response"]); r.font.name = 'Times New Roman'; r.font.size = Pt(8)
        p3 = row_cells[3].paragraphs[0]; r = p3.add_run(row["unvalidated"]); r.font.name = 'Times New Roman'; r.font.size = Pt(7.5); r.font.color.rgb = RGBColor(0xB7, 0x1C, 0x1C)

    add_h2(doc, "1.3 Problem Statement & Design Objectives")
    add_p(doc, "Problem Statement: Community health workers in primary healthcare settings require an auditable, privacy-preserving, and fail-closed decision support tool to triage acute presentations without relying on black-box predictions, ungrounded generative text, or unvetted cloud infrastructure.")
    
    add_p(doc, "To address this problem, I engineered ArogyaMitra according to five design objectives:", bold=True)
    add_p(doc, "1. Objective 1 — Probabilistic Explainability: Deploy an inference engine where every differential disease score is mathematically traceable to specific symptom attributions, avoiding black-box models.", space_after=3)
    add_p(doc, "2. Objective 2 — Deterministic Red-Flag Override: Ensure that clinical red-flag symptoms (e.g., chest pain, acute dyspnea, coma) immediately trigger emergency triage, superseding statistical model predictions.", space_after=3)
    add_p(doc, "3. Objective 3 — Guarded LLM Narrative Generation: Confine the Large Language Model strictly to formatting summaries, enforcing a 10s per-attempt timeout and a 20s overall cap backed by deterministic medical templates.", space_after=3)
    add_p(doc, "4. Objective 4 — Fail-Closed System Behavior: In the event of microservice failure or database unreachability, the system must not output mock predictions; it must reject unsafe operations and return explicit HTTP 503 error states.", space_after=3)
    add_p(doc, "5. Objective 5 — Layered Data Security: Implement cryptographic protections across trust boundaries, including field-level AES-256-GCM encryption, Argon2id credential hashing, and container network isolation.", space_after=8)

    add_h2(doc, "1.4 Design Evolution")
    add_p(doc, "The architecture of ArogyaMitra evolved through several engineering iterations as testing revealed limitations in earlier designs. In early versions, the system was structured as a conventional web prototype: a monolithic script exposing a tree-based classifier, an unconstrained generative LLM prompt, and default web application security. Through systematic auditing and benchmarking, I identified several vulnerabilities and made the following design decisions:")
    
    add_p(doc, "1. Rejection of Spurious Model Calibration Claims: When initial tests attempted post-hoc Platt scaling on the dataset, empirical evaluation revealed that fitting a Platt sigmoid on the 304 unique rows degraded log loss from 0.0061 to 0.1643. I determined that fitting parametric sigmoids on scarce class samples introduces boundary distortion. I removed claims of calibrated probabilities and updated the user interface to explicitly state that scores represent uncalibrated posterior estimates from Bernoulli Naive Bayes.", space_after=4)
    
    add_p(doc, "2. Transition from Mock Fallbacks to Fail-Closed Design: Early prototypes included client-side mock fallbacks that returned simulated predictions when backend services were offline. Recognizing that returning canned predictions during an outage creates patient safety hazards, I redesigned the system to be fail-closed: removing all client mocks and ensuring that service outages return an explicit HTTP 503 MODEL_UNAVAILABLE error with clear instructions to seek emergency care.", space_after=4)
    
    add_p(doc, "3. Derivation of Exact Log-Odds Over Sampling Surrogates: Initial experiments with local perturbation surrogates (such as LIME) showed sampling variance and high latency. To achieve fast, deterministic explanations, I derived closed-form Bayesian log-odds attributions directly from the Bernoulli parameter matrix, achieving exact additive feature attributions without sampling overhead.", space_after=4)
    
    add_p(doc, "4. Container Decoupling and Secret Hardening: Static analysis detected fallback encryption keys embedded in source files. I refactored the system into isolated Docker microservices connected over a private bridge network, added environment variable enforcement, and wrote an automated production-guard test verifying that missing encryption keys halt execution immediately.", space_after=8)

    add_h2(doc, "1.5 Report Outline & Organization")
    add_p(doc, "The remainder of this report is organized as follows: Chapter 2 specifies the functional, non-functional, and STRIDE threat modeling requirements. Chapter 3 provides the system architecture, mathematical formulation of Bernoulli Naive Bayes, red-flag screening rules, guarded LLM timeout cascades, cryptographic implementations, and concurrency controls. Chapter 4 presents empirical evaluations, including nested cross-validation across symptom dropout levels, load testing, automated test suite verification, and literature-linked discussion. Chapter 5 concludes the report and discusses future work. Engineering challenges and CLI reproduction playbooks are provided in Appendices A and B.")

def add_chapter_2(doc):
    add_h1(doc, "Chapter 2: System Requirements & Threat Modeling")
    
    add_h2(doc, "2.1 Functional Requirements")
    add_p(doc, "ArogyaMitra governs clinical triage interactions across frontline community health workers, physicians, and administrative auditors. Table 2.1 specifies the ten functional requirements (FR-1 through FR-10) implemented across the microservice stack.")

    add_table_caption(doc, "Table 2.1: System Functional Requirements Specification (FR-1 to FR-10)")
    fr_data = [
        ("FR-1", "Consultation Intake", "Capture basic demographics and chief complaints, validating inputs against Pydantic schemas."),
        ("FR-2", "Vocabulary Mapping", "Convert symptom selections from a 131-symptom vocabulary into binary indicator vectors."),
        ("FR-3", "Red-Flag Screening", "Scan symptom inputs against 7 emergency symptoms; immediately assign Emergency triage on match."),
        ("FR-4", "Bayesian Inference", "Compute uncalibrated posterior log-odds across 41 disease classes and return top-3 ranked differentials."),
        ("FR-5", "Feature Attribution", "Calculate exact positive and negative log-likelihood contributions for each presenting symptom."),
        ("FR-6", "Guarded LLM Summary", "Generate clinical summaries via Gemini API subject to strict confidence-word filtering."),
        ("FR-7", "Template Fallback", "Engage deterministic pre-compiled templates on LLM timeout (10s/20s) or 429 quota exhaustion."),
        ("FR-8", "Worker Decision Gate", "Provide an explicit Accept / Escalate decision interface for health worker review."),
        ("FR-9", "Consultation Pagination", "Support indexed server-side pagination (limit, page) and lean projection on GET /consultation/my."),
        ("FR-10", "DPDP-aware Retention", "Support patient consent recording, consent withdrawal, and administrator-approved anonymization.")
    ]
    
    t21 = doc.add_table(rows=len(fr_data)+1, cols=3)
    t21.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t21)
    cw21 = [Inches(0.9), Inches(1.8), Inches(4.3)]
    
    h21 = ["Req ID", "Requirement Title", "Technical Scope"]
    for j, h in enumerate(h21):
        cell = t21.cell(0, j); cell.width = cw21[j]
        set_cell_shading(cell, "154360"); set_cell_margins(cell, top=70, bottom=70, left=70, right=70)
        p = cell.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h); r.font.name = 'Times New Roman'; r.font.size = Pt(8.5); r.bold = True; r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        
    for i, (rid, rtitle, rdesc) in enumerate(fr_data):
        row_cells = t21.rows[i+1].cells
        for j, w in enumerate(cw21):
            row_cells[j].width = w; set_cell_margins(row_cells[j], top=50, bottom=50, left=60, right=60)
            if i % 2 == 1: set_cell_shading(row_cells[j], "F4F6F7")
        
        p0 = row_cells[0].paragraphs[0]; r = p0.add_run(rid); r.font.name = 'Times New Roman'; r.font.size = Pt(8); r.bold = True
        p1 = row_cells[1].paragraphs[0]; r = p1.add_run(rtitle); r.font.name = 'Times New Roman'; r.font.size = Pt(8); r.bold = True
        p2 = row_cells[2].paragraphs[0]; r = p2.add_run(rdesc); r.font.name = 'Times New Roman'; r.font.size = Pt(8)

    add_h2(doc, "2.2 Non-Functional Requirements: Targets vs. Measured Results")
    add_p(doc, "Table 2.2 defines eight non-functional requirements presented as engineering targets alongside their measured evaluation outcomes.")

    add_table_caption(doc, "Table 2.2: System Non-Functional Requirements: Targets vs. Measured Results")
    nfr_data = [
        ("NFR-1", "Gateway Latency", "<= 1,500 ms at p95 under load", "PASS at C=1 (190.6 ms); FAIL at C=10 (1952.3 ms) and C=50 (5862.8 ms) under local virtualized load."),
        ("NFR-2", "ML Micro-Latency", "<= 50 ms inference per query", "PASS. Measured 1.8 ms in internal container benchmark via vectorized NumPy log-odds."),
        ("NFR-3", "Fail-Closed Outage", "Return HTTP 503 on service down", "PASS. Verified by test suite (test_phase0.py); rejects requests when ML container is offline."),
        ("NFR-4", "Data Encryption", "AES-256-GCM field encryption", "PASS. Verified by automated tests; unique 96-bit IV per record; process exits if key is missing."),
        ("NFR-5", "Password Security", "Argon2id credential hashing", "PASS. Enforced in auth service (3 iterations, 64 MB RAM, 4 parallelism threads)."),
        ("NFR-6", "State Concurrency", "Prevent lost concurrent writes", "PASS. Enforced via Mongoose version key (__v) and conditional atomic updates."),
        ("NFR-7", "Transport Security", "TLS 1.2 / TLS 1.3 encryption", "PASS. Nginx enforces ssl_protocols TLSv1.2 TLSv1.3 with HSTS and nosniff headers."),
        ("NFR-8", "Container Isolation", "Isolated Docker private bridge", "PASS. Services run on private bridge arogya-net; MongoDB exposes no public host port.")
    ]
    
    t22 = doc.add_table(rows=len(nfr_data)+1, cols=4)
    t22.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t22)
    cw22 = [Inches(0.9), Inches(1.6), Inches(1.8), Inches(2.7)]
    
    h22 = ["Req ID", "Dimension", "Target Specification", "Measured Outcome & Pass/Fail Status"]
    for j, h in enumerate(h22):
        cell = t22.cell(0, j); cell.width = cw22[j]
        set_cell_shading(cell, "1B4F72"); set_cell_margins(cell, top=70, bottom=70, left=70, right=70)
        p = cell.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h); r.font.name = 'Times New Roman'; r.font.size = Pt(8.5); r.bold = True; r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        
    for i, (rid, rdim, rtgt, rout) in enumerate(nfr_data):
        row_cells = t22.rows[i+1].cells
        for j, w in enumerate(cw22):
            row_cells[j].width = w; set_cell_margins(row_cells[j], top=50, bottom=50, left=60, right=60)
            if i % 2 == 1: set_cell_shading(row_cells[j], "F4F6F7")
        
        p0 = row_cells[0].paragraphs[0]; r = p0.add_run(rid); r.font.name = 'Times New Roman'; r.font.size = Pt(8); r.bold = True
        p1 = row_cells[1].paragraphs[0]; r = p1.add_run(rdim); r.font.name = 'Times New Roman'; r.font.size = Pt(8); r.bold = True
        p2 = row_cells[2].paragraphs[0]; r = p2.add_run(rtgt); r.font.name = 'Times New Roman'; r.font.size = Pt(8)
        p3 = row_cells[3].paragraphs[0]; r = p3.add_run(rout); r.font.name = 'Times New Roman'; r.font.size = Pt(8)
        if "FAIL" in rout: r.font.color.rgb = RGBColor(0xB7, 0x1C, 0x1C)

    add_h2(doc, "2.3 Threat Model & Security Analysis (STRIDE Matrix)")
    add_p(doc, "To identify potential attack surfaces, I conducted a STRIDE threat modeling analysis across system trust boundaries. Table 2.3 summarizes the identified threat scenarios and implemented countermeasures.")

    add_table_caption(doc, "Table 2.3: STRIDE Threat Model and Architectural Security Controls")
    stride_data = [
        ("Spoofing", "Adversary forges credentials or intercepts session tokens to submit false triage data.", "Short-lived signed JWTs (15-min expiry) with HMAC-SHA256 and Argon2id hashing."),
        ("Tampering", "Adversary modifies triage urgency scores or alters symptom vectors in transit.", "Enforced TLS 1.2/1.3 encryption across external gateways; internal Docker network isolation."),
        ("Repudiation", "Health worker denies recording a triage decision or clinician denies failing to review.", "Structured MongoDB audit logs recording timestamps, user IDs, roles, and client IPs."),
        ("Info Disclosure", "Eavesdropper accesses patient PII or clinical records through database dumps.", "Field-level AES-256-GCM encryption for patient PII; PII scrubbing before LLM input."),
        ("Denial of Service", "Adversary floods triage endpoints with requests, exhausting CPU or Gemini quota.", "Rate limiting (100 req/15 min on API routes); 20s LLM hard cap with template fallback."),
        ("Elevation of Priv", "Frontline worker accesses administrative routes or modifies physician records.", "Role-Based Access Control middleware enforcing role checks ('worker', 'doctor', 'admin').")
    ]
    
    t23 = doc.add_table(rows=len(stride_data)+1, cols=3)
    t23.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t23)
    cw23 = [Inches(1.2), Inches(2.7), Inches(3.1)]
    
    h23 = ["STRIDE Category", "Identified Threat Scenario", "Architectural Countermeasure"]
    for j, h in enumerate(h23):
        cell = t23.cell(0, j); cell.width = cw23[j]
        set_cell_shading(cell, "154360"); set_cell_margins(cell, top=70, bottom=70, left=70, right=70)
        p = cell.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h); r.font.name = 'Times New Roman'; r.font.size = Pt(8.5); r.bold = True; r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        
    for i, (scat, sthreat, smit) in enumerate(stride_data):
        row_cells = t23.rows[i+1].cells
        for j, w in enumerate(cw23):
            row_cells[j].width = w; set_cell_margins(row_cells[j], top=50, bottom=50, left=60, right=60)
            if i % 2 == 1: set_cell_shading(row_cells[j], "F4F6F7")
        
        p0 = row_cells[0].paragraphs[0]; r = p0.add_run(scat); r.font.name = 'Times New Roman'; r.font.size = Pt(8); r.bold = True
        p1 = row_cells[1].paragraphs[0]; r = p1.add_run(sthreat); r.font.name = 'Times New Roman'; r.font.size = Pt(8)
        p2 = row_cells[2].paragraphs[0]; r = p2.add_run(smit); r.font.name = 'Times New Roman'; r.font.size = Pt(8)

    add_h2(doc, "2.4 Clinical Safety & Ethics Requirements")
    add_p(doc, "In accordance with medical software safety guidelines, ArogyaMitra enforces three clinical safety principles:")
    add_p(doc, "1. Human-in-the-Loop Operation: ArogyaMitra is architected solely as decision support, not an autonomous diagnostic agent. It cannot initiate clinical treatments or finalize discharge without human health worker confirmation.", space_after=3)
    add_p(doc, "2. Deterministic Red-Flag Precedence: Rule-based emergency detection operates with precedence over statistical predictions, ensuring that life-threatening symptoms trigger immediate emergency transfer regardless of model confidence.", space_after=3)
    add_p(doc, "3. Synthetic Data Disclosure: The machine learning model was trained on synthetic clinical datasets (304 unique rows). The system explicitly incorporates these operational limits into its documentation and consent workflows.", space_after=8)
