
import requests
import os
from dotenv import load_dotenv

from matching_algorithm import match_resume_to_job
from resume_scanner import scan_resume

load_dotenv()

# searching the job based on the prompt using Adzuna API
def search_jobs(job_type, location="Calgary", results_per_page=10):
    url = "https://api.adzuna.com/v1/api/jobs/ca/search/1"
    params = {
        # from env file
        "app_id": os.getenv("ADZUNA_APP_ID"),
        "app_key": os.getenv("ADZUNA_APP_KEY"),
        "what": job_type,
        "where": location,
        "results_per_page": results_per_page
    }

    if not params["app_id"] or not params["app_key"]: # check if API key is valid
        raise ValueError("Missing Adzuna API credentials in .env")

    try:
        response = requests.get( # send a get request to search the job
            url,
            params=params,
            timeout=60 # will stop if API take more than 60s to run
        )
        response.raise_for_status() # Check the status of the request
        data = response.json()  # convert to python dict
        return data.get("results", [])
    except requests.exceptions.RequestException as e: # if unsuccessful, raise exception
        raise RuntimeError(f"Adzuna API error: {e}")

def analyze_resume(pdf_path):

    resume_text = scan_resume(pdf_path) # scan the resume & convert into text

    if not resume_text:
        raise ValueError("Unable to extract text from resume.")

    return resume_text

def match_jobs_to_resume(resume_text, jobs):
    matched_jobs = []

    for job in jobs:

        title = job.get("title", "N/A")
        company = job.get(
            "company", {}
        ).get("display_name", "N/A")
        description = job.get(
            "description",
            "No description available"
        )
        link = job.get("redirect_url", "N/A")

        try:
            results = match_resume_to_job(
                resume_text,
                description
            )
            score = float(results["match_score"])

            missing_skills = [
                item.get("requirement", "")
                for item in results.get(
                    "missing_qualifications", []
                )
            ]
            matched_jobs.append({
                "title": title,
                "company": company,
                "link": link,
                "description": description,
                "score": score,

                "summary": results.get(
                    "overall_assessment",
                    "No assessment available"),

                "missing_skills": missing_skills,

                "matching_qualifications": results.get(
                    "matching_qualifications", []),

                "missing_qualifications": results.get(
                    "missing_qualifications", []),

                "skills_match": results.get(
                    "skills_match", []),

                "experience_analysis": results.get(
                    "experience_analysis", ""),

                "education_analysis": results.get(
                    "education_analysis", ""),

                "recommendations": results.get(
                    "recommendations", [])
            })

        except Exception as e:
            print(f"Error matching {title}: {e}")
    matched_jobs.sort(
        key=lambda job: job["score"],
        reverse=True
    )
    return matched_jobs

def search_and_match_jobs(
    resume_text,
    job_type,
    location="Calgary",
    results_per_page=10
):
    jobs = search_jobs(
        job_type,
        location,
        results_per_page
    )
    if not jobs:
        return []

    matched_jobs = match_jobs_to_resume(
        resume_text,
        jobs
    )
    return matched_jobs
