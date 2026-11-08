import pypdf
import re

# extracted all text from resume (pdf file)
def extract_pdf_text(pdf_path):
    text = "" # store the text scanned
    reader = pypdf.PdfReader(pdf_path) # read the pdf file
    for page in reader.pages: # scanned all pages
        page_text = page.extract_text()
        if page_text: # check if text is available for extract and add into text file
            text += page_text + "\n" # add new line to separate teh content from different page
    return text #return the text file of scanned resume

# clean the extracted text
def clean_text(text):
    # Remove spaces
    text = re.sub(r'[ \t]+', ' ', text)
    # Remove blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip() # remove the whitespace

# scan the resume
def scan_resume(pdf_path):
    text = extract_pdf_text(pdf_path) #extrac the text from extracted text
    text = clean_text(text) #clean the extracted text to improve the readability
    return text

if __name__ == "__main__":
    pdf_path = input("Your resume: ") #type the file name (including .pdf)
    resume_text = scan_resume(pdf_path) # scan & extracted cleaned text
    print("-------------- EXTRACTED RESUME -------------\n")
    print(resume_text)
    # Save extracted text in different txt file
    with open("resume_extracted.txt", "w", encoding="utf-8") as file:
        file.write(resume_text) # write extracted text into txt file
    print("\nResume extraction completed!") # print to confirm the saving is successful