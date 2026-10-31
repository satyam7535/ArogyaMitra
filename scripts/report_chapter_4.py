"""
ArogyaMitra — Report Chapter 4 Builder
Constructs Chapter 4: Empirical Evaluation & Experimental Results, including dataset provenance,
nested CV benchmark, calibration analysis, load testing, automated test suite, security audits,
literature discussion, and threats to validity.
"""

import os
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from report_styles import add_p, add_h1, add_h2, add_h3, add_caption, add_callout, insert_image, set_cell_margins, set_cell_shading, set_table_borders, NAVY_BLUE, SLATE_BLUE, MUTED_GREY

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG_DIR = os.path.join(BASE_DIR, "docs", "REPORT_FINAL", "figures")
UI_DIR = os.path.join(BASE_DIR, "docs", "evidence", "ui_screenshots")

def add_chapter_4(doc):
    add_h1(doc, "Chapter 4: Empirical Evaluation & Experimental Results")
    
    add_h2(doc, "4.1 Dataset Profile & Methodological Integrity")
    add_p(doc, "A critical flaw in many published machine learning benchmarks for clinical decision support is the uncritical use of raw public datasets without verifying data provenance or sample duplication. In early development, the standard Kaggle disease-symptom dataset (comprising 4,920 CSV records across 41 disease classes and 131 symptoms) was evaluated.")
    
    add_p(doc, "Automated data provenance auditing conducted in this project (`docs/evidence/data_provenance.txt`) revealed a profound methodological flaw: 4,616 of the 4,920 rows were exact duplicates, representing a staggering 93.8% synthetic duplication rate. When standard random train-test splits (such as 80/20 train/test) are applied to this raw dataset, identical symptom vectors inevitably leak across training and test partitions, yielding artificial, illusory test accuracies of 100.0%.")

    # Insert Figure 4.1
    fig3_path = os.path.join(FIG_DIR, "fig3_dataset_breakdown.png")
    insert_image(doc, fig3_path, "Figure 4.1: Dataset Profile: Raw Kaggle Duplication vs Deduplicated Cohort", width_in=5.8)

    add_p(doc, "Figure 4.1 illustrates the true dataset composition. After rigorous deduplication, exactly 304 unique clinical symptom vectors remain across the 41 disease classes (an average of approximately 7.4 unique presentations per disease). All empirical machine learning evaluations in ArogyaMitra were conducted strictly on this deduplicated 304-row benchmark to eliminate data leakage.")
    
    add_callout(doc, "Methodological Disclaimer: All machine learning models were evaluated exclusively on synthetic tabular data (304 unique rows across 41 diseases and 131 symptoms). The dataset contains zero real-patient records, lacks continuous clinical covariates (such as blood pressure or hemoglobin levels), and does not represent complex multi-morbid clinical populations.", "Synthetic Data Disclosure")

    add_h2(doc, "4.2 Machine Learning Performance & Robustness")
    add_p(doc, "To rigorously evaluate diagnostic robustness under missing clinical data, models were evaluated using a 5x3 Repeated Stratified K-Fold Cross-Validation protocol on the 304 unique rows. In each fold, presenting symptoms were subjected to in-fold random symptom dropout (masking 0%, 30%, and 50% of present symptoms) to simulate incomplete recall or imperfect health worker data collection.")
    
    add_p(doc, "Table 4.1 presents the empirical comparison between the deployed Bernoulli Naive Bayes classifier, Tuned LightGBM (Ke et al., 2017), and Tuned XGBoost across all dropout levels. All metrics trace directly to verifiable execution logs in `docs/evidence/model_benchmark.md` and `docs/evidence/tuned_tree_benchmark.md`.")

    # Table 4.1
    m_data = [
        ("Bernoulli Naive Bayes (Deployed)", "1.000 ± 0.000", "0.989 ± 0.014", "0.919 ± 0.023", "docs/evidence/model_benchmark.md:21-23"),
        ("Tuned LightGBM (Comparison)", "0.989 ± 0.012", "0.864 ± 0.038", "0.683 ± 0.052", "docs/evidence/tuned_tree_benchmark.md:21-23"),
        ("Tuned XGBoost (Comparison)", "0.984 ± 0.015", "0.868 ± 0.035", "0.720 ± 0.048", "docs/evidence/tuned_tree_benchmark.md:31-33")
    ]
    
    t41 = doc.add_table(rows=len(m_data)+1, cols=5)
    t41.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t41)
    cw41 = [Inches(2.2), Inches(1.1), Inches(1.1), Inches(1.1), Inches(1.7)]
    
    h41 = ["Model Architecture", "0% Dropout Acc", "30% Dropout Acc", "50% Dropout Acc", "Verifiable Evidence File"]
    for j, h in enumerate(h41):
        cell = t41.cell(0, j)
        cell.width = cw41[j]
        set_cell_shading(cell, "154360")
        set_cell_margins(cell, top=100, bottom=100, left=80, right=80)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.font.name = 'Times New Roman'; r.font.size = Pt(9); r.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        
    for i, (mname, a0, a30, a50, mevid) in enumerate(m_data):
        row_cells = t41.rows[i+1].cells
        for j, w in enumerate(cw41):
            row_cells[j].width = w
            set_cell_margins(row_cells[j], top=70, bottom=70, left=80, right=80)
            if i % 2 == 1:
                set_cell_shading(row_cells[j], "F4F6F7")
        
        p0 = row_cells[0].paragraphs[0]
        r = p0.add_run(mname); r.font.name = 'Times New Roman'; r.font.size = Pt(8.5); r.bold = True
        p1 = row_cells[1].paragraphs[0]
        r = p1.add_run(a0); r.font.name = 'Times New Roman'; r.font.size = Pt(8.5)
        p2 = row_cells[2].paragraphs[0]
        r = p2.add_run(a30); r.font.name = 'Times New Roman'; r.font.size = Pt(8.5)
        p3 = row_cells[3].paragraphs[0]
        r = p3.add_run(a50); r.font.name = 'Times New Roman'; r.font.size = Pt(8.5); r.bold = (i == 0)
        p4 = row_cells[4].paragraphs[0]
        r = p4.add_run(mevid); r.font.name = 'Times New Roman'; r.font.size = Pt(7.5); r.font.color.rgb = MUTED_GREY

    add_caption(doc, "Table 4.1: Stratified Repeated Cross-Validation Performance Across Dropout Levels", is_table=True)

    # Insert Figure 4.2
    fig1_path = os.path.join(FIG_DIR, "fig1_accuracy_vs_dropout.png")
    insert_image(doc, fig1_path, "Figure 4.2: Classification Accuracy Across Symptom Dropout Rates (0%, 30%, 50%)", width_in=5.8)

    add_p(doc, "As demonstrated in Figure 4.2, Bernoulli Naive Bayes exhibits exceptional resilience to missing symptom features. At 50% dropout, BernoulliNB maintains 0.919 accuracy, whereas LightGBM collapses to 0.683 and XGBoost drops to 0.720. This stark divergence occurs because tree-based models rely on recursive conditional splits; when an early split feature is missing, the sample is routed down an arbitrary branch. In contrast, BernoulliNB accumulates independent log-odds, allowing remaining symptoms to preserve the correct disease ranking.")

    add_p(doc, "Table 4.2 details the probabilistic calibration evaluation, reporting out-of-fold Expected Calibration Error (ECE) across dropout levels. Note that an earlier reported Brier score of 0.2483 was produced exclusively by in-sample evaluation on the 304 unique rows at 0% masking with a legacy model configuration (`docs/evidence/classification_report.md:6`), and is documented here strictly for historical audit reconciliation.")

    # Table 4.2
    cal_data = [
        ("Bernoulli Naive Bayes (Deployed)", "0.005", "0.032", "0.072", "docs/evidence/model_benchmark.md:27-29"),
        ("Tuned LightGBM (Comparison)", "0.010", "0.098", "0.202", "docs/evidence/tuned_tree_benchmark.md"),
        ("Tuned XGBoost (Comparison)", "0.083", "0.198", "0.212", "docs/evidence/tuned_tree_benchmark.md")
    ]
    
    t42 = doc.add_table(rows=len(cal_data)+1, cols=5)
    t42.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t42)
    cw42 = [Inches(2.2), Inches(1.1), Inches(1.1), Inches(1.1), Inches(1.7)]
    
    h42 = ["Model Architecture", "0% Dropout ECE", "30% Dropout ECE", "50% Dropout ECE", "Verifiable Evidence File"]
    for j, h in enumerate(h42):
        cell = t42.cell(0, j)
        cell.width = cw42[j]
        set_cell_shading(cell, "1B4F72")
        set_cell_margins(cell, top=100, bottom=100, left=80, right=80)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.font.name = 'Times New Roman'; r.font.size = Pt(9); r.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        
    for i, (mname, e0, e30, e50, mevid) in enumerate(cal_data):
        row_cells = t42.rows[i+1].cells
        for j, w in enumerate(cw42):
            row_cells[j].width = w
            set_cell_margins(row_cells[j], top=70, bottom=70, left=80, right=80)
            if i % 2 == 1:
                set_cell_shading(row_cells[j], "F4F6F7")
        
        p0 = row_cells[0].paragraphs[0]
        r = p0.add_run(mname); r.font.name = 'Times New Roman'; r.font.size = Pt(8.5); r.bold = True
        p1 = row_cells[1].paragraphs[0]
        r = p1.add_run(e0); r.font.name = 'Times New Roman'; r.font.size = Pt(8.5)
        p2 = row_cells[2].paragraphs[0]
        r = p2.add_run(e30); r.font.name = 'Times New Roman'; r.font.size = Pt(8.5)
        p3 = row_cells[3].paragraphs[0]
        r = p3.add_run(e50); r.font.name = 'Times New Roman'; r.font.size = Pt(8.5); r.bold = (i == 0)
        p4 = row_cells[4].paragraphs[0]
        r = p4.add_run(mevid); r.font.name = 'Times New Roman'; r.font.size = Pt(7.5); r.font.color.rgb = MUTED_GREY

    add_caption(doc, "Table 4.2: Expected Calibration Error (ECE) and Probabilistic Evaluation", is_table=True)

    # Insert Figure 4.3
    fig2_path = os.path.join(FIG_DIR, "fig2_ece_vs_dropout.png")
    insert_image(doc, fig2_path, "Figure 4.3: Expected Calibration Error (ECE) Across Dropout Rates", width_in=5.8)

    add_h2(doc, "4.3 Load Testing, Concurrency & System Throughput")
    add_p(doc, "To verify system stability and throughput under concurrent rural clinic traffic, an extensive load test was conducted using a dedicated testing configuration (`docker-compose.test.yml`). In test mode, rate limits are relaxed (`ALLOW_LOAD_TEST=true`) and generative LLM calls are disabled (`LLM_ENABLED=false`) to isolate backend routing, database transaction overhead, and cryptographic execution without external API quota throttling. Crucially, the production stack rejects relaxed limits by design.")
    
    add_p(doc, "The standardized test executed exactly 200 requests per endpoint across Concurrency levels 1, 10, and 50, totaling 2,400 HTTP requests across four endpoints: user authentication (`/api/v1/auth/login`), consultation submission (`/api/v1/consultation/triage`), clinician response (`/api/v1/consultation/respond`), and worker consultation history (`/api/v1/consultation/my`).")
    
    add_p(doc, "Across all 2,400 requests, the status code distribution was 100% clean: exactly 2,400 HTTP 200 responses, zero HTTP 400 Bad Requests, zero HTTP 429 Rate Limits, and zero HTTP 500 Internal Server Errors. Table 4.3 reports the throughput and percentile latency distributions recorded in `docs/evidence/load_test_testmode_results.txt`.")

    # Table 4.3
    lt_data = [
        ("Concurrency 1 (Sequential)", "10.2 req/s", "235.3 ms", "283.0 ms", "317.0 ms", "660.6 ms", "800/800"),
        ("Concurrency 10 (Moderate Load)", "13.9 req/s", "598.6 ms", "835.6 ms", "914.8 ms", "1028.9 ms", "800/800"),
        ("Concurrency 50 (Stress Load)", "14.7 req/s", "2790.6 ms", "3801.4 ms", "4092.1 ms", "4612.4 ms", "800/800")
    ]
    
    t43 = doc.add_table(rows=len(lt_data)+1, cols=7)
    t43.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t43)
    cw43 = [Inches(1.8), Inches(0.9), Inches(0.8), Inches(0.8), Inches(0.8), Inches(0.9), Inches(0.8)]
    
    h43 = ["Test Concurrency Level", "Throughput", "p50 Latency", "p90 Latency", "p95 Latency", "p99 Latency", "Success Ratio"]
    for j, h in enumerate(h43):
        cell = t43.cell(0, j)
        cell.width = cw43[j]
        set_cell_shading(cell, "154360")
        set_cell_margins(cell, top=100, bottom=100, left=60, right=60)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.font.name = 'Times New Roman'; r.font.size = Pt(8.5); r.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        
    for i, (clevel, tput, lp50, lp90, lp95, lp99, sratio) in enumerate(lt_data):
        row_cells = t43.rows[i+1].cells
        for j, w in enumerate(cw43):
            row_cells[j].width = w
            set_cell_margins(row_cells[j], top=70, bottom=70, left=60, right=60)
            if i % 2 == 1:
                set_cell_shading(row_cells[j], "F4F6F7")
        
        p0 = row_cells[0].paragraphs[0]
        r = p0.add_run(clevel); r.font.name = 'Times New Roman'; r.font.size = Pt(8); r.bold = True
        p1 = row_cells[1].paragraphs[0]
        r = p1.add_run(tput); r.font.name = 'Times New Roman'; r.font.size = Pt(8)
        p2 = row_cells[2].paragraphs[0]
        r = p2.add_run(lp50); r.font.name = 'Times New Roman'; r.font.size = Pt(8)
        p3 = row_cells[3].paragraphs[0]
        r = p3.add_run(lp90); r.font.name = 'Times New Roman'; r.font.size = Pt(8)
        p4 = row_cells[4].paragraphs[0]
        r = p4.add_run(lp95); r.font.name = 'Times New Roman'; r.font.size = Pt(8)
        p5 = row_cells[5].paragraphs[0]
        r = p5.add_run(lp99); r.font.name = 'Times New Roman'; r.font.size = Pt(8)
        p6 = row_cells[6].paragraphs[0]
        r = p6.add_run(sratio); r.font.name = 'Times New Roman'; r.font.size = Pt(8); r.bold = True
        r.font.color.rgb = RGBColor(0x2E, 0x7D, 0x32)

    add_caption(doc, "Table 4.3: Comprehensive Multi-Tier Load Test Performance (2,400 Requests)", is_table=True)

    # Insert Figure 4.4
    fig4_path = os.path.join(FIG_DIR, "fig4_load_test_latency_throughput.png")
    insert_image(doc, fig4_path, "Figure 4.4: Load Test Throughput & Latency Distributions (C=1, 10, 50)", width_in=5.8)

    add_p(doc, "During early testing, the worker consultation history endpoint (`GET /consultation/my`) dominated latency, taking up to 783 ms under sequential load. Profiling revealed that MongoDB was performing an unindexed collection scan and serializing heavy internal audit objects. To resolve this, server-side pagination (`page` and `limit`) and a lean projection were introduced. Table 4.4 and Figure 4.5 contrast performance before and after pagination.")

    # Table 4.4
    opt_data = [
        ("Before Optimization (Full Scan)", "193.0 ms", "382.4 ms", "495.1 ms", "660.6 ms", "Entire record collection"),
        ("After Optimization (Paginated)", "76.2 ms", "112.5 ms", "128.0 ms", "152.0 ms", "20 records + Lean projection"),
        ("Net Improvement (Reduction)", "60.5% Speedup", "70.6% Speedup", "74.1% Speedup", "77.0% Speedup", "84% Bandwidth Saved")
    ]
    
    t44 = doc.add_table(rows=len(opt_data)+1, cols=6)
    t44.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t44)
    cw44 = [Inches(2.0), Inches(0.9), Inches(0.9), Inches(0.9), Inches(0.9), Inches(1.2)]
    
    h44 = ["Profiling State", "p50 Latency", "p90 Latency", "p95 Latency", "p99 Latency", "Payload Profile"]
    for j, h in enumerate(h44):
        cell = t44.cell(0, j)
        cell.width = cw44[j]
        set_cell_shading(cell, "1B4F72")
        set_cell_margins(cell, top=100, bottom=100, left=60, right=60)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.font.name = 'Times New Roman'; r.font.size = Pt(8.5); r.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        
    for i, (pstate, p50, p90, p95, p99, pprof) in enumerate(opt_data):
        row_cells = t44.rows[i+1].cells
        for j, w in enumerate(cw44):
            row_cells[j].width = w
            set_cell_margins(row_cells[j], top=70, bottom=70, left=60, right=60)
            if i % 2 == 1:
                set_cell_shading(row_cells[j], "F4F6F7")
        
        p0 = row_cells[0].paragraphs[0]
        r = p0.add_run(pstate); r.font.name = 'Times New Roman'; r.font.size = Pt(8); r.bold = True
        p1 = row_cells[1].paragraphs[0]
        r = p1.add_run(p50); r.font.name = 'Times New Roman'; r.font.size = Pt(8)
        p2 = row_cells[2].paragraphs[0]
        r = p2.add_run(p90); r.font.name = 'Times New Roman'; r.font.size = Pt(8)
        p3 = row_cells[3].paragraphs[0]
        r = p3.add_run(p95); r.font.name = 'Times New Roman'; r.font.size = Pt(8)
        p4 = row_cells[4].paragraphs[0]
        r = p4.add_run(p99); r.font.name = 'Times New Roman'; r.font.size = Pt(8)
        p5 = row_cells[5].paragraphs[0]
        r = p5.add_run(pprof); r.font.name = 'Times New Roman'; r.font.size = Pt(8); r.bold = (i == 2)

    add_caption(doc, "Table 4.4: Worker Consultation List Endpoint Profiling: Full Scan vs Pagination", is_table=True)

    # Insert Figure 4.5
    fig6_path = os.path.join(FIG_DIR, "fig6_list_latency_before_after.png")
    insert_image(doc, fig6_path, "Figure 4.5: Worker List Latency Before vs After Index Projection Optimization", width_in=5.8)

    add_h2(doc, "4.4 Automated Testing & Verification Suite")
    add_p(doc, "To verify system correctness and fail-closed safety, ArogyaMitra maintains a comprehensive automated testing suite encompassing 321 prototype test cases across all four microservices. Table 4.5 summarizes test distribution and execution logs.")

    # Table 4.5
    test_summary = [
        ("Backend API Service", "231 Tests", "Jest / Supertest", "100% Pass", "docs/evidence/verify_backend.txt:85"),
        ("Stateless ML Engine", "55 Tests", "Pytest / NumPy", "100% Pass", "docs/evidence/verify_ml.txt:47"),
        ("Guarded Graph Service", "26 Tests", "Pytest / LangGraph", "100% Pass", "docs/evidence/verify_graph.txt:32"),
        ("Frontend UI Service", "9 Tests", "Pytest / Streamlit", "100% Pass", "docs/evidence/verify_ui.txt:26"),
        ("Total Automated Tests", "321 Tests", "Multi-Framework", "100% Pass", "Clean Verification Run")
    ]
    
    t45 = doc.add_table(rows=len(test_summary)+1, cols=5)
    t45.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t45)
    cw45 = [Inches(1.8), Inches(1.1), Inches(1.3), Inches(1.0), Inches(1.6)]
    
    h45 = ["Microservice Layer", "Test Case Count", "Testing Harness", "Pass Rate", "Evidence Citation"]
    for j, h in enumerate(h45):
        cell = t45.cell(0, j)
        cell.width = cw45[j]
        set_cell_shading(cell, "154360")
        set_cell_margins(cell, top=100, bottom=100, left=70, right=70)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.font.name = 'Times New Roman'; r.font.size = Pt(8.5); r.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        
    for i, (sname, tcount, tharn, prate, tevid) in enumerate(test_summary):
        row_cells = t45.rows[i+1].cells
        for j, w in enumerate(cw45):
            row_cells[j].width = w
            set_cell_margins(row_cells[j], top=70, bottom=70, left=70, right=70)
            if i % 2 == 1:
                set_cell_shading(row_cells[j], "F4F6F7")
        
        p0 = row_cells[0].paragraphs[0]
        r = p0.add_run(sname); r.font.name = 'Times New Roman'; r.font.size = Pt(8); r.bold = True
        p1 = row_cells[1].paragraphs[0]
        r = p1.add_run(tcount); r.font.name = 'Times New Roman'; r.font.size = Pt(8)
        p2 = row_cells[2].paragraphs[0]
        r = p2.add_run(tharn); r.font.name = 'Times New Roman'; r.font.size = Pt(8)
        p3 = row_cells[3].paragraphs[0]
        r = p3.add_run(prate); r.font.name = 'Times New Roman'; r.font.size = Pt(8); r.bold = True
        r.font.color.rgb = RGBColor(0x2E, 0x7D, 0x32)
        p4 = row_cells[4].paragraphs[0]
        r = p4.add_run(tevid); r.font.name = 'Times New Roman'; r.font.size = Pt(7.5); r.font.color.rgb = MUTED_GREY

    add_caption(doc, "Table 4.5: Automated Prototype Test Suite Breakdown Across Services", is_table=True)

    # Insert Figure 4.6
    fig5_path = os.path.join(FIG_DIR, "fig5_test_suite_composition.png")
    insert_image(doc, fig5_path, "Figure 4.6: Test Suite Distribution Across Prototype Architectural Layers (321 Tests)", width_in=5.8)

    add_p(doc, "In addition to unit and integration testing, two specialized end-to-end verification suites are executed against the running Docker stack:")
    add_p(doc, "1. Golden Clinical Test Set (20/20 Passing): Validates 20 standardized clinical vignettes covering emergency cardiac, respiratory, infectious, and dermatological presentations (`docs/evidence/p0_golden_tests.txt:38`).", space_after=4)
    add_p(doc, "2. Playwright End-to-End Suite (11/11 Passing): Automates complete browser journeys across authenticated roles, testing intake, red-flag emergency blocking, role-based navigation, pagination, and fail-closed error handling (`docs/evidence/p4_playwright_suite.txt:72`).", space_after=10)

    # Insert UI Screenshots
    s1_path = os.path.join(UI_DIR, "p4_s1_worker_accept.png")
    insert_image(doc, s1_path, "Figure 4.7: User Interface: Primary Health Worker Consultation Intake & Accept Journey", width_in=5.5)

    s2_path = os.path.join(UI_DIR, "p4_s2_redflag_blocked.png")
    insert_image(doc, s2_path, "Figure 4.8: User Interface: Red-Flag Emergency Detection & Blocked Direct Triage", width_in=5.5)

    s11_path = os.path.join(UI_DIR, "p4_s11_ui_pagination.png")
    insert_image(doc, s11_path, "Figure 4.9: User Interface: Server-Side Consultation Pagination & Historical Record Review", width_in=5.5)

    s9_path = os.path.join(UI_DIR, "p4_s9_ml_outage_error.png")
    insert_image(doc, s9_path, "Figure 4.10: User Interface: Fail-Closed Resilient Error State on ML Service Outage", width_in=5.5)

    add_h2(doc, "4.5 Security Vulnerability & Dependency Auditing")
    add_p(doc, "To verify container and dependency hygiene, automated security scanning was conducted across the production images. Vulnerability auditing with Trivy (`trivy image --ignore-unfixed`) verified zero High or Critical vulnerabilities with available upstream vendor fixes across the backend, ML, and graph Python runtime images (`docs/evidence/trivy_all_images_scan.txt`). Similarly, `pip-audit` verified that all Python dependencies in the LangGraph service are cleanly pinned with zero known CVEs.")
    
    add_p(doc, "Dynamic application security testing was conducted using the OWASP Zed Attack Proxy (ZAP) baseline scanner. Table 4.6 documents the five identified Low-risk findings and their architectural dispositions.")

    # Table 4.6
    zap_data = [
        ("10015", "Re-examine Cache-Control Directives", "Low (Informational)", "Accepted, not tested: Static UI assets employ caching, while dynamic API responses set strict no-store headers."),
        ("10020", "Missing Anti-clickjacking Header", "Low (Informational)", "Mitigated: Nginx gateway sets `X-Frame-Options: SAMEORIGIN` across all proxied responses."),
        ("10021", "X-Content-Type-Options Header Missing", "Low (Informational)", "Mitigated: Enforced `X-Content-Type-Options: nosniff` globally in Nginx configuration."),
        ("10038", "Content Security Policy (CSP) Header Not Set", "Low (Informational)", "Mitigated: Implemented CSP policy restricting script and connect sources to trusted endpoints."),
        ("90004", "Cross-Origin-Embedder-Policy (COEP) Missing", "Low (Informational)", "Accepted, not tested: Cross-origin embedding is restricted by top-level CORS and Docker network boundaries.")
    ]
    
    t46 = doc.add_table(rows=len(zap_data)+1, cols=4)
    t46.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t46)
    cw46 = [Inches(0.9), Inches(2.2), Inches(1.3), Inches(2.4)]
    
    h46 = ["Plugin ID", "ZAP Alert Title", "Risk Level", "Architectural Disposition"]
    for j, h in enumerate(h46):
        cell = t46.cell(0, j)
        cell.width = cw46[j]
        set_cell_shading(cell, "154360")
        set_cell_margins(cell, top=100, bottom=100, left=70, right=70)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.font.name = 'Times New Roman'; r.font.size = Pt(8.5); r.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        
    for i, (pid, ptitle, prisk, pdisp) in enumerate(zap_data):
        row_cells = t46.rows[i+1].cells
        for j, w in enumerate(cw46):
            row_cells[j].width = w
            set_cell_margins(row_cells[j], top=70, bottom=70, left=70, right=70)
            if i % 2 == 1:
                set_cell_shading(row_cells[j], "F4F6F7")
        
        p0 = row_cells[0].paragraphs[0]
        r = p0.add_run(pid); r.font.name = 'Times New Roman'; r.font.size = Pt(8); r.bold = True
        p1 = row_cells[1].paragraphs[0]
        r = p1.add_run(ptitle); r.font.name = 'Times New Roman'; r.font.size = Pt(8)
        p2 = row_cells[2].paragraphs[0]
        r = p2.add_run(prisk); r.font.name = 'Times New Roman'; r.font.size = Pt(8)
        p3 = row_cells[3].paragraphs[0]
        r = p3.add_run(pdisp); r.font.name = 'Times New Roman'; r.font.size = Pt(7.5)

    add_caption(doc, "Table 4.6: OWASP ZAP Dynamic Security Baseline Scan Dispositions", is_table=True)

    add_h2(doc, "4.6 Literature-Linked Discussion & Analysis")
    add_p(doc, "The empirical findings obtained across ArogyaMitra provide direct architectural answers to core vulnerabilities documented in clinical and machine learning literature:")
    
    add_p(doc, "1. Overcoming the Swiss-Cheese Failure Model (Wallace et al., 2022 [W]): Wallace et al. cautioned that commercial symptom checkers produce safety hazards when erroneous classification cascades into unsafe triage. In ArogyaMitra, this hazard is eliminated by decoupling triage from classification: rule-based red-flag screening operates prior to ML inference, guaranteeing that acute surgical and cardiac emergencies are triaged safely regardless of model confidence.", space_after=6)
    
    add_p(doc, "2. Grounding Classifier Overconfidence (Niculescu-Mizil & Caruana, 2005 [N]): Theoretical literature established that Naive Bayes models push probabilities toward 0 and 1, while post-hoc calibration overfits on scarce clinical cohorts. ArogyaMitra embraces this theoretical reality: discarding false calibration claims, labeling scores as uncalibrated posterior estimates, and using exact additive log-odds to explain feature attributions to machine precision.", space_after=6)
    
    add_p(doc, "3. Containing LLM Hallucinations (Ji et al., 2023): Generative models frequently fabricate clinical claims. By stripping the LLM of diagnostic authority, enforcing strict timeout budgets (10s/20s), and deploying regex confidence filters backed by pre-compiled templates, ArogyaMitra demonstrates how modern generative AI can be deployed safely in high-stakes healthcare domains.", space_after=12)

    add_h2(doc, "4.7 Limitations & Threats to Validity")
    add_p(doc, "A rigorous engineering evaluation requires full disclosure of system boundaries, limitations, and threats to validity:")
    
    add_p(doc, "1. Synthetic Tabular Dataset Limitation: The system was trained and evaluated on synthetic data (304 unique rows across 41 disease classes). It has not been validated on real-world patient records, EHR databases, or multi-morbid clinical cohorts. The true clinical sensitivity on human populations remains unmeasured.", space_after=4)
    add_p(doc, "2. Unvalidated Clinical Heuristics: Red-flag screening rules represent DRAFT heuristics (`docs/RED_FLAG_REVIEW.md`). They have not received formal certification from CDSCO or institutional medical ethical boards.", space_after=4)
    add_p(doc, "3. Generative Model Nondeterminism: Although constrained by temperature=0.0 and regex filters, LLMs are fundamentally non-deterministic and subject to API rate limits (HTTP 429).", space_after=4)
    add_p(doc, "4. Single-Node Testbed Constraints: Load testing was executed on local virtualized container infrastructure. Real-world rural deployment requires multi-region cluster testing under intermittent cellular packet loss.", space_after=12)
