"""
ArogyaMitra — Report Chapter 4 Builder (Item 2, 3, 5, 9, 10, 14, 18, 19 Compliant)
Builds Chapter 4: Empirical Evaluation & Experimental Results, including dataset provenance,
nested CV benchmark, calibration evaluation, load testing, automated testing, security auditing,
literature discussion, and extended known limitations.
"""

import os
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from report_styles import (
    add_p, add_h1, add_h2, add_h3, add_table_caption, add_callout, insert_image,
    set_cell_margins, set_cell_shading, set_table_borders,
    NAVY_BLUE, MUTED_GREY, DARK_GREY
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG_DIR = os.path.join(BASE_DIR, "docs", "REPORT_FINAL", "figures")

def add_chapter_4(doc):
    add_h1(doc, "Chapter 4: Empirical Evaluation & Experimental Results")
    
    add_h2(doc, "4.1 Dataset Profile & Methodological Integrity")
    add_p(doc, "A potential flaw in public machine learning benchmarks for clinical decision support is the uncritical use of datasets without verifying data provenance. During initial exploration, I evaluated the standard Kaggle disease-symptom dataset comprising 4,920 records across 41 disease classes and 131 symptoms.")
    
    add_p(doc, "Automated data provenance analysis (docs/evidence/data_provenance.txt:12-14) revealed that 4,616 of the 4,920 rows were exact duplicates, representing a 93.8% synthetic duplication rate. When random train-test splits (such as 80/20) are applied to this raw dataset, identical symptom vectors leak across partitions, producing artificial test accuracies of 100.0%.")

    # Insert Figure 4.2
    fig2_path = os.path.join(FIG_DIR, "fig2_dataset_provenance.png")
    insert_image(doc, fig2_path, "Figure 4.2: Dataset Provenance: Raw 4,920 Rows vs. 304 Deduplicated Unique Rows", width_in=4.4)

    add_p(doc, "Figure 4.2 illustrates the dataset composition. After deduplication, exactly 304 unique clinical symptom vectors remain across the 41 classes (approximately 7.4 unique presentations per disease). All empirical machine learning evaluations in ArogyaMitra were conducted strictly on this deduplicated 304-row benchmark.")
    
    add_callout(doc, "Dataset Scope: All machine learning models were evaluated on synthetic tabular data (304 unique rows across 41 classes and 131 symptoms). The dataset contains no real-patient records, lacks continuous clinical covariates (such as blood pressure or lab markers), and does not represent complex multi-morbid clinical populations.", "Synthetic Data Disclosure")

    add_h2(doc, "4.2 Machine Learning Performance & Robustness")
    add_p(doc, "To evaluate diagnostic robustness under missing clinical data, models were benchmarked using a 5-fold by 3-repeat (15 splits) Stratified Cross-Validation protocol on the 304 unique rows. In each fold, symptoms were subjected to in-fold random symptom dropout (masking 0%, 30%, and 50% of present symptoms) to simulate incomplete health worker data collection.")
    
    add_p(doc, "Table 4.1 presents the comparison between Bernoulli Naive Bayes, Tuned LightGBM [4], and Tuned XGBoost across all dropout levels. All metrics trace directly to docs/evidence/model_benchmark.md:14,31,48 and docs/evidence/tuned_tree_benchmark.md:12-17.")

    # Table 4.1 (Exact evidence numbers)
    add_table_caption(doc, "Table 4.1: Repeated Stratified 5x3 Cross-Validation Accuracy Across Dropout")
    m_data = [
        ("BernoulliNB (Deployed)", "1.000 ± 0.000", "0.989 ± 0.014", "0.919 ± 0.023", "docs/evidence/model_benchmark.md:14,31,48"),
        ("Tuned LightGBM [4]", "0.9890 ± 0.0119", "0.8640 ± 0.0399", "0.6830 ± 0.0783", "docs/evidence/tuned_tree_benchmark.md:12-14"),
        ("Tuned XGBoost", "0.9836 ± 0.0139", "0.8683 ± 0.0413", "0.7203 ± 0.0773", "docs/evidence/tuned_tree_benchmark.md:15-17")
    ]
    
    t41 = doc.add_table(rows=len(m_data)+1, cols=5)
    t41.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t41)
    cw41 = [Inches(1.8), Inches(1.2), Inches(1.2), Inches(1.2), Inches(1.9)]
    
    h41 = ["Model Architecture", "0% Dropout Acc", "30% Dropout Acc", "50% Dropout Acc", "Evidence Citation"]
    for j, h in enumerate(h41):
        cell = t41.cell(0, j); cell.width = cw41[j]
        set_cell_shading(cell, "154360"); set_cell_margins(cell, top=70, bottom=70, left=60, right=60)
        p = cell.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h); r.font.name = 'Times New Roman'; r.font.size = Pt(8.5); r.bold = True; r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        
    for i, (mname, a0, a30, a50, mevid) in enumerate(m_data):
        row_cells = t41.rows[i+1].cells
        for j, w in enumerate(cw41):
            row_cells[j].width = w; set_cell_margins(row_cells[j], top=50, bottom=50, left=60, right=60)
            if i % 2 == 1: set_cell_shading(row_cells[j], "F4F6F7")
        
        p0 = row_cells[0].paragraphs[0]; r = p0.add_run(mname); r.font.name = 'Times New Roman'; r.font.size = Pt(8); r.bold = True
        p1 = row_cells[1].paragraphs[0]; r = p1.add_run(a0); r.font.name = 'Times New Roman'; r.font.size = Pt(8)
        p2 = row_cells[2].paragraphs[0]; r = p2.add_run(a30); r.font.name = 'Times New Roman'; r.font.size = Pt(8)
        p3 = row_cells[3].paragraphs[0]; r = p3.add_run(a50); r.font.name = 'Times New Roman'; r.font.size = Pt(8); r.bold = (i == 0)
        p4 = row_cells[4].paragraphs[0]; r = p4.add_run(mevid); r.font.name = 'Times New Roman'; r.font.size = Pt(7); r.font.color.rgb = MUTED_GREY

    # Table 4.2 (ECE)
    add_table_caption(doc, "Table 4.2: Expected Calibration Error (ECE) Across Dropout Rates")
    cal_data = [
        ("BernoulliNB (Deployed)", "0.005", "0.032", "0.072", "docs/evidence/model_benchmark.md:14,31,48"),
        ("Tuned LightGBM [4]", "0.0098 ± 0.0079", "0.0975 ± 0.0370", "0.2019 ± 0.0508", "docs/evidence/tuned_tree_benchmark.md:12-14"),
        ("Tuned XGBoost", "0.0826 ± 0.0129", "0.1983 ± 0.0346", "0.2118 ± 0.0474", "docs/evidence/tuned_tree_benchmark.md:15-17")
    ]
    
    t42 = doc.add_table(rows=len(cal_data)+1, cols=5)
    t42.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t42)
    cw42 = [Inches(1.8), Inches(1.2), Inches(1.2), Inches(1.2), Inches(1.9)]
    
    h42 = ["Model Architecture", "0% Dropout ECE", "30% Dropout ECE", "50% Dropout ECE", "Evidence Citation"]
    for j, h in enumerate(h42):
        cell = t42.cell(0, j); cell.width = cw42[j]
        set_cell_shading(cell, "1B4F72"); set_cell_margins(cell, top=70, bottom=70, left=60, right=60)
        p = cell.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h); r.font.name = 'Times New Roman'; r.font.size = Pt(8.5); r.bold = True; r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        
    for i, (mname, e0, e30, e50, mevid) in enumerate(cal_data):
        row_cells = t42.rows[i+1].cells
        for j, w in enumerate(cw42):
            row_cells[j].width = w; set_cell_margins(row_cells[j], top=50, bottom=50, left=60, right=60)
            if i % 2 == 1: set_cell_shading(row_cells[j], "F4F6F7")
        
        p0 = row_cells[0].paragraphs[0]; r = p0.add_run(mname); r.font.name = 'Times New Roman'; r.font.size = Pt(8); r.bold = True
        p1 = row_cells[1].paragraphs[0]; r = p1.add_run(e0); r.font.name = 'Times New Roman'; r.font.size = Pt(8)
        p2 = row_cells[2].paragraphs[0]; r = p2.add_run(e30); r.font.name = 'Times New Roman'; r.font.size = Pt(8)
        p3 = row_cells[3].paragraphs[0]; r = p3.add_run(e50); r.font.name = 'Times New Roman'; r.font.size = Pt(8); r.bold = (i == 0)
        p4 = row_cells[4].paragraphs[0]; r = p4.add_run(mevid); r.font.name = 'Times New Roman'; r.font.size = Pt(7); r.font.color.rgb = MUTED_GREY

    # Insert Merged Figure 4.1 (Two Panels, Item 18)
    fig1_path = os.path.join(FIG_DIR, "fig1_accuracy_and_ece.png")
    insert_image(doc, fig1_path, "Figure 4.1: Top-1 Accuracy and Expected Calibration Error (ECE) vs. Dropout", width_in=5.4)

    add_p(doc, "As shown in Figure 4.1, Bernoulli Naive Bayes maintains 0.919 accuracy at 50% symptom dropout, whereas LightGBM decreases to 0.683 and XGBoost to 0.720. In tree models, missing an early split feature routes samples down incorrect subtrees, whereas BernoulliNB accumulates independent symptom log-odds. Note that an earlier reported Brier score of 0.2483 was produced by in-sample evaluation on 304 unique rows at 0% masking with a legacy model (docs/evidence/classification_report.md:6).")

    add_h2(doc, "4.3 Load Testing, Concurrency & System Throughput")
    add_p(doc, "To evaluate gateway stability, a load test was executed using a test-mode compose override (docker-compose.test.yml) with relaxed rate limits (ALLOW_LOAD_TEST=true) and generative LLM calls disabled (LLM_ENABLED=false). Crucially, the production configuration rejects relaxed limits by design.")
    
    add_p(doc, "The test executed 200 requests per endpoint across Concurrency levels 1, 10, and 50, totaling 2,400 requests across four routes: /auth/login, /consultation/triage, /consultation/respond, and /consultation/my. Table 4.3 presents the measured throughput and latency distributions from docs/evidence/load_test_testmode_results.txt:15-17.")

    # Table 4.3 (Exact evidence numbers)
    add_table_caption(doc, "Table 4.3: Load Test Benchmark Results Across Concurrency Levels (2,400 Requests)")
    lt_data = [
        ("C = 1 (Sequential)", "800", "78.79 s", "10.2 req/s", "79.3 ms", "148.9 ms", "190.6 ms", "317.4 ms", "{200: 800}"),
        ("C = 10 (Moderate)", "800", "57.74 s", "13.9 req/s", "500.7 ms", "1530.1 ms", "1952.3 ms", "2548.2 ms", "{200: 800}"),
        ("C = 50 (Stress)", "800", "54.31 s", "14.7 req/s", "2428.4 ms", "5057.2 ms", "5862.8 ms", "8087.4 ms", "{200: 800}")
    ]
    
    t43 = doc.add_table(rows=len(lt_data)+1, cols=9)
    t43.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t43)
    cw43 = [Inches(1.3), Inches(0.5), Inches(0.7), Inches(0.9), Inches(0.7), Inches(0.8), Inches(0.8), Inches(0.8), Inches(0.8)]
    
    h43 = ["Concurrency", "Reqs", "Duration", "Throughput", "p50", "p90", "p95", "p99", "Status"]
    for j, h in enumerate(h43):
        cell = t43.cell(0, j); cell.width = cw43[j]
        set_cell_shading(cell, "154360"); set_cell_margins(cell, top=70, bottom=70, left=50, right=50)
        p = cell.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h); r.font.name = 'Times New Roman'; r.font.size = Pt(8); r.bold = True; r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        
    for i, (clev, creq, cdur, ctput, cp50, cp90, cp95, cp99, cstat) in enumerate(lt_data):
        row_cells = t43.rows[i+1].cells
        for j, w in enumerate(cw43):
            row_cells[j].width = w; set_cell_margins(row_cells[j], top=50, bottom=50, left=50, right=50)
            if i % 2 == 1: set_cell_shading(row_cells[j], "F4F6F7")
        
        row_cells[0].paragraphs[0].add_run(clev).font.size = Pt(7.5)
        row_cells[1].paragraphs[0].add_run(creq).font.size = Pt(7.5)
        row_cells[2].paragraphs[0].add_run(cdur).font.size = Pt(7.5)
        row_cells[3].paragraphs[0].add_run(ctput).font.size = Pt(7.5)
        row_cells[4].paragraphs[0].add_run(cp50).font.size = Pt(7.5)
        row_cells[5].paragraphs[0].add_run(cp90).font.size = Pt(7.5)
        row_cells[6].paragraphs[0].add_run(cp95).font.size = Pt(7.5)
        row_cells[7].paragraphs[0].add_run(cp99).font.size = Pt(7.5)
        r = row_cells[8].paragraphs[0].add_run(cstat); r.font.size = Pt(7.5); r.bold = True; r.font.color.rgb = RGBColor(0x2E, 0x7D, 0x32)

    # Insert Figure 4.3
    fig3_path = os.path.join(FIG_DIR, "fig3_load_test_results.png")
    insert_image(doc, fig3_path, "Figure 4.3: Gateway Throughput and Percentile Latencies Across Concurrency", width_in=5.4)

    add_p(doc, "During testing, the worker consultation history endpoint dominated latency. Profiling indicated collection scan and JSON payload overhead. To address this, server-side pagination and projection were introduced. Table 4.4 and Figure 4.4 contrast the before and after latency distributions from docs/evidence/load_test_profiling_notes.md:44-48.")

    # Table 4.4 (Exact evidence numbers, Item 3 note on combined change)
    add_table_caption(doc, "Table 4.4: Worker List Latency Before vs. After Pagination and Projection")
    opt_data = [
        ("Before (Full Scan)", "193.0 ms", "349.8 ms", "460.5 ms", "660.6 ms", "docs/evidence/load_test_profiling_notes.md:44"),
        ("After (Paginated + Projected)", "76.2 ms", "117.9 ms", "130.3 ms", "152.0 ms", "docs/evidence/load_test_profiling_notes.md:45"),
        ("Improvement", "60.5% faster", "66.3% faster", "71.7% faster", "77.0% faster", "Combined optimization")
    ]
    
    t44 = doc.add_table(rows=len(opt_data)+1, cols=6)
    t44.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t44)
    cw44 = [Inches(1.8), Inches(1.0), Inches(1.0), Inches(1.0), Inches(1.0), Inches(1.5)]
    
    h44 = ["Profiling State", "p50 Latency", "p90 Latency", "p95 Latency", "p99 Latency", "Evidence Citation"]
    for j, h in enumerate(h44):
        cell = t44.cell(0, j); cell.width = cw44[j]
        set_cell_shading(cell, "1B4F72"); set_cell_margins(cell, top=70, bottom=70, left=50, right=50)
        p = cell.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h); r.font.name = 'Times New Roman'; r.font.size = Pt(8.5); r.bold = True; r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        
    for i, (pstate, p50, p90, p95, p99, pcit) in enumerate(opt_data):
        row_cells = t44.rows[i+1].cells
        for j, w in enumerate(cw44):
            row_cells[j].width = w; set_cell_margins(row_cells[j], top=50, bottom=50, left=50, right=50)
            if i % 2 == 1: set_cell_shading(row_cells[j], "F4F6F7")
        
        p0 = row_cells[0].paragraphs[0]; r = p0.add_run(pstate); r.font.name = 'Times New Roman'; r.font.size = Pt(8); r.bold = True
        p1 = row_cells[1].paragraphs[0]; r = p1.add_run(p50); r.font.name = 'Times New Roman'; r.font.size = Pt(8)
        p2 = row_cells[2].paragraphs[0]; r = p2.add_run(p90); r.font.name = 'Times New Roman'; r.font.size = Pt(8)
        p3 = row_cells[3].paragraphs[0]; r = p3.add_run(p95); r.font.name = 'Times New Roman'; r.font.size = Pt(8)
        p4 = row_cells[4].paragraphs[0]; r = p4.add_run(p99); r.font.name = 'Times New Roman'; r.font.size = Pt(8)
        p5 = row_cells[5].paragraphs[0]; r = p5.add_run(pcit); r.font.name = 'Times New Roman'; r.font.size = Pt(7); r.font.color.rgb = MUTED_GREY

    add_callout(doc, "Profiling Finding: The latency gain came from a combined change (server-side pagination and projection) and the individual contributing cause was not isolated.", "Engineering Assessment")

    # Insert Figure 4.4
    fig4_path = os.path.join(FIG_DIR, "fig4_list_latency_before_after.png")
    insert_image(doc, fig4_path, "Figure 4.4: Worker List Latency Before vs. After Pagination and Projection", width_in=5.2)

    add_h2(doc, "4.4 Automated Testing & Verification Suite")
    add_p(doc, "ArogyaMitra maintains 321 automated prototype tests across its microservices. Table 4.5 summarizes the test counts recorded by the actual test runners in docs/evidence/verify_*.txt.")

    # Table 4.5 (Real test runner counts, Item 5 & 18)
    add_table_caption(doc, "Table 4.5: Automated Test Suite Summary from Actual Test Runners (321 Tests)")
    test_summary = [
        ("Backend API Service", "13 Files", "231 Tests", "Jest / Supertest", "100% Pass", "docs/evidence/verify_backend.txt:85"),
        ("Stateless ML Engine", "5 Files", "55 Tests", "Pytest / NumPy", "100% Pass", "docs/evidence/verify_ml.txt:47"),
        ("Guarded Graph Service", "2 Files", "26 Tests", "Pytest / LangGraph", "100% Pass", "docs/evidence/verify_graph.txt:32"),
        ("Frontend UI Service", "1 File", "9 Tests", "Pytest / Streamlit", "100% Pass", "docs/evidence/verify_ui.txt:26"),
        ("Total Automated Tests", "21 Files", "321 Tests", "Multi-Framework", "100% Pass", "Clean Verification Run")
    ]
    
    t45 = doc.add_table(rows=len(test_summary)+1, cols=6)
    t45.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t45)
    cw45 = [Inches(1.6), Inches(0.8), Inches(0.9), Inches(1.3), Inches(0.9), Inches(1.8)]
    
    h45 = ["Microservice", "Test Files", "Test Count", "Testing Harness", "Pass Rate", "Evidence Citation"]
    for j, h in enumerate(h45):
        cell = t45.cell(0, j); cell.width = cw45[j]
        set_cell_shading(cell, "154360"); set_cell_margins(cell, top=70, bottom=70, left=50, right=50)
        p = cell.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h); r.font.name = 'Times New Roman'; r.font.size = Pt(8.5); r.bold = True; r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        
    for i, (sname, sfiles, tcount, tharn, prate, tevid) in enumerate(test_summary):
        row_cells = t45.rows[i+1].cells
        for j, w in enumerate(cw45):
            row_cells[j].width = w; set_cell_margins(row_cells[j], top=50, bottom=50, left=50, right=50)
            if i % 2 == 1: set_cell_shading(row_cells[j], "F4F6F7")
        
        row_cells[0].paragraphs[0].add_run(sname).font.size = Pt(8)
        row_cells[1].paragraphs[0].add_run(sfiles).font.size = Pt(8)
        row_cells[2].paragraphs[0].add_run(tcount).font.size = Pt(8)
        row_cells[3].paragraphs[0].add_run(tharn).font.size = Pt(8)
        r = row_cells[4].paragraphs[0].add_run(prate); r.font.size = Pt(8); r.bold = True; r.font.color.rgb = RGBColor(0x2E, 0x7D, 0x32)
        row_cells[5].paragraphs[0].add_run(tevid).font.size = Pt(7)

    add_p(doc, "In addition, two verification suites run against the Docker cluster: (1) Golden Clinical Set: 20/20 cases passing (docs/evidence/p0_docker_tests.txt); (2) Playwright Suite: 11/11 browser journeys passing (docs/evidence/p4_playwright_suite.txt:72). Figure 4.5 presents a composite panel of four representative UI workflows.")

    # Insert Figure 4.5 (Combined UI Composite, Item 18)
    fig5_path = os.path.join(FIG_DIR, "fig5_ui_panels_combined.png")
    insert_image(doc, fig5_path, "Figure 4.5: User Interface Journeys: Worker Intake, Red-Flag Block, Pagination, Outage", width_in=5.4)

    add_h2(doc, "4.5 Security Vulnerability & Dependency Auditing")
    add_p(doc, "Container vulnerability scanning with Trivy (trivy image --ignore-unfixed) verified zero fixable Critical/High (Trivy --ignore-unfixed) vulnerabilities across backend, ml, and graph Python runtime images (docs/evidence/trivy_all_images_scan.txt). Dependency auditing with pip-audit confirmed pinned dependencies in the LangGraph service.")
    
    add_p(doc, "Dynamic scanning was conducted using an unauthenticated OWASP ZAP baseline scan against https://localhost, producing 6 warnings (docs/evidence/zap_baseline_report.txt:88-93). Table 4.6 documents the alerts and dispositions.")

    # Table 4.6 (Real 6 ZAP warnings, Item 9)
    add_table_caption(doc, "Table 4.6: OWASP ZAP Dynamic Security Baseline Scan Dispositions (6 Alerts)")
    zap_data = [
        ("10015", "Re-examine Cache-control Directives", "Warn", "accepted, not tested: Static UI assets employ caching, dynamic API sets no-store."),
        ("10049", "Storable and Cacheable Content", "Warn", "accepted, not tested: Evaluated on static assets; sensitive patient routes disable caching."),
        ("10055", "CSP: Failure to Define Directive with No Fallback", "Warn", "mitigated (not re-scanned): Restrictive default-src added to Nginx proxy headers."),
        ("10096", "Timestamp Disclosure - Unix", "Warn", "accepted, not tested: Internal diagnostic timestamps in health responses."),
        ("10109", "Modern Web Application", "Warn", "accepted, not tested: Informational alert identifying single-page/Streamlit frontend."),
        ("90004", "Cross-Origin-Embedder-Policy Header Missing", "Warn", "accepted, not tested: Cross-origin embedding restricted by network boundaries.")
    ]
    
    t46 = doc.add_table(rows=len(zap_data)+1, cols=4)
    t46.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t46)
    cw46 = [Inches(0.9), Inches(2.3), Inches(0.8), Inches(3.3)]
    
    h46 = ["Alert ID", "ZAP Alert Title", "Risk", "Architectural Disposition"]
    for j, h in enumerate(h46):
        cell = t46.cell(0, j); cell.width = cw46[j]
        set_cell_shading(cell, "154360"); set_cell_margins(cell, top=70, bottom=70, left=50, right=50)
        p = cell.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h); r.font.name = 'Times New Roman'; r.font.size = Pt(8.5); r.bold = True; r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        
    for i, (pid, ptitle, prisk, pdisp) in enumerate(zap_data):
        row_cells = t46.rows[i+1].cells
        for j, w in enumerate(cw46):
            row_cells[j].width = w; set_cell_margins(row_cells[j], top=50, bottom=50, left=50, right=50)
            if i % 2 == 1: set_cell_shading(row_cells[j], "F4F6F7")
        
        row_cells[0].paragraphs[0].add_run(pid).font.size = Pt(8)
        row_cells[1].paragraphs[0].add_run(ptitle).font.size = Pt(8)
        row_cells[2].paragraphs[0].add_run(prisk).font.size = Pt(8)
        row_cells[3].paragraphs[0].add_run(pdisp).font.size = Pt(7.5)

    add_h2(doc, "4.6 Literature-Linked Discussion & Analysis")
    add_p(doc, "The empirical findings obtained across ArogyaMitra address vulnerabilities documented in literature:")
    add_p(doc, "1. Addressing the Swiss-Cheese Failure Model (Wallace et al. [1]): Wallace et al. cautioned that commercial symptom checkers produce safety hazards when classification errors lead to delayed triage. In ArogyaMitra, emergency detection is decoupled from classification: deterministic red-flag screening operates before ML inference, ensuring acute emergencies are triaged safely regardless of model confidence.", space_after=3)
    add_p(doc, "2. Grounding Classifier Confidence (Niculescu-Mizil & Caruana [2]): Literature established that Naive Bayes pushes probabilities toward 0 and 1, while calibration methods can distort predictions on small datasets. ArogyaMitra labels scores as uncalibrated posterior estimates and uses exact additive log-odds to explain feature attributions.", space_after=3)
    add_p(doc, "3. Containing LLM Hallucinations (Ji et al. [6]): Generative models can fabricate medical claims. By stripping the LLM of diagnostic authority, enforcing a 20s timeout cap, and using confidence filters backed by pre-compiled templates, ArogyaMitra bounds generative behavior.", space_after=6)

    add_h2(doc, "4.7 Limitations & Threats to Validity")
    add_p(doc, "In accordance with engineering integrity standards, the known limitations of the prototype are fully disclosed (docs/KNOWN_LIMITATIONS.md):")
    add_p(doc, "1. Synthetic Source Data: The model was trained on synthetic data (304 unique rows across 41 classes). It has not been validated on real clinical EHR cohorts. No symptom severity grades exist in the dataset; symptoms are modeled as binary indicators.", space_after=2)
    add_p(doc, "2. Conditional Independence Assumption: Correlated symptoms (e.g., cough and breathlessness) double-count statistical evidence, causing confidence scores to saturate near 100%.", space_after=2)
    add_p(doc, "3. Frontline Decision Support Only: The model outputs distributions across 41 predefined classes. It is an assistive screening aid and cannot replace clinical examinations or laboratory testing.", space_after=2)
    add_p(doc, "4. Safe Mode as Usual Demo Path: Due to external Gemini API rate limits and model deprecations, Safe Mode (deterministic fallback templates) is the usual execution path during continuous testing.", space_after=2)
    add_p(doc, "5. Draft Fallback Templates: Clinical fallback templates remain labeled DRAFT pending review by a licensed medical board.", space_after=2)
    add_p(doc, "6. Self-Signed TLS Certificate: The gateway uses a self-signed certificate for arogyamitra.local, requiring explicit trust in test environments.", space_after=2)
    add_p(doc, "7. Single-Replica Stack: Runs as single-replica containers on a single host node without multi-region clustering or Kubernetes autoscaling.", space_after=2)
    add_p(doc, "8. In-Memory Rate Limiting: Rate limit counters reside in local Node.js process memory rather than a shared Redis store.", space_after=2)
    add_p(doc, "9. Offline Scope: Inference requires network connection to the local Docker gateway; fully offline in-browser execution is not yet compiled.", space_after=2)
    add_p(doc, "10. Devanagari Typography: ReportLab lacks HarfBuzz complex script shaping, causing occasional mispositioned vowel matras in Hindi and Marathi PDFs.", space_after=2)
    add_p(doc, "11. Pending Fix Round Workflows: [PENDING FIX ROUND] Consultation saving upon worker escalation, physician review queue retrieval, doctor response note logging, worker seeing reviewed status, and 401 session expiry handling represent ongoing defect-fix enhancements.", space_after=6)
