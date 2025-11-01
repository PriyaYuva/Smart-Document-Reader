# ocr_utils.py
import tempfile
import fitz  # PyMuPDF
import easyocr
import io
from typing import List


def extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    """
    Tries to extract selectable text from a PDF using PyMuPDF first.
    If that fails or returns empty, falls back to EasyOCR for image/scan OCR.
    Returns the extracted text as a single string.
    """
    text = ""
    # Try PDF text extraction first (faster and cleaner)
    if filename.lower().endswith(".pdf"):
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            pages = []
            for page in doc:
                pages.append(page.get_text("text"))
            text = "\n".join(pages).strip()
            if text:
                return text
        except Exception:
            # fall through to OCR
            pass

    # For images or scanned PDFs: use EasyOCR
    reader = easyocr.Reader(["en"], gpu=False)  # set gpu=True if GPU available
    with tempfile.NamedTemporaryFile(suffix=filename, delete=False) as tmp:
        tmp.write(file_bytes)
        tmp.flush()
        result = reader.readtext(tmp.name, detail=0)
        text = "\n".join(result).strip()
    return text
