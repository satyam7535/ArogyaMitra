import pypdfium2 as pdfium
import re

pdf_path = 'docs/REPORT_FINAL/ArogyaMitra_BTech_Project_Report.pdf'
pdf = pdfium.PdfDocument(pdf_path)
full_text = ''
for i, page in enumerate(pdf):
    text = page.get_textpage().get_text_range()
    full_text += f'\n--- Page {i+1} ---\n' + text

print(f'Total Pages: {len(pdf)}')

banned = ['ZZTest', 'TEST-', 'Diagram ', 'AssistedPrimary', 'Latenc y', '(None)']
print('=== BANNED STRINGS CHECK ===')
for b in banned:
    matches = [m.start() for m in re.finditer(re.escape(b), full_text)]
    print(f'{b}: {len(matches)} occurrences')

print('\n=== KEY EMPIRICAL NUMBERS CHECK ===')
checks = [
    '322',
    '20/20',
    '11/11',
    '0.919',
    '0.683',
    '14.7 req/s',
    '193.0 ms',
    '76.2 ms',
    '0.0061',
    '0.1643',
    '0 fixable'
]
for c in checks:
    count = full_text.count(c)
    print(f'"{c}": {count} occurrences')

print('\n=== PLACEHOLDERS CHECK ===')
placeholders = ['[CONFIRM TITLE]', '[CONFIRM HOD NAME]', '[CONFIRM DIRECTOR NAME]']
for p in placeholders:
    count = full_text.count(p)
    print(f'"{p}": {count} occurrences')
