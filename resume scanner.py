import pypdf
import re


def extract_pdf_text(pdf_path):
    """Extract text from every page of a PDF resume."""

    text = ""

    reader = pypdf.PdfReader(pdf_path)

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


def clean_text(text):
    """Clean extracted resume text."""

    # Remove excessive spaces
    text = re.sub(r'[ \t]+', ' ', text)

    # Remove excessive blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()


def scan_resume(pdf_path):
    """Scan and clean resume."""

    text = extract_pdf_text(pdf_path)
    text = clean_text(text)

    return text


if __name__ == "__main__":

    pdf_path = input("Your resume: ")

    resume_text = scan_resume(pdf_path)

    print("========== EXTRACTED RESUME ==========\n")
    print(resume_text)

    # Save extracted text
    with open("resume_extracted.txt", "w", encoding="utf-8") as file:
        file.write(resume_text)

    print("\nResume extraction completed!")