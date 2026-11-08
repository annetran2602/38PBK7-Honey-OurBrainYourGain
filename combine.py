
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
            timeout=60) # will stop if API take more than 60s to run
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

# matching skills required from the job description & compare to resume
def match_jobs_to_resume(resume_text, jobs):
    matched_jobs = [] # store analyzed result from job search

    for job in jobs:

        title = job.get("title", "N/A")
        company = job.get(
            "company", {} ).get("display_name", "N/A")
        description = job.get(
            "description",
            "No description available")
        link = job.get("redirect_url", "N/A")

# AI evaluate the matching between job description and resume
        try:
            results = match_resume_to_job(
                resume_text, # resume (extracted)
                description) # job description
            # retrieved AI generated matching score & convert it into float
            score = float(results["match_score"])

            # extract the missing skill (mismatch in skills)
            missing_skills = [
                item.get("requirement", "")
                for item in results.get(
                    "missing_qualifications", [] #list contain missing skills, qualification
                )
            ]

            # Store matching job info in dictionary
            matched_jobs.append({
                "title": title,
                "company": company,
                "link": link,
                "description": description,
                "score": score,

                # The analysis of job matching while comparing with uploaded resume
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
        except Exception as e: # allow the program to continue matching with other jobs if any error occured
            print(f"Error matching {title}: {e}")
    matched_jobs.sort( # sort matching job in ascending order based on the matching score
        key=lambda job: job["score"],
        reverse=True)
    return matched_jobs # return sorted list

# combine job searching and AI resume analysis & matching
def search_and_match_jobs(
    resume_text,
    job_type,
    location="Calgary",
    results_per_page=10):
    # retrieve job posting based in requested job (job type) and location
    jobs = search_jobs(
        job_type,
        location,
        results_per_page)
    if not jobs: #  check if jobs are found/ available
        return []

    matched_jobs = match_jobs_to_resume( # compare the extracted resume and all job description
        resume_text,
        jobs)
    return matched_jobs # return the job postings rank based on the matching score
