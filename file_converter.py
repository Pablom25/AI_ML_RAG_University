import os
from typing import Optional

import pdfplumber


def _extract_text_from_pdf(uploaded_file) -> str:
    """
    Extracts text from a PDF file-like object using pdfplumber.
    """
    # Make sure we're at the beginning of the file
    uploaded_file.seek(0)

    pages_text = []
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            pages_text.append(page_text)

    # Join pages with blank lines between them
    return "\n\n".join(pages_text)


def convert_and_save(uploaded_file, output_path: str) -> Optional[str]:
    """
    Takes a Streamlit uploaded_file (or similar),
    detects if it's .txt or .pdf,
    extracts the text, and saves it as a .txt file at output_path.

    Returns the output_path if everything went well, or None if it failed.
    """
    # 1. Get the extension (".txt", ".pdf", etc.)
    _, ext = os.path.splitext(uploaded_file.name)
    ext = ext.lower()

    # 2. Read the file depending on extension
    if ext == ".txt":
        uploaded_file.seek(0)
        raw_bytes = uploaded_file.read()
        text = raw_bytes.decode("utf-8", errors="ignore")

    elif ext == ".pdf":
        try:
            text = _extract_text_from_pdf(uploaded_file)
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return None

    else:
        # For the MVP: we only accept .txt and .pdf
        print(f"Unsupported file type: {ext}")
        return None

    # 3. Save the extracted text to a .txt file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)

    return output_path
