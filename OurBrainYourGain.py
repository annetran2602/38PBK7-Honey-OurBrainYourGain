
import requests
import os
from dotenv import load_dotenv

from matching_algorithm import match_resume_to_job
from resume_scanner import scan_resume


# Load API credentials
load_dotenv()


def main():

    # --------------------------------
    # 1. Get job search information
    # --------------------------------

    job_type = input(
        "What type of job are you looking for?: "
    )

    pdf_path = input(
        "Enter your resume PDF path: "
    )

    # --------------------------------
    # 2. Scan resume
    # --------------------------------

    print("\nScanning resume...")

    resume_text = scan_resume(pdf_path)

    if not resume_text:
        print("Unable to extract text from resume.")
        return

    print("Resume successfully scanned!")

    # --------------------------------
    # 3. Retrieve jobs from Adzuna
    # --------------------------------

    url = "https://api.adzuna.com/v1/api/jobs/ca/search/1"

    params = {
        "app_id": os.getenv("ADZUNA_APP_ID"),
        "app_key": os.getenv("ADZUNA_APP_KEY"),
        "what": job_type,
        "where": "Calgary",
        "results_per_page": 10
    }

    if not params["app_id"] or not params["app_key"]:
        print("Missing Adzuna API credentials in .env.")
        return

    print("\nSearching for jobs...")

    try:
        response = requests.get(
            url,
            params=params,
            timeout=30
        )

        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        print("Error retrieving jobs:", e)
        return

    data = response.json()

    jobs = data.get("results", [])

    print("\nTotal matching jobs:", data.get("count", 0))
    print("Jobs retrieved:", len(jobs))

    if not jobs:
        print("No jobs found.")
        return

    # --------------------------------
    # 4. Compare resume against jobs
    # --------------------------------

    matched_jobs = []

    for index, job in enumerate(jobs, start=1):

        title = job.get("title", "N/A")

        company = job.get(
            "company", {}
        ).get("display_name", "N/A")

        description = job.get(
            "description",
            "No description available"
        )

        link = job.get("redirect_url", "N/A")

        print("\n" + "=" * 65)
        print(f"JOB {index}: {title}")
        print("Company:", company)
        print("Application Link:", link)
        print("=" * 65)

        print("\nAnalyzing resume with Ollama...")

        try:

            results = match_resume_to_job(
                resume_text,
                description
            )

            score = results["match_score"]

            print("\nMatch Score:", score, "%")

            print("\nOverall Assessment:")
            print(results["overall_assessment"])

            print("\nMatching Qualifications:")

            for item in results["matching_qualifications"]:
                print("-", item["requirement"])
                print("  Evidence:", item["resume_evidence"])
                print("  Match:", item["match"])

            print("\nMissing Qualifications:")

            for item in results["missing_qualifications"]:
                print("-", item["requirement"])
                print("  Importance:", item["importance"])
                print("  Reason:", item.get("reason", "N/A"))

            print("\nSkills Match:")

            for skill in results["skills_match"]:
                print("-", skill)

            print("\nExperience Analysis:")
            print(results["experience_analysis"])

            print("\nEducation Analysis:")
            print(results["education_analysis"])

            print("\nRecommendations:")

            for recommendation in results["recommendations"]:
                print("-", recommendation)

            # Store results for ranking
            matched_jobs.append({
                "title": title,
                "company": company,
                "link": link,
                "match_score": score,
                "assessment": results["overall_assessment"]
            })

        except Exception as e:
            print("Error matching resume:", e)

        input("\nPress Enter to view the next job...")

    # --------------------------------
    # 5. Rank jobs by match score
    # --------------------------------

    matched_jobs.sort(
        key=lambda job: job["match_score"],
        reverse=True
    )

    print("\n\n" + "=" * 65)
    print("FINAL JOB MATCH RANKINGS")
    print("=" * 65)

    for rank, job in enumerate(matched_jobs, start=1):

        print(f"\nRank #{rank}")
        print("Job Title:", job["title"])
        print("Company:", job["company"])
        print("Match Score:", job["match_score"], "%")
        print("Application Link:", job["link"])


if __name__ == "__main__":
    main()
