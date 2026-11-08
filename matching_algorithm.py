
import pypdf
import os
import json
import re

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# Initialize Gemini client
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# Extract resume text from PDF
def extract_pdf_text(pdf_path):

    text = ""

    reader = pypdf.PdfReader(pdf_path)

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


# Clean extracted resume text
def clean_text(text):

    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()


# Analyze resume against job description
def match_resume(resume_text, job_description):

    prompt = f"""
    You are an expert recruitment and resume analysis assistant.

    Analyze the candidate's resume against the job description.

    IMPORTANT:
    This system must work for ALL industries and occupations,
    not just Computer Science or Data Science.

    Evaluate these categories:

    1. Skills
    2. Education
    3. Work Experience
    4. Responsibilities
    5. Certifications and Qualifications
    6. Relevant Projects and Achievements

    Instructions:

    - Dynamically identify requirements from the job description.
    - Do not use hardcoded industry-specific skills.
    - Identify matching and missing qualifications.
    - Recognize transferable skills.
    - Distinguish mandatory from preferred requirements.
    - Do not invent experience or qualifications.
    - Mark unavailable information as unknown.
    - Provide evidence from the resume for each match.
    - Consider the importance of each job requirement.
    - Calculate a reasonable overall match score from 0 to 100.
    - Explain the reasoning behind the score.

    RESUME:
    {resume_text}

    JOB DESCRIPTION:
    {job_description}

    Return valid JSON with this structure:

    {{
        "job_title": "",
        "overall_match_score": 0,
        "categories": {{
            "skills": {{
                "score": 0,
                "matched": [],
                "missing": []
            }},
            "education": {{
                "score": 0,
                "matched": [],
                "missing": []
            }},
            "experience": {{
                "score": 0,
                "matched": [],
                "missing": []
            }},
            "responsibilities": {{
                "score": 0,
                "matched": [],
                "missing": []
            }},
            "certifications": {{
                "score": 0,
                "matched": [],
                "missing": []
            }},
            "projects_and_achievements": {{
                "score": 0,
                "matched": [],
                "missing": []
            }}
        }},
        "transferable_skills": [],
        "strengths": [],
        "areas_for_improvement": [],
        "recommendation": "",
        "score_explanation": ""
    }}
    """

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2
        )
    )

    result = response.text

    return json.loads(result)


# Main program
if __name__ == "__main__":

    pdf_path = "resume.pdf"

    # Extract resume
    resume_text = extract_pdf_text(pdf_path)

    resume_text = clean_text(resume_text)

    if not resume_text:
        raise ValueError(
            "No text found in PDF. The PDF may require OCR."
        )

    # Get job description
    job_description = input(
        "Paste the job description: "
    )

    if not job_description.strip():
        raise ValueError("Job description cannot be empty.")

    # Compare resume and job
    try:

        results = match_resume(
            resume_text,
            job_description
        )

        print("\n========== RESUME MATCH RESULTS ==========\n")

        print(json.dumps(
            results,
            indent=4,
            ensure_ascii=False
        ))

        # Save results
        with open(
            "match_results.json",
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                results,
                file,
                indent=4,
                ensure_ascii=False
            )

        print("\nResults saved to match_results.json")

    except Exception as e:

        print(f"Error analyzing resume: {e}")
