"""
Inspect exact page numbers of all headings, tables, and figures in the generated PDF using pypdfium2.
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')
import pypdfium2 as pdfium

pdf = pdfium.PdfDocument('docs/REPORT_FINAL/ArogyaMitra_BTech_Project_Report.pdf')
print(f"Total Pages in PDF: {len(pdf)}")

targets = [
    "BONAFIDE CERTIFICATE", "DECLARATION", "ACKNOWLEDGEMENTS", "ABSTRACT",
    "TABLE OF CONTENTS", "LIST OF FIGURES", "LIST OF TABLES", "LIST OF ABBREVIATIONS",
    "Chapter 1:", "Chapter 2:", "Chapter 3:", "Chapter 4:", "Chapter 5:",
    "References", "Appendix A:", "Appendix B:",
    "1.1 Motivation", "1.2 Comprehensive", "1.2.1 Review", "1.2.2 Comparison",
    "1.3 Problem Statement", "1.4 Design Evolution", "1.5 Report Outline",
    "2.1 Functional Requirements", "2.2 Non-Functional", "2.3 Threat Model", "2.4 Clinical Safety",
    "3.1 Architectural Overview", "3.2 Machine Learning", "3.2.1 Bernoulli", "3.2.2 Feature Engineering",
    "3.2.3 Explainability", "3.2.4 Calibration", "3.2.5 Comparative Model",
    "3.3 Rule-Based", "3.4 Multi-Tier LLM", "3.5 End-to-End", "3.6 Security Architecture",
    "3.7 Database Design", "3.8 Logging and Audit",
    "4.1 Dataset Profile", "4.2 Machine Learning Performance", "4.3 Load Testing",
    "4.4 Automated Testing", "4.5 Security Vulnerability", "4.6 Literature-Linked", "4.7 Limitations",
    "5.1 Project Summary", "5.2 Lessons Learned", "5.3 Future Work",
    "Table 1.1", "Table 1.2", "Table 2.1", "Table 2.2", "Table 2.3",
    "Table 3.1", "Table 3.2", "Table 4.1", "Table 4.2", "Table 4.3", "Table 4.4", "Table 4.5", "Table 4.6", "Table A.1",
    "Figure 3.1", "Figure 3.2", "Figure 3.3", "Figure 4.1", "Figure 4.2", "Figure 4.3", "Figure 4.4", "Figure 4.5"
]

found_items = []

for idx, page in enumerate(pdf):
    page_num = idx + 1
    textpage = page.get_textpage()
    page_text = textpage.get_text_range()
    
    # Check if page is blank
    if len(page_text.strip()) == 0:
        print(f"Page {page_num} is BLANK!")
        
    lines = [l.strip() for l in page_text.split('\r\n') if l.strip()]
    if not lines:
        lines = [l.strip() for l in page_text.split('\n') if l.strip()]
        
    # Skip TOC pages from registering targets as headings
    if page_num in [6, 7, 8]:
        continue

    for line in lines:
        for target in targets:
            if target.lower() in line.lower():
                if not any(item[0] == target for item in found_items):
                    found_items.append((target, page_num, line[:60]))

print("\n=== EXTRACTED PAGE LOCATIONS ===")
for target, pnum, sample in found_items:
    print(f"{target:<35} -> Page {pnum:<3} | Sample: {sample}")
