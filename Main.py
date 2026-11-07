
import os
import time
import requests
import pandas as pd

from dotenv import load_dotenv

# Load API key
load_dotenv()
API_KEY = os.getenv("SEARCHAPI_KEY")

if not API_KEY:
    raise ValueError("Missing SEARCHAPI_KEY in .env file")

BASE_URL = "https://www.searchapi.org/api/v1/search"

# Search configuration
LOCATION = "Canada"

SEARCH_TERMS = [
    "software engineer intern",
    "software developer intern",
    "computer science intern",
    "software engineering internship",
    "IT intern",
    "technology intern",
    "programming intern",
    "developer co-op",
    "software developer co-op"
]

# API request helper
def api_request(params):
    params["api_key"] = API_KEY

    response = requests.get(
        BASE_URL,
        params=params,
        timeout=30
    )

    response.raise_for_status()
    return response.json()


# Search LinkedIn jobs
def search_jobs():
    all_jobs = []

    for term in SEARCH_TERMS:
        print(f"\nSearching: {term}")

        for page in range(1, 96):

            params = {
                "engine": "linkedin_jobs",
                "q": term,
                "location": LOCATION,
                "page": page
            }

            data = api_request(params)
            jobs = data.get("jobs", [])

            if not jobs:
                break

            all_jobs.extend(jobs)

            print(f"Page {page}: {len(jobs)} jobs")

            time.sleep(0.3)

    return all_jobs


# Remove duplicate jobs
def remove_duplicates(jobs):
    unique_jobs = {}

    for job in jobs:
        job_id = job.get("job_id")

        if job_id:
            unique_jobs[job_id] = job

    return list(unique_jobs.values())


# Retrieve full job information
def get_job_details(job_id):
    params = {
        "engine": "linkedin_job_details",
        "job_id": job_id
    }

    data = api_request(params)

    return data.get("job", {})


# Filter internship-level jobs
def get_internships(jobs):
    internships = []

    for index, job in enumerate(jobs, start=1):

        title = job.get("title", "")

        # Avoid unnecessary detail requests
        title_lower = title.lower()

        if not any(word in title_lower for word in [
            "intern", "internship", "co-op", "coop"
        ]):
            continue

        job_id = job.get("job_id")

        if not job_id:
            continue

        print(f"Checking {index}/{len(jobs)}: {title}")

        try:
            details = get_job_details(job_id)

            seniority = details.get("seniority_level", "")

            # Keep confirmed internship-level positions
            if seniority.lower() != "internship":
                continue

            internships.append({
                "job_id": job_id,
                "title": details.get("title", title),
                "company": details.get("company_name"),
                "location": details.get("location"),
                "date_posted": job.get("date"),
                "posted_at": details.get("posted_at"),
                "seniority_level": seniority,
                "employment_type": details.get("employment_type"),
                "salary": details.get("salary"),
                "applicants": details.get("applicants"),
                "description": details.get("description"),
                "job_url": details.get("link")
            })

            print("  Internship confirmed!")

            time.sleep(0.3)

        except requests.RequestException as error:
            print(f"  API error: {error}")

    return internships


# Main program
def main():

    print("Starting LinkedIn internship collection...\n")

    jobs = search_jobs()

    print(f"\nTotal collected: {len(jobs)}")

    jobs = remove_duplicates(jobs)

    print(f"After removing duplicates: {len(jobs)}")

    internships = get_internships(jobs)

    # Export to CSV
    df = pd.DataFrame(internships)

    df.to_csv(
        "linkedin_internships_canada.csv",
        index=False,
        encoding="utf-8-sig"
    )

    print("\nCollection complete!")
    print(f"Confirmed internships: {len(df)}")
    print("Saved: linkedin_internships_canada.csv")


if __name__ == "__main__":
    main()
