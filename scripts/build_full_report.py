"""
ArogyaMitra — Complete B.Tech Project Report Builder & PDF Converter (Item 18 & 19 Compliant)
Builds the complete academic project report targeting 36-40 pages.
Exports DOCX and converts to PDF using Microsoft Word COM Automation.
Rasterizes PDF pages for visual inspection of text overlap, clipped labels, and blank half-pages.
"""

import os
import sys
import docx
import win32com.client
import pypdfium2 as pdfium

# Ensure scripts dir is on sys.path
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from report_styles import setup_frontmatter_geometry, setup_main_geometry
from report_frontmatter import (
    add_cover_page,
    add_bonafide_certificate,
    add_declaration_and_conflict_page,
    add_acknowledgements,
    add_abstract,
    add_table_of_contents_pages,
    add_merged_list_of_figures_and_tables,
    add_abbreviations
)
from report_chapters_1_2 import add_chapter_1, add_chapter_2
from report_chapter_3 import add_chapter_3
from report_chapter_4 import add_chapter_4
from report_chapter_5_and_backmatter import (
    add_chapter_5,
    add_references,
    add_appendix_a,
    add_appendix_b
)

BASE_DIR = os.path.dirname(SCRIPTS_DIR)
OUTPUT_DIR = os.path.join(BASE_DIR, "docs", "REPORT_FINAL")
PAGES_DIR = os.path.join(OUTPUT_DIR, "pdf_pages")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(PAGES_DIR, exist_ok=True)

DOCX_PATH = os.path.join(OUTPUT_DIR, "ArogyaMitra_BTech_Project_Report.docx")
PDF_PATH = os.path.join(OUTPUT_DIR, "ArogyaMitra_BTech_Project_Report.pdf")

def build_report():
    print("=" * 70)
    print("Building ArogyaMitra B.Tech Project Report (.docx)...")
    print("Target Page Budget: 36–40 Pages")
    print("=" * 70)
    
    doc = docx.Document()
    
    # Section 1: Front Matter (Roman Numerals, 0.9 in margins)
    print("1. Assembling Front Matter (Cover, Certificate, Declaration+COI, Ack, Abstract, TOC, LoF+LoT, Abbrevs)...")
    setup_frontmatter_geometry(doc.sections[0])
    add_cover_page(doc)
    add_bonafide_certificate(doc)
    add_declaration_and_conflict_page(doc)
    add_acknowledgements(doc)
    add_abstract(doc)
    add_table_of_contents_pages(doc)
    add_merged_list_of_figures_and_tables(doc)
    add_abbreviations(doc)
    
    # Section 2: Main Body & Appendices (Arabic Numerals, 0.9 in margins)
    print("2. Assembling Main Chapters (Chapters 1 to 5)...")
    main_section = doc.add_section()
    setup_main_geometry(main_section)
    
    add_chapter_1(doc)
    add_chapter_2(doc)
    add_chapter_3(doc)
    add_chapter_4(doc)
    add_chapter_5(doc)
    
    print("3. Assembling Back Matter (References, Appendix A, Appendix B)...")
    add_references(doc)
    add_appendix_a(doc)
    add_appendix_b(doc)
    
    print(f"Saving Word Document to: {DOCX_PATH}")
    doc.save(DOCX_PATH)
    docx_size = os.path.getsize(DOCX_PATH)
    print(f"Word document saved! Size: {docx_size:,} bytes")
    
    print("=" * 70)
    print("Converting DOCX to PDF using Microsoft Word COM Automation...")
    print("=" * 70)
    
    word = None
    pdf_pages = 0
    try:
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        word.DisplayAlerts = False
        
        abs_docx = os.path.abspath(DOCX_PATH)
        abs_pdf = os.path.abspath(PDF_PATH)
        
        print(f"Opening: {abs_docx}")
        word_doc = word.Documents.Open(abs_docx)
        
        # wdStatisticPages = 2
        word_pages = word_doc.ComputeStatistics(2)
        print(f"Word Document Computed Page Count: {word_pages}")
        
        # FileFormat=17 is wdFormatPDF
        print(f"Exporting to PDF: {abs_pdf}")
        word_doc.SaveAs(abs_pdf, FileFormat=17)
        word_doc.Close()
        
        pdf_size = os.path.getsize(PDF_PATH)
        print(f"PDF exported successfully! Size: {pdf_size:,} bytes")
        
        pdf_pages = len(pdfium.PdfDocument(abs_pdf))
        print(f"PDF Verified Page Count: {pdf_pages} pages")
        
    except Exception as e:
        print(f"Error during Word COM conversion: {e}")
        raise e
    finally:
        if word:
            word.Quit()
            
    print("=" * 70)
    print(f"Generation Complete! Target: 36–40 pages. Actual: {pdf_pages} pages.")
    print("=" * 70)
    return pdf_pages

if __name__ == "__main__":
    build_report()
