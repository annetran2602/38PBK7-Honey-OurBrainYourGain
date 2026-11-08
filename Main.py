
import requests
import os
from dotenv import load_dotenv

load_dotenv()

job_type = input("What type of job are you looking for?: ") # get input of job

url = "https://api.adzuna.com/v1/api/jobs/ca/search/1"

params = {
    "app_id": os.getenv("ADZUNA_APP_ID"), # retrieved api id from env file
    "app_key": os.getenv("ADZUNA_APP_KEY"),# retrieve api key from env key
    "what": job_type,
    "where": "Calgary",
    "results_per_page": 10 # display 10 result only
}

response = requests.get(url, params=params)

print("Status:", response.status_code) # status of the request

if response.ok:
    data = response.json()

    print("Total matching jobs:", data.get("count")) # total job that matched with the request

    for job in data.get("results", []): # display each job info
        title = job.get("title", "N/A")
        company = job.get("company", {}).get("display_name", "N/A") # display company name, n/a otherwise
        description = job.get("description", "No description available") # display job description or no description available otherwise
        link = job.get("redirect_url", "N/A")

# print search result
        print("\n" + "=" * 60)
        print("Job Title:", title)
        print("Company:", company)
        print("Description:", description)
        print("Application Link:", link)

else:
    print(response.text)
