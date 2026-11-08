
import ollama
import json


def match_resume_to_job(resume_text, job_description):

    prompt = f"""
You are an AI recruitment assistant.

Your task is to compare a candidate's resume against a
job description and evaluate how well the candidate
matches the position.

Analyze these categories:

1. Technical and transferable skills
2. Education and academic qualifications
3. Work experience
4. Job responsibilities
5. Certifications and professional qualifications
6. Projects and achievements

IMPORTANT RULES:

- Evaluate the candidate based ONLY on information in the resume.
- Never invent skills, experience, education or certifications.
- Distinguish required qualifications from preferred qualifications.
- A qualification not mentioned in the resume should be
  considered unknown or missing, not automatically absent.
- Include evidence from the resume for matching qualifications.
- Identify transferable skills where relevant.
- Consider all industries and job types.
- Give a realistic match score between 0 and 100.
- Explain why the candidate received that score.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Return ONLY valid JSON using this structure:

{{
    "match_score": 0,
    "overall_assessment": "Overall evaluation",

    "matching_qualifications": [
        {{
            "requirement": "Job requirement",
            "resume_evidence": "Evidence from resume",
            "match": "Strong"
        }}
    ],

    "missing_qualifications": [
        {{
            "requirement": "Job requirement",
            "importance": "Required",
            "reason": "Why this qualification is missing or unverified"
        }}
    ],

    "skills_match": [
        "Relevant skill"
    ],

    "experience_analysis": "Experience comparison",

    "education_analysis": "Education comparison",

    "recommendations": [
        "Recommendation for the candidate"
    ]
}}

The match_score must be an integer between 0 and 100.

If a category has no findings, return an empty list.
Do not include Markdown code fences.
"""

    try: # request ollama to process the prompt

        response = ollama.chat(
            model="llama3.2", #model of ollama
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            format="json",
            options={
                "temperature": 0.2 # how consistent the answer is to the given prompt
            }
        )

        result = json.loads( # Forces the model to return its response in JSON format
            response["message"]["content"]
        )

        return result #return as the parsed JSON data

    except json.JSONDecodeError:
        raise ValueError(
            "Ollama returned an invalid JSON response." #handle the invalid prompt
        )

    except Exception as e:
        raise RuntimeError(
            f"Error communicating with Ollama: {e}"
        )
