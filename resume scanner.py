
import os
import pypdf
from pdf2image import convert_from_path
import pytesseract


class ResumePDFScanner:
    """Extracts text from PDF resumes, supporting native text and OCR."""

    @staticmethod
    def extract_text_native(pdf_path: str) -> str:
        """Extract text directly from searchable PDF documents."""

        reader = pypdf.PdfReader(pdf_path)

        extracted_text = ""

        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()

            if text:
                extracted_text += text + "\n"

        return extracted_text.strip()

    @staticmethod
    def extract_text_with_ocr(pdf_path: str, dpi: int = 300) -> str:
        """Convert PDF pages to images and extract text using OCR."""

        images = convert_from_path(pdf_path, dpi=dpi)

        ocr_text = ""

        for page_num, image in enumerate(images):
            text = pytesseract.image_to_string(image)
            ocr_text += text + "\n"

        return ocr_text.strip()

    def scan_resume(self, pdf_path: str) -> str:
        """Automatically use native extraction, falling back to OCR."""

        if not os.path.exists(pdf_path):
            raise FileNotFoundError(
                f"PDF file not found at: {pdf_path}"
            )

        # Step 1: Attempt native extraction
        native_text = self.extract_text_native(pdf_path)

        # Step 2: Fall back to OCR if insufficient text
        if len(native_text) < 50:
            print(
                "Notice: Low native text detected. "
                "Switching to OCR fallback..."
            )

            return self.extract_text_with_ocr(pdf_path)

        return native_text


# Example usage

if __name__ == "__main__":

    scanner = ResumePDFScanner()

    # Ask user for a PDF path
    target_pdf = input("Enter the path to the resume PDF: ").strip().strip('"')

    try:
        resume_text = scanner.scan_resume(target_pdf)

        print("\n--- Successfully Extracted Resume Text ---")
        print(resume_text)

    except Exception as e:
        print(f"Error scanning resume: {e}")

