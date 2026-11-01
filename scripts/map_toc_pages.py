import os
import pypdfium2 as pdfium

PDF_PATH = "docs/REPORT_FINAL/ArogyaMitra_BTech_Project_Report.pdf"
pdf = pdfium.PdfDocument(PDF_PATH)

# Main section starts on PDF page 9, which is Arabic page 1.
# So Arabic page = PDF_page - 8.
def to_arabic(pdf_idx):
    return str(pdf_idx - 8 + 1)

toc_queries = [
    # (TOC display title, search phrase, is_frontmatter, roman_val)
    ("Bonafide Certificate", "BONAFIDE CERTIFICATE", True, "ii"),
    ("Declaration & Conflict of Interest", "DECLARATION & PLAGIARISM", True, "iii"),
    ("Acknowledgements", "ACKNOWLEDGEMENTS", True, "iv"),
    ("Abstract", "ABSTRACT", True, "v"),
    ("List of Figures & List of Tables", "LIST OF FIGURES", True, "vi"),
    ("List of Abbreviations", "LIST OF ABBREVIATIONS", True, "vii"),
    ("Chapter 1: Introduction & Literature Review", "Chapter 1: Introduction", False, ""),
    ("    1.1 Motivation & Primary Healthcare Challenges in Rural India", "1.1 Motivation", False, ""),
    ("    1.2 Comprehensive Literature Review", "1.2 Comprehensive Literature Review", False, ""),
    ("        1.2.1 Review of Symptom Checkers, Decision Support, and Calibration", "1.2.1 Review of Symptom Checkers", False, ""),
    ("        1.2.2 Comparison with Existing Work", "1.2.2 Comparison with Existing Work", False, ""),
    ("    1.3 Problem Statement & Design Objectives", "1.3 Problem Statement", False, ""),
    ("    1.4 Design Evolution", "1.4 Design Evolution", False, ""),
    ("    1.5 Report Outline & Organization", "1.5 Report Outline", False, ""),
    ("Chapter 2: System Requirements & Threat Modeling", "Chapter 2: System Requirements", False, ""),
    ("    2.1 Functional Requirements (FR-1 to FR-10)", "2.1 Functional Requirements", False, ""),
    ("    2.2 Non-Functional Requirements (NFR-1 to NFR-8)", "2.2 Non-Functional Requirements", False, ""),
    ("    2.3 Threat Model & Security Analysis (STRIDE Matrix)", "2.3 Threat Model", False, ""),
    ("    2.4 Clinical Safety & Ethics Requirements", "2.4 Clinical Safety", False, ""),
    ("Chapter 3: System Architecture & Design", "Chapter 3: System Architecture", False, ""),
    ("    3.1 Architectural Overview & Container Topology", "3.1 Architectural Overview", False, ""),
    ("    3.2 Machine Learning Inference & Calibration Engine", "3.2 Machine Learning Inference", False, ""),
    ("        3.2.1 Bernoulli Naive Bayes Mathematical Formulation", "3.2.1 Bernoulli Naive Bayes", False, ""),
    ("        3.2.2 Feature Engineering & Vocabulary Alignment", "3.2.2 Feature Engineering", False, ""),
    ("        3.2.3 Explainability via Top-Feature Attribution", "3.2.3 Explainability", False, ""),
    ("        3.2.4 Calibration Theoretical Background & Analysis", "3.2.4 Calibration Theoretical Background", False, ""),
    ("        3.2.5 Comparative Model Selection", "3.2.5 Comparative Model Selection", False, ""),
    ("    3.3 Rule-Based Clinical Red-Flag Override System", "3.3 Rule-Based Clinical Red-Flag", False, ""),
    ("    3.4 Multi-Tier LLM Explanation & Resilient Fallback Layer", "3.4 Multi-Tier LLM Explanation", False, ""),
    ("    3.5 End-to-End Clinical Consultation Workflow", "3.5 End-to-End Clinical Consultation", False, ""),
    ("        3.5.1 Verified Clinical Workflow Demonstration", "3.5.1 Verified Clinical Workflow", False, ""),
    ("    3.6 Security Architecture & Cryptographic Implementation", "3.6 Security Architecture", False, ""),
    ("    3.7 Database Design, Concurrency & Data Integrity", "3.7 Database Design", False, ""),
    ("    3.8 Logging and Audit System", "3.8 Logging and Audit System", False, ""),
    ("Chapter 4: Empirical Evaluation & Experimental Results", "Chapter 4: Empirical Evaluation", False, ""),
    ("    4.1 Dataset Profile & Methodological Integrity", "4.1 Dataset Profile", False, ""),
    ("    4.2 Machine Learning Performance & Robustness", "4.2 Machine Learning Performance", False, ""),
    ("    4.3 Load Testing, Concurrency & System Throughput", "4.3 Load Testing", False, ""),
    ("    4.4 Automated Testing & Verification Suite", "4.4 Automated Testing", False, ""),
    ("    4.5 Security Vulnerability & Dependency Auditing", "4.5 Security Vulnerability", False, ""),
    ("    4.6 Literature-Linked Discussion & Analysis", "4.6 Literature-Linked Discussion", False, ""),
    ("    4.7 Limitations & Threats to Validity", "4.7 Limitations", False, ""),
    ("Chapter 5: Conclusion & Future Scope", "Chapter 5: Conclusion", False, ""),
    ("    5.1 Project Summary & Achievements", "5.1 Project Summary", False, ""),
    ("    5.2 Lessons Learned & Engineering Insights", "5.2 Lessons Learned", False, ""),
    ("    5.3 Future Work & Roadmap", "5.3 Future Work", False, ""),
    ("References", "References", False, ""),
    ("Appendix A: Engineering Challenges, Root Causes, and Architectural Fixes", "Appendix A:", False, ""),
    ("Appendix B: Reproduction Commands Playbook", "Appendix B:", False, ""),
]

figure_queries = [
    ("Figure 3.1", "Figure 3.1: Container Topology"),
    ("Figure 3.2", "Figure 3.2: Consultation Lifecycle"),
    ("Figure 3.3", "Figure 3.3: Hierarchical Request Timeout"),
    ("Figure 3.4", "Figure 3.4: Verified End-to-End Clinical Workflow"),
    ("Figure 4.1", "Figure 4.1: Dataset Provenance"),
    ("Figure 4.2", "Figure 4.2: Top-1 Accuracy and Expected Calibration Error"),
    ("Figure 4.3", "Figure 4.3: Gateway Throughput"),
    ("Figure 4.4", "Figure 4.4: Worker List Latency"),
]

table_queries = [
    ("Table 1.1", "Table 1.1: Comprehensive Literature Review"),
    ("Table 1.2", "Table 1.2: Systematic Comparison"),
    ("Table 2.1", "Table 2.1: System Functional Requirements"),
    ("Table 2.2", "Table 2.2: System Non-Functional Requirements"),
    ("Table 2.3", "Table 2.3: STRIDE Threat Model"),
    ("Table 3.1", "Table 3.1: Container Technology Stack"),
    ("Table 3.2", "Table 3.2: Emergency Red-Flag Trigger Symptoms"),
    ("Table 4.1", "Table 4.1: Repeated Stratified 5x3 Cross-Validation"),
    ("Table 4.2", "Table 4.2: Expected Calibration Error"),
    ("Table 4.3", "Table 4.3: Load Test Benchmark Results"),
    ("Table 4.4", "Table 4.4: Worker List Latency Before vs. After"),
    ("Table 4.5", "Table 4.5: Automated Test Suite Summary"),
    ("Table 4.6", "Table 4.6: OWASP ZAP Dynamic Security"),
    ("Table A.1", "Table A.1: Engineering Challenges"),
]

print("=== TOC MAPPINGS ===")
final_toc = []
for title, search_str, is_front, roman in toc_queries:
    if is_front:
        final_toc.append((title, roman))
        print(f"('{title}', '{roman}'),")
    else:
        found_arabic = None
        for i in range(8, len(pdf)):
            page_text = pdf[i].get_textpage().get_text_range()
            if search_str.lower() in page_text.lower():
                found_arabic = to_arabic(i)
                break
        final_toc.append((title, found_arabic or "?"))
        print(f"('{title}', '{found_arabic}'),")

print("\n=== FIGURE MAPPINGS ===")
for fig_id, search_str in figure_queries:
    found_arabic = None
    for i in range(8, len(pdf)):
        page_text = pdf[i].get_textpage().get_text_range()
        if search_str.lower() in page_text.lower():
            found_arabic = to_arabic(i)
            break
    print(f"('{fig_id}', '{found_arabic}'),")

print("\n=== TABLE MAPPINGS ===")
for tbl_id, search_str in table_queries:
    found_arabic = None
    for i in range(8, len(pdf)):
        page_text = pdf[i].get_textpage().get_text_range()
        if search_str.lower() in page_text.lower():
            found_arabic = to_arabic(i)
            break
    print(f"('{tbl_id}', '{found_arabic}'),")
