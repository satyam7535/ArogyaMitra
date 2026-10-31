"""
ArogyaMitra — Report Chapter 5, References & Appendices Builder
Constructs Chapter 5 (Conclusion & Future Scope), Formal References,
Appendix A (Engineering Challenges), Appendix B (Reproduction Commands), and Appendix C (Test Inventory).
"""

from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from report_styles import add_p, add_h1, add_h2, add_h3, add_caption, add_callout, set_cell_margins, set_cell_shading, set_table_borders, NAVY_BLUE, SLATE_BLUE, MUTED_GREY
from report_data import APPENDIX_A_CHALLENGES

def add_chapter_5(doc):
    add_h1(doc, "Chapter 5: Conclusion & Future Scope")
    
    add_h2(doc, "5.1 Project Summary & Achievements")
    add_p(doc, "The ArogyaMitra project successfully engineered and validated an auditable, explainable, and fail-closed AI-assisted clinical decision support system tailored specifically for community health workers in resource-constrained rural environments. By confronting the systemic pitfalls documented in contemporary medical literature—specifically diagnostic inaccuracy and safety hazards in consumer symptom checkers (Wallace et al., 2022 [W]), and probability distortion in Naive Bayes classifiers (Niculescu-Mizil & Caruana, 2005 [N])—the project achieved several key engineering milestones:")
    
    add_p(doc, "1. Deduplicated Baseline Benchmark: Uncovered and eliminated a 93.8% synthetic duplication artifact in raw public clinical datasets, establishing an uncontaminated 304-row benchmark across 41 disease classes and 131 symptoms.", space_after=4)
    add_p(doc, "2. Robust Bayesian Inference Engine: Demonstrated that stateless Bernoulli Naive Bayes significantly outperforms tuned gradient-boosted decision trees under symptom dropout (0.919 accuracy vs 0.683 for LightGBM at 50% missing data) while executing in 1.8 milliseconds.", space_after=4)
    add_p(doc, "3. Closed-Form Additive Feature Attribution: Derived exact mathematical log-odds symptom attributions satisfying Shapley efficiency to machine precision (< 1e-10) without stochastic sampling.", space_after=4)
    add_p(doc, "4. Fail-Closed Clinical Safety Architecture: Decoupled emergency triage from statistical classification via deterministic red-flag overrides; isolated the LLM narrative layer behind 10s/20s timeout caps and whole-phrase confidence filters backed by pre-compiled templates; and eliminated all mock fallbacks in favor of explicit HTTP 503 error states.", space_after=4)
    add_p(doc, "5. Audited Defense-in-Depth Security & Concurrency: Implemented TLS 1.3, Argon2id password hashing, AES-256-GCM field-level encryption, optimistic concurrency controls (`__v`), and verified zero fixable High container vulnerabilities under Trivy and 100% clean passes across 321 automated tests.", space_after=10)

    add_h2(doc, "5.2 Lessons Learned & Engineering Insights")
    add_p(doc, "The iterative design and remediation of ArogyaMitra yielded profound software engineering and machine learning insights:")
    add_p(doc, "1. The Danger of Silent Fallback Mocks: In software engineering tutorials, falling back to mock data on network error is common practice. In clinical healthcare, however, returning canned mock predictions on an ML outage is catastrophic. Designing for fail-closed behavior—explicitly signaling unavailability and halting unsafe automation—is an absolute prerequisite for medical software.", space_after=6)
    add_p(doc, "2. Empirical Humility Regarding Model Calibration: Machine learning practitioners often treat classifier probabilities as genuine clinical likelihoods. Verifying that Platt scaling degraded log loss on small clinical samples reinforced the vital lesson that uncalibrated model scores must never masquerade as diagnostic certainties.", space_after=6)
    add_p(doc, "3. Profiling Over Intuition: A full collection scan on worker consultation history initially introduced a 783 ms bottleneck. Methodical profiling revealed the exact root cause, and simple database indexing combined with server-side pagination yielded a 60.5% latency reduction, outperforming premature caching.", space_after=12)

    add_h2(doc, "5.3 Future Work & Roadmap")
    add_p(doc, "While ArogyaMitra establishes a robust foundation for primary healthcare decision support, several key milestones remain for future clinical transition:")
    add_p(doc, "1. Multi-Centric Prospective Clinical Pilot: Conduct observational clinical pilots across rural Health and Wellness Centres in Maharashtra, evaluating concordance between ASHA worker decision support recommendations and attending Medical Officer diagnoses.", space_after=4)
    add_p(doc, "2. Integration with ABHA & Ayushman Bharat Ecosystem: Implement standardized HL7 FHIR interfaces to enable seamless bidirectional synchronization with the Ayushman Bharat Digital Mission (ABDM) electronic health records.", space_after=4)
    add_p(doc, "3. Multi-Modal Diagnostic Ingestion: Extend the Bayesian feature vector to ingest continuous vital streams (SpO2, pulse rate, automated non-invasive blood pressure) and point-of-care rapid diagnostic strip images (e.g., malaria RDTs).", space_after=4)
    add_p(doc, "4. Non-Parametric Calibration on Clinical Cohorts: When genuine multi-thousand patient cohorts become available, train non-parametric calibration maps (such as beta calibration or Venn-Abers predictors) to deliver formally calibrated probabilistic risk intervals.", space_after=12)

def add_references(doc):
    add_h1(doc, "References")
    
    refs = [
        ("Wallace et al. (2022) [W]", "Wallace, W., Chan, C., Chidambaram, S., et al. (2022). The diagnostic and triage accuracy of digital symptom checkers and their potential to provide safe triage: A systematic review and meta-analysis. npj Digital Medicine, 5(1), 177. https://doi.org/10.1038/s41746-022-00713-1"),
        ("Niculescu-Mizil & Caruana (2005) [N]", "Niculescu-Mizil, A., & Caruana, R. (2005). Predicting good probabilities with supervised learning. In Proceedings of the 22nd International Conference on Machine Learning (ICML '05), pp. 625–632. ACM. https://doi.org/10.1145/1102351.1102430"),
        ("Domingos & Pazzani (1997)", "Domingos, P., & Pazzani, M. (1997). On the optimality of the simple Bayesian classifier under zero-one loss. Machine Learning, 29(2), 103–130. https://doi.org/10.1023/A:1007413511361"),
        ("Ke et al. (2017)", "Ke, G., Meng, Q., Finley, T., Wang, T., Chen, W., Ma, W., Ye, Q., & Liu, T. Y. (2017). LightGBM: A highly efficient gradient boosting decision tree. Advances in Neural Information Processing Systems (NeurIPS 2017), 30, 3146–3154."),
        ("Ribeiro et al. (2016)", "Ribeiro, M. T., Singh, S., & Guestrin, C. (2016). \"Why should I trust you?\": Explaining the predictions of any classifier. In Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining (KDD '16), pp. 1135–1144. ACM. https://doi.org/10.1145/2939672.2939778"),
        ("Lundberg & Lee (2017)", "Lundberg, S. M., & Lee, S. I. (2017). A unified approach to interpreting model predictions. Advances in Neural Information Processing Systems (NeurIPS 2017), 30, 4765–4774."),
        ("Ji et al. (2023)", "Ji, Z., Lee, N., Frieske, R., Yu, T., Su, D., Yan, Y., Ishii, E., Bang, Y. J., Madotto, A., & Fung, P. (2023). Survey of hallucination in natural language generation. ACM Computing Surveys, 55(12), 1–38. https://doi.org/10.1145/3571730"),
        ("Singhal et al. (2023)", "Singhal, K., Azizi, S., Tu, T., Mahdavi, S. S., Wei, J., Chung, H. W., Nathan, S., Gaurav, A., Schmidt, V., Le, Q., et al. (2023). Large language models encode clinical knowledge. Nature, 620(7972), 172–180. https://doi.org/10.1038/s41586-023-06291-2"),
        ("Biryukov et al. (2016)", "Biryukov, A., Dinu, D., & Khovratovich, D. (2016). Argon2: New generation of memory-hard functions for password hashing and other applications. In 2016 IEEE European Symposium on Security and Privacy (EuroS&P), pp. 292–302. IEEE. https://doi.org/10.1109/EuroSP.2016.31"),
        ("Kung & Robinson (1981)", "Kung, H. T., & Robinson, J. T. (1981). On optimistic methods for concurrency control. ACM Transactions on Database Systems (TODS), 6(2), 213–226. https://doi.org/10.1145/319566.319567"),
        ("Government of India (2023)", "Ministry of Law and Justice, Government of India. (2023). The Digital Personal Data Protection Act, 2023 (Act No. 22 of 2023). The Gazette of India, Extraordinary, Part II—Section 1."),
        ("World Health Organization (2021)", "World Health Organization. (2021). Ethics and governance of artificial intelligence for health: WHO guidance. World Health Organization. ISBN: 978-92-4-002920-0."),
        ("Indian Council of Medical Research (2023)", "Indian Council of Medical Research. (2023). Ethical guidelines for application of artificial intelligence in biomedical research and healthcare. ICMR, New Delhi, India."),
        ("Open Web Application Security Project (2021)", "OWASP Foundation. (2021). OWASP Top 10:2021 The Ten Most Critical Web Application Security Risks. https://owasp.org/Top10/"),
        ("National Institute of Standards and Technology (2007)", "Dworkin, M. (2007). Recommendation for block cipher modes of operation: Galois/Counter Mode (GCM) and GMAC. NIST Special Publication 800-38D, National Institute of Standards and Technology, Gaithersburg, MD.")
    ]
    
    for i, (short_cite, full_text) in enumerate(refs):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_before = Pt(3)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = 1.15
        
        r1 = p.add_run(f"[{i+1}] ")
        r1.font.name = 'Times New Roman'
        r1.font.size = Pt(10)
        r1.bold = True
        r1.font.color.rgb = NAVY_BLUE
        
        r2 = p.add_run(full_text)
        r2.font.name = 'Times New Roman'
        r2.font.size = Pt(10)

def add_appendix_a(doc):
    add_h1(doc, "Appendix A: Engineering Challenges, Root Causes, and Architectural Remediation Fixes")
    add_p(doc, "During the end-to-end realization of ArogyaMitra, numerous subtle architectural defects, data leakage anomalies, cryptographic vulnerabilities, and concurrency bottlenecks were identified through systematic testing and faculty audits. Table A.1 chronicles the ten primary engineering challenges, their diagnosed root causes, and the concrete technical remediations implemented in the codebase.")

    # Table A.1
    t_a1 = doc.add_table(rows=len(APPENDIX_A_CHALLENGES)+1, cols=4)
    t_a1.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_a1)
    cwa1 = [Inches(1.8), Inches(2.2), Inches(2.4), Inches(1.1)]
    
    ha1 = ["Identified Challenge", "Discovered Root Cause", "Architectural Remediation Implemented", "Evidence Citation"]
    for j, h in enumerate(ha1):
        cell = t_a1.cell(0, j)
        cell.width = cwa1[j]
        set_cell_shading(cell, "154360")
        set_cell_margins(cell, top=100, bottom=100, left=70, right=70)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.font.name = 'Times New Roman'; r.font.size = Pt(8.5); r.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        
    for i, row in enumerate(APPENDIX_A_CHALLENGES):
        row_cells = t_a1.rows[i+1].cells
        for j, w in enumerate(cwa1):
            row_cells[j].width = w
            set_cell_margins(row_cells[j], top=70, bottom=70, left=70, right=70)
            if i % 2 == 1:
                set_cell_shading(row_cells[j], "F4F6F7")
        
        p0 = row_cells[0].paragraphs[0]
        r = p0.add_run(row["problem"]); r.font.name = 'Times New Roman'; r.font.size = Pt(8); r.bold = True
        p1 = row_cells[1].paragraphs[0]
        r = p1.add_run(row["found"]); r.font.name = 'Times New Roman'; r.font.size = Pt(7.5)
        p2 = row_cells[2].paragraphs[0]
        r = p2.add_run(row["fix"]); r.font.name = 'Times New Roman'; r.font.size = Pt(7.5)
        p3 = row_cells[3].paragraphs[0]
        r = p3.add_run(row["evidence"]); r.font.name = 'Times New Roman'; r.font.size = Pt(7); r.font.color.rgb = MUTED_GREY

    add_caption(doc, "Table A.1: Engineering Challenges, Root Causes, and Architectural Remediation Fixes", is_table=True)

def add_appendix_b(doc):
    add_h1(doc, "Appendix B: Reproduction Commands & Verification Playbook")
    add_p(doc, "To ensure total scientific reproducibility, this appendix provides the complete sequence of command-line instructions required to launch the ArogyaMitra microservice cluster, execute all 321 automated test suites, run the 20 golden clinical test cases, execute the Playwright UI automation, and run the security scanners from a clean development environment.")

    cmds = [
        ("Step 1: Clone Repository & Build Docker Stack", 
         "git checkout remediation\n"
         "docker compose -f docker-compose.yml build\n"
         "docker compose -f docker-compose.yml up -d\n"
         "powershell -File scripts\\health_check.ps1"),
        ("Step 2: Seed Clean Test Environment", 
         "powershell -File scripts\\seed_docker.ps1\n"
         "# Verifies database initialized with 6 healthy services and clean test users"),
        ("Step 3: Execute Backend API Unit & Integration Suite (231 Tests)", 
         "docker compose exec -T backend npm test -- --coverage\n"
         "# Output recorded in docs/evidence/verify_backend.txt"),
        ("Step 4: Execute Machine Learning Inference Suite (55 Tests)", 
         "docker compose exec -T ml pytest -v\n"
         "# Output recorded in docs/evidence/verify_ml.txt"),
        ("Step 5: Execute Guarded LLM Narrative Suite (26 Tests)", 
         "docker compose exec -T graph pytest -v\n"
         "# Output recorded in docs/evidence/verify_graph.txt"),
        ("Step 6: Execute Frontend UI Test Suite (9 Tests)", 
         "docker compose exec -T ui pytest -v\n"
         "# Output recorded in docs/evidence/verify_ui.txt"),
        ("Step 7: Run Golden Clinical Validation Set (20 Vignettes)", 
         "python scripts\\test_p0_golden_set.py\n"
         "# Output recorded in docs/evidence/p0_golden_tests.txt"),
        ("Step 8: Run Playwright Browser Automation Suite (11 Journeys)", 
         "node scripts\\test_p4_playwright_suite.mjs\n"
         "# Output recorded in docs/evidence/p4_playwright_suite.txt"),
        ("Step 9: Execute Multi-Tier Load Test (2,400 Requests across C=1, 10, 50)", 
         "docker compose -f docker-compose.test.yml up -d\n"
         "python scripts\\run_p5_load_test_testmode.py\n"
         "# Output recorded in docs/evidence/load_test_testmode_results.txt"),
        ("Step 10: Run Container Vulnerability Auditing with Trivy", 
         "powershell -File scripts\\run_trivy_scan_all.ps1\n"
         "# Output recorded in docs/evidence/trivy_all_images_scan.txt")
    ]

    for title, code_block in cmds:
        add_p(doc, title, space_before=6, space_after=2, bold=True)
        table = doc.add_table(rows=1, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = table.cell(0, 0)
        set_cell_shading(cell, "263238")
        set_cell_margins(cell, top=80, bottom=80, left=120, right=120)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.line_spacing = 1.05
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(code_block)
        r.font.name = 'Consolas'
        r.font.size = Pt(8)
        r.font.color.rgb = RGBColor(0xEE, 0xFF, 0x41)
        p_after = doc.add_paragraph()
        p_after.paragraph_format.space_after = Pt(2)

def add_appendix_c(doc):
    add_h1(doc, "Appendix C: Complete Prototype Test Suite Inventory")
    add_p(doc, "Table C.1 catalogues the 321 automated prototype tests verifying system correctness, security guardrails, fail-closed behavior, and database integrity across all microservices.")

    # Table C.1
    tests_inv = [
        ("Backend", "tests/triage_flow.test.js", "18 Tests", "Tests full triage payload ingestion, Pydantic validation, and red-flag short-circuiting."),
        ("Backend", "tests/redflag_screening.test.js", "14 Tests", "Verifies all 5 emergency rules, boundary combinations, and override guarantees."),
        ("Backend", "tests/auth_argon2.test.js", "22 Tests", "Validates password hashing, salt uniqueness, timing resistance, and role verification."),
        ("Backend", "tests/aes_encryption.test.js", "16 Tests", "Verifies AES-256-GCM encryption at rest, unique IV generation, and deciphering."),
        ("Backend", "tests/encryption_key_exit.test.js", "8 Tests", "Production guard verifying backend terminates immediately if encryption key is unset."),
        ("Backend", "tests/concurrency_occ.test.js", "24 Tests", "Tests Mongoose `__v` optimistic locking and rejection of concurrent colliding updates."),
        ("Backend", "tests/pagination_projection.test.js", "20 Tests", "Validates server-side pagination, limit bounds, bad input handling, and lean projection."),
        ("Backend", "tests/api_security_headers.test.js", "28 Tests", "Verifies HSTS, X-Content-Type-Options, CSP, and CORS across endpoints."),
        ("Backend", "tests/rate_limit.test.js", "16 Tests", "Tests IP rate limiters, 429 status generation, and test-mode limit relaxation."),
        ("Backend", "tests/dpdp_consent.test.js", "14 Tests", "Tests patient consent logging, revocation requests, and data anonymization triggers."),
        ("Backend", "tests/doctor_queue.test.js", "25 Tests", "Verifies doctor consultation retrieval, status filtering, and clinician response notes."),
        ("Backend", "tests/fail_closed_ml.test.js", "26 Tests", "Verifies 503 MODEL_UNAVAILABLE error generation when ML service is down."),
        ("ML Engine", "tests/test_model_inference.py", "15 Tests", "Tests BernoulliNB prediction, output shape, class rankings, and Softmax normalization."),
        ("ML Engine", "tests/test_log_odds_attribution.py", "12 Tests", "Verifies exact additive log-odds formula and additivity to machine precision (<1e-10)."),
        ("ML Engine", "tests/test_vocabulary_validation.py", "10 Tests", "Tests 131 symptom vectorization, zero-padding, and invalid symptom rejection."),
        ("ML Engine", "tests/test_missing_dropout.py", "18 Tests", "Verifies model stability under 0%, 30%, and 50% random symptom masking."),
        ("Graph LLM", "tests/test_llm_timeouts.py", "8 Tests", "Verifies 10s per-attempt timeout and 20s hard deadline cap enforcement."),
        ("Graph LLM", "tests/test_model_cascade.py", "6 Tests", "Tests ordered cascade from gemini-2.5-flash to fallback models on 429/404."),
        ("Graph LLM", "tests/test_confidence_filter.py", "6 Tests", "Tests whole-phrase banned confidence detection and regeneration trigger."),
        ("Graph LLM", "tests/test_template_fallback.py", "6 Tests", "Verifies deterministic template rendering when LLM is offline or times out."),
        ("Frontend UI", "tests/test_ui_views.py", "5 Tests", "Validates Streamlit page rendering, role authentication, and session expiry warnings."),
        ("Frontend UI", "tests/test_triage_form.py", "4 Tests", "Tests symptom selection state, payload formatting, and submission handling.")
    ]

    t_c1 = doc.add_table(rows=len(tests_inv)+1, cols=4)
    t_c1.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_c1)
    cwc1 = [Inches(1.2), Inches(2.2), Inches(1.1), Inches(2.7)]
    
    hc1 = ["Target Service", "Test Suite File", "Test Count", "Functional Scope & Invariants Tested"]
    for j, h in enumerate(hc1):
        cell = t_c1.cell(0, j)
        cell.width = cwc1[j]
        set_cell_shading(cell, "154360")
        set_cell_margins(cell, top=100, bottom=100, left=70, right=70)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.font.name = 'Times New Roman'; r.font.size = Pt(8.5); r.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        
    for i, (tserv, tfile, tcnt, tdesc) in enumerate(tests_inv):
        row_cells = t_c1.rows[i+1].cells
        for j, w in enumerate(cwc1):
            row_cells[j].width = w
            set_cell_margins(row_cells[j], top=60, bottom=60, left=70, right=70)
            if i % 2 == 1:
                set_cell_shading(row_cells[j], "F4F6F7")
        
        p0 = row_cells[0].paragraphs[0]
        r = p0.add_run(tserv); r.font.name = 'Times New Roman'; r.font.size = Pt(8); r.bold = True
        p1 = row_cells[1].paragraphs[0]
        r = p1.add_run(tfile); r.font.name = 'Times New Roman'; r.font.size = Pt(8)
        p2 = row_cells[2].paragraphs[0]
        r = p2.add_run(tcnt); r.font.name = 'Times New Roman'; r.font.size = Pt(8); r.bold = True
        p3 = row_cells[3].paragraphs[0]
        r = p3.add_run(tdesc); r.font.name = 'Times New Roman'; r.font.size = Pt(7.5)

    add_caption(doc, "Table C.1: Detailed Inventory of 321 Prototype Automated Test Cases", is_table=True)
