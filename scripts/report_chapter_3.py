"""
ArogyaMitra — Report Chapter 3 Builder
Constructs Chapter 3: System Architecture & Design, including container topology,
Bayesian ML formulations, red-flag triage overrides, LLM fallbacks, security, and concurrency.
"""

import os
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from report_styles import add_p, add_h1, add_h2, add_h3, add_caption, add_callout, insert_image, set_cell_margins, set_cell_shading, set_table_borders, NAVY_BLUE, SLATE_BLUE, MUTED_GREY

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG_DIR = os.path.join(BASE_DIR, "docs", "REPORT_FINAL", "figures")

def add_chapter_3(doc):
    add_h1(doc, "Chapter 3: System Architecture & Design")
    
    add_h2(doc, "3.1 Architectural Overview & Container Topology")
    add_p(doc, "ArogyaMitra is architected as an event-driven, containerized microservice ecosystem engineered for fault tolerance, horizontal modularity, and strict cryptographic trust boundaries. Rather than deploying a monolithic application where failure in an auxiliary service (such as natural language explanation) halts primary triage, the system decomposes clinical workflows across four specialized services, an edge reverse proxy, and a persistent database.")
    
    add_p(doc, "The container topology comprises six coordinated Docker services operating within a dedicated private bridge network (`arogya-net`):")
    add_p(doc, "1. Edge Gateway & TLS Terminator (Nginx): The sole public ingress point. Exposes HTTPS over port 443 with TLS 1.3 encryption, terminates client connections, enforces HTTP Strict Transport Security (HSTS), manages cross-origin resource sharing (CORS), and proxies traffic internally.", space_after=4)
    add_p(doc, "2. Frontend UI Service (Streamlit / Python 3.11): Provides an intuitive, role-tailored interface for community health workers and medical officers. Communicates exclusively with the backend gateway over the internal container network (port 8501).", space_after=4)
    add_p(doc, "3. Core Backend API Gateway (Node.js 20 / Express): Orchestrates consultation state, enforces JWT authentication and Argon2id password security, executes AES-256-GCM field encryption, and manages MongoDB transactions (port 5000).", space_after=4)
    add_p(doc, "4. Stateless Machine Learning Engine (FastAPI / Python 3.11): Implements the scikit-learn Bernoulli Naive Bayes classifier, vectorizes 131 symptom inputs, and computes closed-form log-odds feature attributions (port 8000).", space_after=4)
    add_p(doc, "5. Guarded LLM Narrative Service (FastAPI / LangGraph): Executes structured narrative formatting, Gemini API cascades, regex guardrails, and deterministic clinical template rendering (port 8001).", space_after=4)
    add_p(doc, "6. Database Persistence Layer (MongoDB 7.0): Stores encrypted consultation records, user accounts, and immutable audit trails backed by a dedicated Docker persistent volume (`mongo-data`). Crucially, MongoDB exposes no published ports to the host machine, preventing unauthorized network access.", space_after=10)

    # Insert Figure 3.1
    diag1_path = os.path.join(FIG_DIR, "diag1_architecture_trust_boundaries.png")
    insert_image(doc, diag1_path, "Figure 3.1: Microservice Container Topology & Trust Boundaries", width_in=6.0)

    add_p(doc, "Figure 3.1 illustrates the architectural trust boundaries. Outside the perimeter, client web browsers communicate strictly over encrypted TLS 1.3 tunnels. Inside the perimeter, the Nginx reverse proxy routes traffic across microservices over the isolated Docker bridge. Sensitive database interactions occur strictly between the Backend API Gateway and MongoDB, isolating the data tier from external tampering.")

    # Insert Figure 3.2
    diag6_path = os.path.join(FIG_DIR, "diag6_docker_network_volume.png")
    insert_image(doc, diag6_path, "Figure 3.2: Docker Bridge Network Isolation & Persistent Volumes", width_in=5.8)

    add_p(doc, "As detailed in Figure 3.2, container network isolation guarantees that even if a frontend or auxiliary narrative service is compromised, direct access to raw database files or unencrypted storage volumes is physically impossible under standard Linux containerization namespaces.")

    add_h2(doc, "3.2 Machine Learning Inference & Calibration Engine")
    add_h3(doc, "3.2.1 Bernoulli Naive Bayes Mathematical Formulation")
    add_p(doc, "The core classification engine of ArogyaMitra utilizes a multivariate Bernoulli Naive Bayes model. Let $\\mathcal{C} = \\{c_1, c_2, \\dots, c_K\\}$ denote the set of $K = 41$ target disease classes, and let $\\mathbf{x} = (x_1, x_2, \\dots, x_D)^T \\in \\{0, 1\\}^D$ represent a binary symptom vector of dimension $D = 131$, where $x_j = 1$ indicates the reported presence of symptom $j$, and $x_j = 0$ indicates its absence.")
    
    add_p(doc, "Under the conditional independence assumption, the joint likelihood of observing symptom vector $\\mathbf{x}$ given disease class $c$ is expressed as:")
    
    add_callout(doc, "P(\\mathbf{x} \\mid Y = c) = \\prod_{j=1}^{D} P(X_j = x_j \\mid Y = c) = \\prod_{j=1}^{D} \\theta_{c, j}^{x_j} (1 - \\theta_{c, j})^{1 - x_j}\n\nwhere \\theta_{c, j} = P(X_j = 1 \\mid Y = c) represents the parameter probability that symptom j is present given disease c.", "Mathematical Formulation: Likelihood")

    add_p(doc, "To prevent zero-frequency probability estimation when a symptom was not observed during training for a particular disease, Laplace smoothing (additive smoothing with parameter $\\alpha = 1.0$) is applied during parameter estimation:")
    
    add_callout(doc, "\\hat{\\theta}_{c, j} = \\frac{N_{c, j} + \\alpha}{N_c + 2\\alpha}\n\nwhere N_{c, j} is the count of training samples in class c presenting symptom j, and N_c is the total sample count in class c.", "Mathematical Formulation: Laplace Smoothing")

    add_p(doc, "Applying Bayes' Theorem, the posterior class probability is formulated in log-space to ensure numerical stability and prevent floating-point underflow:")
    
    add_callout(doc, "\\ln P(Y = c \\mid \\mathbf{x}) = \\ln P(Y = c) + \\sum_{j=1}^{D} \\left[ x_j \\ln \\hat{\\theta}_{c, j} + (1 - x_j) \\ln (1 - \\hat{\\theta}_{c, j}) \\right] - \\ln P(\\mathbf{x})", "Mathematical Formulation: Log-Posterior")

    add_p(doc, "The optimal predicted condition $\\hat{y}$ is selected via maximum a posteriori (MAP) estimation across all 41 classes: $\\hat{y} = \\arg\\max_{c \\in \\mathcal{C}} \\ln P(Y = c \\mid \\mathbf{x})$. To present normalized differential estimates to clinicians, the log-posteriors are converted via the standard Softmax function.")

    add_h3(doc, "3.2.2 Feature Engineering & Vocabulary Alignment")
    add_p(doc, "The feature vocabulary consists of 131 discrete clinical symptoms curated to reflect primary healthcare presentations in rural India. Symptoms range from common infectious indicators (fever, chills, cough, nausea) to acute systemic signs (chest pain, breathlessness, jaundice, joint swelling).")
    
    add_p(doc, "When a health worker selects symptoms in the user interface, the frontend constructs a JSON payload containing an array of string identifiers. The ML microservice validates the incoming payload against a strict Pydantic schema, verifies that all submitted identifiers exist within the master vocabulary, and constructs a 131-dimensional binary NumPy array. Unselected features are deterministically zero-padded. Crucially, the model evaluates both the presence ($x_j = 1$) and the absence ($x_j = 0$) of symptoms, allowing the model to penalize disease hypotheses whose hallmark signs are explicitly denied by the patient.")

    add_h3(doc, "3.2.3 Explainability via Top-Feature Attribution")
    add_p(doc, "A critical limitation of complex ensemble models (such as deep neural networks or dense gradient boosted trees) is their opacity. In clinical settings, frontline workers cannot safely act upon an ungrounded classification score without understanding which symptoms drove the algorithmic decision. While post-hoc perturbation methods like LIME (Ribeiro et al., 2016) are widely used, they introduce stochastic sampling variance and high latency (often 800–1,500 ms).")
    
    add_p(doc, "To provide deterministic, sub-millisecond interpretability, ArogyaMitra derives exact additive log-odds feature attributions directly from the trained Bernoulli parameters. Let $\\bar{\\theta}_j = \\frac{1}{K} \\sum_{k=1}^K \\hat{\\theta}_{k, j}$ represent the background prevalence of symptom $j$ across all disease classes. The individual evidence contribution $w_{c, j}(x_j)$ of feature $j$ toward disease class $c$ is formulated as:")
    
    add_callout(doc, "w_{c, j}(x_j) = x_j \\ln \\left( \\frac{\\hat{\\theta}_{c, j}}{\\bar{\\theta}_j} \\right) + (1 - x_j) \\ln \\left( \\frac{1 - \\hat{\\theta}_{c, j}}{1 - \\bar{\\theta}_j} \\right)", "Mathematical Formulation: Additive Feature Log-Odds")

    add_p(doc, "Properties of this derivation:", bold=True)
    add_p(doc, "1. Positive Evidence: If symptom $j$ is present ($x_j = 1$) and its class probability exceeds background prevalence ($\\hat{\\theta}_{c, j} > \\bar{\\theta}_j$), $w_{c, j} > 0$, indicating that this symptom actively supports the diagnosis.", space_after=4)
    add_p(doc, "2. Negative Evidence: If symptom $j$ is present but rare in class $c$ ($\\hat{\\theta}_{c, j} < \\bar{\\theta}_j$), or absent ($x_j = 0$) despite being a defining hallmark of class $c$ ($\\hat{\\theta}_{c, j} \\gg \\bar{\\theta}_j$), $w_{c, j} < 0$, penalizing the hypothesis.", space_after=4)
    add_p(doc, "3. Machine-Precision Additivity: Summing $w_{c, j}$ across all $D = 131$ features exactly equals the total log-evidence difference to machine precision ($< 10^{-10}$ error), satisfying the efficiency axiom of Shapley values (Lundberg & Lee, 2017) without Monte Carlo approximations.", space_after=10)

    add_h3(doc, "3.2.4 Calibration Theoretical Background & Analysis")
    add_p(doc, "In supervised machine learning, a classifier is considered well-calibrated if its predicted probability reflects true empirical observation: $P(Y = 1 \\mid \\hat{P} = p) = p$. However, as established by Niculescu-Mizil & Caruana (2005) [N], Naive Bayes models violate this principle due to the conditional independence assumption. Because correlated symptoms multiply their likelihoods, the resulting log-odds scale grows linearly with the number of redundant features, pushing output probabilities asymptotically to 0.0 or 1.0.")
    
    add_p(doc, "During the development of ArogyaMitra, post-hoc calibration via Platt Scaling (logistic sigmoid fitting) was empirically tested on held-out folds of the 304 unique rows. The results were revealing: Platt scaling caused multiclass cross-entropy log loss to deteriorate significantly from 0.0061 to 0.1643. This occurred because the small sample size (~7.4 instances per class) led the logistic sigmoid to compress well-separated likelihoods, introducing boundary noise.")
    
    add_callout(doc, "Engineering Decision on Calibration: Following the findings of Niculescu-Mizil & Caruana (2005), post-hoc calibration was discarded. The model outputs are explicitly labeled in the user interface and API as 'uncalibrated posterior estimates from Bernoulli Naive Bayes', preventing false confidence among clinicians.", "Architectural Ruling")

    add_h3(doc, "3.2.5 Comparative Model Selection")
    add_p(doc, "To rigorously justify the selection of Bernoulli Naive Bayes over popular gradient-boosted decision trees, an extensive comparative evaluation was conducted against Tuned LightGBM (Ke et al., 2017) and Tuned XGBoost using nested cross-validation. While decision trees excel on dense, continuous tabular data, their recursive splitting mechanism struggles on high-dimensional, sparse binary vectors under missing data.")
    
    add_p(doc, "As detailed in Chapter 4, when symptoms are progressively dropped (simulating real-world patient forgetfulness or incomplete health worker intake), tree ensembles experience catastrophic accuracy collapse (LightGBM dropping from 0.989 to 0.683 at 50% dropout). In contrast, Bernoulli Naive Bayes maintains 0.919 accuracy at 50% dropout due to its linear log-odds accumulation. Combined with an ultra-low inference latency of 1.8 milliseconds (compared to 45 ms for tree ensembles), BernoulliNB represents the optimal algorithmic choice for rural primary healthcare decision support.")

    add_h2(doc, "3.3 Rule-Based Clinical Red-Flag Override System")
    add_p(doc, "The most critical clinical safety mechanism in ArogyaMitra is the deterministic Red-Flag Screening Layer. As demonstrated by Wallace et al. (2022) [W], statistical symptom checkers frequently fail to recognize acute surgical and cardiac emergencies when symptoms overlap with benign conditions.")
    
    add_p(doc, "To eliminate this risk, ArogyaMitra decouples emergency triage from machine learning. Prior to executing Bayesian inference, incoming symptom vectors are evaluated against deterministic medical rules. If any emergency combination is triggered, the system instantly sets triage urgency to EMERGENCY, locks the recommendation, and displays prominent warning banners instructing the health worker to immediately arrange tertiary ambulance transport. Table 3.1 details the red-flag screening triggers implemented in `Backend/src/validators/diseaseClasses.js`.")

    # Table 3.1
    rf_data = [
        ("RF-01", "Acute Coronary Syndrome", "Chest pain AND (breathlessness OR sweating OR radiation to left arm)", "Immediate emergency transfer to cardiac facility; initiate Aspirin/ECG per local protocol."),
        ("RF-02", "Severe Acute Respiratory Distress", "Breathlessness AND (cyanosis OR inability to speak in sentences OR altered sensorium)", "High-flow oxygen administration; emergency transport to ICU-equipped center."),
        ("RF-03", "Acute Meningitis / Sepsis", "High fever AND stiff neck AND altered consciousness", "Immediate emergency transfer; evaluate for acute bacterial meningitis or cerebral malaria."),
        ("RF-04", "Massive Hemoptysis", "Coughing up blood AND acute tachycardia OR dyspnea", "Emergency pulmonary referral; airway protection and blood product preparation."),
        ("RF-05", "Acute Abdomen / Perforation", "Severe generalized abdominal rigidity AND vomiting AND signs of shock", "Immediate surgical referral; strict nil-by-mouth; IV fluid resuscitation.")
    ]
    
    t31 = doc.add_table(rows=len(rf_data)+1, cols=4)
    t31.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t31)
    cw31 = [Inches(1.0), Inches(2.0), Inches(2.3), Inches(2.0)]
    
    h31 = ["Rule ID", "Clinical Presentation", "Symptom Trigger Pattern", "Mandatory Emergency Action"]
    for j, h in enumerate(h31):
        cell = t31.cell(0, j)
        cell.width = cw31[j]
        set_cell_shading(cell, "B71C1C")
        set_cell_margins(cell, top=100, bottom=100, left=90, right=90)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.font.name = 'Times New Roman'; r.font.size = Pt(9.5); r.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        
    for i, (rid, rtitle, rtrig, ract) in enumerate(rf_data):
        row_cells = t31.rows[i+1].cells
        for j, w in enumerate(cw31):
            row_cells[j].width = w
            set_cell_margins(row_cells[j], top=70, bottom=70, left=80, right=80)
            if i % 2 == 1:
                set_cell_shading(row_cells[j], "FFEBEE")
        
        p0 = row_cells[0].paragraphs[0]
        r = p0.add_run(rid); r.font.name = 'Times New Roman'; r.font.size = Pt(9); r.bold = True
        p1 = row_cells[1].paragraphs[0]
        r = p1.add_run(rtitle); r.font.name = 'Times New Roman'; r.font.size = Pt(9); r.bold = True
        p2 = row_cells[2].paragraphs[0]
        r = p2.add_run(rtrig); r.font.name = 'Times New Roman'; r.font.size = Pt(8.5)
        p3 = row_cells[3].paragraphs[0]
        r = p3.add_run(ract); r.font.name = 'Times New Roman'; r.font.size = Pt(8.5)

    add_caption(doc, "Table 3.1: Rule-Based Emergency Red-Flag Trigger Conditions (DRAFT Status)", is_table=True)

    add_callout(doc, "Clinical Status Note: The red-flag rules specified in Table 3.1 represent DRAFT clinical heuristics documented in docs/RED_FLAG_REVIEW.md. They have not been formally validated by an institutional medical board or authorized by CDSCO. In live clinical deployment, these rules must undergo exhaustive multi-specialty physician validation.", "Clinical Validation Warning")

    add_h2(doc, "3.4 Multi-Tier LLM Explanation & Resilient Fallback Layer")
    add_p(doc, "While the Bayesian model produces statistical differential scores, raw numerical percentages are insufficient for community health workers who need actionable clinical summaries. To bridge this communication gap, ArogyaMitra integrates a Large Language Model narrative layer implemented using LangGraph and the Google Gemini API.")
    
    add_p(doc, "To prevent hallucination (Ji et al., 2023) and preserve patient safety, the LLM is architecturally isolated through strict guardrails:")
    add_p(doc, "1. Zero Diagnostic Authority: The LLM prompt explicitly denies the model diagnostic authority. The disease name, differential ranking, and top contributing symptoms are pre-computed by the ML engine and passed as immutable context. The LLM is instructed solely to synthesize a patient-friendly explanation in clear, simple language.", space_after=4)
    add_p(doc, "2. Prohibition of Specific Drug Dosages: The system prompt prohibits the LLM from prescribing specific pharmaceutical dosages (e.g., 'Take Amoxicillin 500mg TID'), restricting output to supportive primary care measures (hydration, rest, oral rehydration salts) and physician referral advice.", space_after=4)
    add_p(doc, "3. Dynamic Ordered Cascade: Because external LLM APIs are subject to transient 429 quota exhaustion and 404 model deprecation, the system maintains an ordered cascade: `LLM_MODELS = ['gemini-2.5-flash', 'gemini-3.5-flash', 'gemini-3-flash-preview']`. If a model returns 429 or 404, the engine immediately tries the next candidate.", space_after=4)
    add_p(doc, "4. Whole-Phrase Confidence Word Filtering: To prevent misleading overconfidence, generated summaries are evaluated against banned confidence phrases ('certain diagnosis', 'guaranteed cure', 'very high probability'). If a banned phrase is detected, the system triggers one regeneration attempt. If the second attempt still violates guardrails, the system discards the LLM output entirely and falls back to a deterministic, pre-compiled clinical template.", space_after=10)

    # Insert Figure 3.3
    diag5_path = os.path.join(FIG_DIR, "diag5_llm_timeout_hierarchy.png")
    insert_image(doc, diag5_path, "Figure 3.3: Hierarchical LLM Request Timeout Cascade & Guardrail Budgets", width_in=5.8)

    add_p(doc, "As shown in Figure 3.3, request timeouts follow a strict descending hierarchy to prevent gateway thread exhaustion. The edge Nginx proxy enforces a 90-second read timeout; the backend API enforces a 30-second HTTP client timeout; the LangGraph service enforces a hard 20-second deadline across all cascade attempts; and individual Gemini API calls enforce a 10-second per-attempt cap. If the 20-second overall cap expires, the system deterministically serves a local pre-compiled template, guaranteeing bounded response time.")

    add_h2(doc, "3.5 End-to-End Clinical Consultation Workflow")
    add_p(doc, "The complete clinical consultation lifecycle is structured as an auditable multi-stage state machine that guides frontline workers while maintaining mandatory physician oversight.")

    # Insert Figure 3.4
    diag2_path = os.path.join(FIG_DIR, "diag2_workflow_sequence.png")
    insert_image(doc, diag2_path, "Figure 3.4: End-to-End Clinical Consultation Sequence Workflow", width_in=6.0)

    add_p(doc, "Figure 3.4 details the sequence of interactions across the ten-step clinical lifecycle:")
    add_p(doc, "Step 1: Patient presents at Sub-Centre; ASHA worker initiates consultation via Streamlit UI, entering demographic details and chief complaints.", space_after=3)
    add_p(doc, "Step 2: ASHA worker selects presenting symptoms from the validated 131-symptom vocabulary list.", space_after=3)
    add_p(doc, "Step 3: Frontend dispatches consultation payload to Backend API (`POST /api/v1/consultation/triage`).", space_after=3)
    add_p(doc, "Step 4: Backend validates input and executes deterministic Red-Flag Screening. If positive, triage status is immediately locked to Emergency, bypassing ML.", space_after=3)
    add_p(doc, "Step 5: If no red flags are found, Backend calls ML Microservice (`POST /predict`), receiving top-3 differential diagnoses and exact log-odds feature attributions within 5 ms.", space_after=3)
    add_p(doc, "Step 6: Backend calls LangGraph Narrative Service (`POST /generate-narrative`). If LLM fails or times out, deterministic clinical template is substituted.", space_after=3)
    add_p(doc, "Step 7: Backend encrypts sensitive fields via AES-256-GCM, stores record in MongoDB, and returns complete triage assessment to UI.", space_after=3)
    add_p(doc, "Step 8: UI presents assessment to health worker with transparent top-contributing symptoms and an explicit Decision Gate B: Accept or Escalate.", space_after=3)
    add_p(doc, "Step 9: If escalated or low-confidence (<70%), consultation enters physician review queue for second opinion.", space_after=3)
    add_p(doc, "Step 10: Physician reviews differential, adds clinical observations, and finalizes disposition.", space_after=10)

    # Insert Figure 3.5
    diag3_path = os.path.join(FIG_DIR, "diag3_state_machine.png")
    insert_image(doc, diag3_path, "Figure 3.5: Consultation Lifecycle State Machine & Decision Gate B", width_in=5.8)

    add_callout(doc, "Implementation Status Note: [TO BE UPDATED after defect-fix round] The consultation intake, red-flag screening, Bayesian ML inference, LLM narrative formatting, and worker acceptance workflows are fully verified and operational. The secondary physician escalation saving, asynchronous doctor review queue, and bidirectional status reflection represent ongoing defect-fix enhancements documented in docs/KNOWN_LIMITATIONS.md.", "Workflow Status")

    add_h2(doc, "3.6 Security Architecture & Cryptographic Implementation")
    add_p(doc, "ArogyaMitra implements an audited five-layer defense-in-depth security model engineered to protect sensitive medical data against unauthorized access, network snooping, and insider privilege escalation.")

    # Insert Figure 3.6
    diag4_path = os.path.join(FIG_DIR, "diag4_security_layers.png")
    insert_image(doc, diag4_path, "Figure 3.6: Five-Layer Defense-in-Depth Security Architecture", width_in=6.0)

    add_p(doc, "The five security layers illustrated in Figure 3.6 operate cooperatively:")
    add_p(doc, "Layer 1 — Perimeter & Transport Security: Enforces TLS 1.3 with automated HSTS, X-Content-Type-Options: nosniff, and Content-Security-Policy headers managed by Nginx.", space_after=4)
    add_p(doc, "Layer 2 — Gateway Rate Limiting: Restricts public authentication routes to 5 requests per 15 minutes and API routes to 100 requests per 15 minutes, preventing denial-of-service and brute-force cracking.", space_after=4)
    add_p(doc, "Layer 3 — Authentication & Session Management: Protects credentials using Argon2id (3 iterations, 64 MB memory cost). Issues cryptographically signed JSON Web Tokens (JWT) with 15-minute expirations and explicit 401 session expiry handling.", space_after=4)
    add_p(doc, "Layer 4 — Role-Based Authorization: Validates user permissions ('worker', 'doctor', 'admin') at the middleware layer on every protected route.", space_after=4)
    add_p(doc, "Layer 5 — Field-Level Cryptographic Storage: All patient identifiers (name, contact, location) are encrypted at rest using AES-256-GCM with a unique 96-bit initialization vector (IV) per record. An automated startup test (`encryption_key_exit.test.js`) guarantees that the backend process immediately terminates if the master encryption key is missing or invalid.", space_after=10)

    # Insert Figure 3.7
    diag7_path = os.path.join(FIG_DIR, "diag7_mitm_interception.png")
    insert_image(doc, diag7_path, "Figure 3.7: Packet Interception Analysis: Cleartext HTTP vs Encrypted TLS 1.3", width_in=5.8)

    add_p(doc, "Figure 3.7 presents packet capture analysis conducted during security auditing. Under unencrypted HTTP, patient symptom payloads and authentication tokens are plainly visible to network sniffers. Under ArogyaMitra's enforced TLS 1.3 configuration, network interception yields only cryptographically randomized ciphertext.")

    add_h2(doc, "3.7 Database Design, Concurrency & Data Integrity")
    add_p(doc, "The persistence tier is built on MongoDB 7.0 utilizing three core schemas: `Consultation`, `User`, and `AuditLog`. To preserve data integrity during simultaneous clinical interactions across rural clinics, the system implements Optimistic Concurrency Control (OCC) (Kung & Robinson, 1981).")
    
    add_p(doc, "Each consultation document maintains a version key (`__v`). When a health worker or physician submits a status update, Mongoose executes an atomic conditional update: `Consultation.findOneAndUpdate({ _id: id, __v: currentVersion, status: 'PENDING' }, { $set: updateData, $inc: { __v: 1 } })`. If another user modified the record concurrently, the version precondition fails, aborting the write and returning an HTTP 409 Conflict error, preventing lost updates.")
    
    add_p(doc, "Furthermore, to resolve severe latency degradation identified during load testing (where `GET /consultation/my` suffered 7.0s p99 latencies due to unindexed collection scans), the endpoint was re-architected with server-side pagination (`page` and `limit` parameters) and lean Mongoose projections (`.select('patientName age gender symptoms topCondition triageStatus createdAt')`), reducing response payload sizes by 84% and cutting latency by 60.5%.")
