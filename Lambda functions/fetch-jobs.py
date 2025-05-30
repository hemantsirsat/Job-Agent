import json
import os
import requests

adzuna_app_id = os.environ.get("ADZUNA_APP_ID")
adzuna_api_key = os.environ.get("ADZUNA_API_KEY")
adzuna_endpoint = "https://api.adzuna.com/v1/api/jobs/de/search/1"

def lambda_handler(event, context):
    job_keywords = event.get("keywords", [])
    results = []

    try:
        for keyword in job_keywords:
            params = {
                "app_id": adzuna_app_id,
                "app_key": adzuna_api_key,
                "results_per_page": 3,
                "what": keyword,
                # "where": "Germany",
                "full_time": 1,
                # "experience": "0"
            }
            try:
                response = requests.get(adzuna_endpoint, params=params)
                print(f"Response from Adzuna for {keyword}: {response.text}")
                jobs = response.json().get("results", [])
                results.extend(jobs)
            except Exception as e:
                print(f"Error fetching jobs from Adzuna API: {e}")

        result = {
            "statusCode": 200,
            "body": json.dumps(results)
        }
        print(f"Results: {result}")
        return result
    except Exception as e:
        print(e)
        return {
                "statusCode": 500,
                "body": json.dumps({
                    "message": "Error fetching jobs from Adzuna API."
                })
            }