
import requests
import os
from dotenv import load_dotenv

load_dotenv()

job_type = input("What type of job are you looking for?: ")

url = "https://api.adzuna.com/v1/api/jobs/ca/search/1"

params = {
    "app_id": os.getenv("ADZUNA_APP_ID"),
    "app_key": os.getenv("ADZUNA_APP_KEY"),
    "what": job_type,
    "where": "Calgary",
    "results_per_page": 10
}

response = requests.get(url, params=params)

print("Status:", response.status_code)

if response.ok:
    data = response.json()

    print("Total matching jobs:", data.get("count"))

    for job in data.get("results", []):
        title = job.get("title", "N/A")
        company = job.get("company", {}).get("display_name", "N/A")
        description = job.get("description", "No description available")
        link = job.get("redirect_url", "N/A")

        print("\n" + "=" * 60)
        print("Job Title:", title)
        print("Company:", company)
        print("Description:", description)
        print("Application Link:", link)

else:
    print(response.text)
