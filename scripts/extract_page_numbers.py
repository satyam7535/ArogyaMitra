import os
import pypdfium2 as pdfium

PDF_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "REPORT_FINAL", "ArogyaMitra_BTech_Project_Report.pdf")

pdf = pdfium.PdfDocument(PDF_PATH)
print(f"Total pages: {len(pdf)}")

items_to_find = [
    # Frontmatter
    ("Bonafide Certificate", "BONAFIDE CERTIFICATE"),
    ("Declaration & Conflict of Interest", "DECLARATION & PLAGIARISM"),
    ("Acknowledgements", "ACKNOWLEDGEMENTS"),
    ("Abstract", "ABSTRACT"),
    ("List of Figures & List of Tables", "LIST OF FIGURES"),
    ("List of Abbreviations", "LIST OF ABBREVIATIONS"),
    # Chapters
    ("Chapter 1: Introduction & Literature Review", "Chapter 1: Introduction"),
    ("1.1 Motivation", "1.1 Motivation"),
    ("1.2 Comprehensive Literature Review", "1.2 Comprehensive Literature Review"),
    ("1.2.1 Review of Symptom Checkers", "1.2.1 Review of Symptom Checkers"),
    ("1.2.2 Comparison with Existing Work", "1.2.2 Comparison with Existing Work"),
    ("1.3 Problem Statement & Design Objectives", "1.3 Problem Statement"),
    ("1.4 Design Evolution", "1.4 Design Evolution"),
    ("1.5 Report Outline & Organization", "1.5 Report Outline"),
    ("Chapter 2: System Requirements & Threat Modeling", "Chapter 2: System Requirements"),
    ("2.1 Functional Requirements", "2.1 Functional Requirements"),
    ("2.2 Non-Functional Requirements", "2.2 Non-Functional Requirements"),
    ("2.3 Threat Model & Security Analysis", "2.3 Threat Model"),
    ("2.4 Clinical Safety & Ethics Requirements", "2.4 Clinical Safety"),
    ("Chapter 3: System Architecture & Design", "Chapter 3: System Architecture"),
    ("3.1 Architectural Overview", "3.1 Architectural Overview"),
    ("3.2 Machine Learning Inference", "3.2 Machine Learning Inference"),
    ("3.2.1 Bernoulli Naive Bayes", "3.2.1 Bernoulli Naive Bayes"),
    ("3.2.2 Feature Engineering", "3.2.2 Feature Engineering"),
    ("3.2.3 Explainability via Top-Feature Attribution", "3.2.3 Explainability"),
    ("3.2.4 Calibration Theoretical Background", "3.2.4 Calibration Theoretical Background"),
    ("3.2.5 Comparative Model Selection", "3.2.5 Comparative Model Selection"),
    ("3.3 Rule-Based Clinical Red-Flag Override System", "3.3 Rule-Based Clinical Red-Flag"),
    ("3.4 Multi-Tier LLM Explanation", "3.4 Multi-Tier LLM Explanation"),
    ("3.5 End-to-End Clinical Consultation Workflow", "3.5 End-to-End Clinical Consultation"),
    ("3.5.1 Verified Clinical Workflow Demonstration", "3.5.1 Verified Clinical Workflow"),
    ("3.6 Security Architecture & Cryptographic Implementation", "3.6 Security Architecture"),
    ("3.7 Database Design, Concurrency & Data Integrity", "3.7 Database Design"),
    ("3.8 Logging and Audit System", "3.8 Logging and Audit System"),
    ("Chapter 4: Empirical Evaluation & Experimental Results", "Chapter 4: Empirical Evaluation"),
    ("4.1 Dataset Profile & Methodological Integrity", "4.1 Dataset Profile"),
    ("4.2 Machine Learning Performance & Robustness", "4.2 Machine Learning Performance"),
    ("4.3 Load Testing, Concurrency & System Throughput", "4.3 Load Testing"),
    ("4.4 Automated Testing & Verification Suite", "4.4 Automated Testing"),
    ("4.5 Security Vulnerability & Dependency Auditing", "4.5 Security Vulnerability"),
    ("4.6 Literature-Linked Discussion & Analysis", "4.6 Literature-Linked Discussion"),
    ("4.7 Limitations & Threats to Validity", "4.7 Limitations"),
    ("Chapter 5: Conclusion & Future Scope", "Chapter 5: Conclusion"),
    ("5.1 Project Summary & Achievements", "5.1 Project Summary"),
    ("5.2 Lessons Learned & Engineering Insights", "5.2 Lessons Learned"),
    ("5.3 Future Work & Roadmap", "5.3 Future Work"),
    ("References", "References"),
    ("Appendix A", "Appendix A:"),
    ("Appendix B", "Appendix B:"),
    # Figures
    ("Figure 3.1", "Figure 3.1"),
    ("Figure 3.2", "Figure 3.2"),
    ("Figure 3.3", "Figure 3.3"),
    ("Figure 3.4", "Figure 3.4"),
    ("Figure 4.1", "Figure 4.1"),
    ("Figure 4.2", "Figure 4.2"),
    ("Figure 4.3", "Figure 4.3"),
    ("Figure 4.4", "Figure 4.4"),
    # Tables
    ("Table 1.1", "Table 1.1"),
    ("Table 1.2", "Table 1.2"),
    ("Table 2.1", "Table 2.1"),
    ("Table 2.2", "Table 2.2"),
    ("Table 2.3", "Table 2.3"),
    ("Table 3.1", "Table 3.1"),
    ("Table 3.2", "Table 3.2"),
    ("Table 4.1", "Table 4.1"),
    ("Table 4.2", "Table 4.2"),
    ("Table 4.3", "Table 4.3"),
    ("Table 4.4", "Table 4.4"),
    ("Table 4.5", "Table 4.5"),
    ("Table 4.6", "Table 4.6"),
    ("Table A.1", "Table A.1"),
]

page_texts = []
for i, page in enumerate(pdf):
    text = page.get_textpage().get_text_range()
    page_texts.append(text)

print("\n--- LOCATIONS IN PDF ---")
for label, needle in items_to_find:
    found_pages = []
    for idx, txt in enumerate(page_texts):
        # Skip TOC page itself when searching
        if idx in [5, 6] and ("Figure" in label or "Table" in label or "1." in label or "2." in label or "3." in label or "4." in label or "5." in label or "Chapter" in label):
            continue
        if needle.lower() in txt.lower():
            # Frontmatter pages are 0 to 7 (Cover=0, Bonafide=1=ii, etc.)
            # Main section starts at index 7 (Page 1 in Arabic)
            main_start_idx = 7 # let's detect where Chapter 1 starts
            found_pages.append(idx + 1)
    print(f"{label:50} -> Pages: {found_pages}")
