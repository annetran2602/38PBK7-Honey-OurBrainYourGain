import os
import pypdf
from pdf2image import convert_from_path
import pytesseract


class ResumePDFScanner:
    """Extracts text from PDF resumes, supporting both native text and scanned images (OCR)."""

    @staticmethod
    def extract_text_native(pdf_path: str) -> str:
        """Extracts text directly from digital/searchable PDF documents."""
        reader = pypdf.PdfReader(pdf_path)
        extracted_text = ""
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                extracted_text += text + "\n"
        return extracted_text.strip()

    @staticmethod
    def extract_text_with_ocr(pdf_path: str, dpi: int = 300) -> str:
        """Converts PDF pages into images and runs OCR for non-searchable/scanned resumes."""
        images = convert_from_path(pdf_path, dpi=dpi)
        ocr_text = ""
        for page_num, image in enumerate(images):
            text = pytesseract.image_to_string(image)
            ocr_text += text + "\n"
        return ocr_text.strip()

    def scan_resume(self, pdf_path: str) -> str:
        """Automatically attempts native extraction; falls back to OCR if little/no text is found."""
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found at: {pdf_path}")

        # Step 1: Try native text extraction
        native_text = self.extract_text_native(pdf_path)

        # Verification: If native text yields fewer than 50 characters, it's likely a scanned image PDF
        if len(native_text) < 50:
            print("Notice: Low native text detected. Switching to OCR fallback...")
            ocr_text = self.extract_text_with_ocr(pdf_path)
            return ocr_text

        return native_text


# ---------------------------------------------------------------------------
# EXAMPLE USAGE
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    scanner = ResumePDFScanner()

    # Replace with the path to your target resume PDF
    target_pdf = "sample_resume.pdf"

    try:
        resume_text = scanner.scan_resume(target_pdf)
        print("--- Successfully Extracted Resume Text ---")
        print(resume_text[:500])  # Print first 500 characters as verification
    except Exception as e:
        print(f"Error scanning resume: {e}")