

from parser import extract_text_from_pdf, clean_report_text
from analyzer import analyze_report

file_path = "PHR Analyzer/report2.pdf"
raw_text = extract_text_from_pdf(file_path)
cleaned_text = clean_report_text(raw_text)

result = analyze_report(cleaned_text)

print(result.strip())
