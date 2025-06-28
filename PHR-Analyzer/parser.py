
import re
import pdfplumber

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts and returns text from a PDF file.
    
    Args:
        file_path (str): Path to the PDF file.

    Returns:
        str: Extracted plain text.
    """
    full_text = ""
    
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
    
    return full_text.strip()

def clean_report_text(raw_text: str) -> str:
    """
    Cleans up raw text extracted from a PDF.
    Removes excessive whitespace and unwanted artifacts.

    Args:
        raw_text (str): The raw extracted text.

    Returns:
        str: Cleaned text.
    """
    # Remove repeated spaces and newlines
    cleaned = re.sub(r'\n+', '\n', raw_text)         # Remove multiple newlines
    #cleaned = re.sub(r'\s{2,}', ' ', cleaned)        # Replace multiple spaces with one
    return cleaned.strip()





