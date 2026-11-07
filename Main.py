import requests
import os
from dotenv import load_dotenv

job = input("What Type of Job are you looking for?: ")

load_dotenv()

url = "https://api.adzuna.com/v1/api/jobs/ca/search/1"

params = {
    "app_id": os.getenv("ADZUNA_APP_ID"),
    "app_key": os.getenv("ADZUNA_APP_KEY"),
    "what": job,
    "where": "Calgary",
    "results_per_page": 10
}

response = requests.get(url, params=params)

print("Status:", response.status_code)

if response.ok:
    data = response.json()

    print("Total matching jobs:", data.get("count"))

    for job in data.get("results", []):
        print(job["title"], "-", job["company"]["display_name"])
else:
    print(response.text)