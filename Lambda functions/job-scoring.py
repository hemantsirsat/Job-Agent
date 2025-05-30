import os
import re
import json
import time
import boto3
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI

# Initialize LLM
gemini_api_key = os.environ["GEMINI_API_KEY"]
llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash-exp', google_api_key=gemini_api_key)

def build_scoring_prompt(job, cv):
    return f"""
        You are a job matching assistant. Score the fit of a candidate for a job posting.

        ### Candidate CV (JSON)
        {json.dumps(cv, indent=2)}

        ### Job Posting
        Title: {job.get("title", "")}
        Company: {job.get("company", {}).get("display_name", "")}
        Location: {job.get("location", {}).get("display_name", "")}
        Category: {job.get("category", {}).get("label", "")}
        Description: {job.get("description", "")}

        ### Instructions:
        Score how well this job matches the candidate's background. Use the following criteria:
        - Relevant skills match (e.g., programming languages, frameworks)
        - Job title relevance to past experience
        - Educational background fit
        - General industry alignment

        Return only a JSON object like this:

        ```json
        {{
        "score": 0–100,
        "reason": "Short explanation"
        }}""".strip()

def lambda_handler(event, context):
    jobs = event.get("jobs", [])
    cv = event.get("cv", {})
    for job in jobs:
        try:
            prompt = build_scoring_prompt(job, cv)
            response = llm.invoke(prompt)

            cleaned = re.sub(r"^```json|```$", "", response.content.strip(), flags=re.MULTILINE)
            parsed = json.loads(cleaned)
            score = parsed["score"]
            reason = parsed["reason"]
        except Exception as e:
            score = 0
            reason = f"Error: {str(e)}"
            time.sleep(3)
        job["score"] = json.dumps({"score": score, "reason": reason})
        print(f"Job {job.get('id', 'N/A')} scored {score} reason: {reason}")
    return {
            "statusCode": 200,
            "body": json.dumps({
                "jobs": jobs
            })
        }