import json
import os
import boto3
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI

# Initialize LLM
gemini_api_key = os.environ["GEMINI_API_KEY"]
llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash-exp', google_api_key=gemini_api_key)

# Initialize S3 client
s3 = boto3.client("s3")
bucket_name = "parsed-cv-results"  # Or hardcode: 'your-bucket-name'
lambda_client = boto3.client("lambda")

def fetch_job_keywords(parsed_json):
    target_lambda_function = "extract-job-keywords"

    payload = {
        "structured-cv": json.dumps(parsed_json),
    }

    # Invoke the next Lambda
    response = lambda_client.invoke(
        FunctionName=target_lambda_function,
        InvocationType='RequestResponse',  # can be "Event" as well
        Payload=json.dumps(payload)
    )

    response_payload = response['Payload'].read()
    result = json.loads(response_payload)

    print(f"Received response from {target_lambda_function}: {result}")

    # Parse the body and extract keywords
    parsed_body = json.loads(result['body'])
    keywords = parsed_body.get("keywords", [])
    print("Extracted keywords:", keywords)
    return keywords

def fetch_relevant_jobs(keywords):
    target_lambda_function = "fetch-jobs"

    payload = {
        "keywords": keywords,
    }

    # Invoke the next Lambda
    response = lambda_client.invoke(
        FunctionName=target_lambda_function,
        InvocationType='RequestResponse',  # can be "Event" as well
        Payload=json.dumps(payload)
    )

    response_payload = response['Payload'].read()
    result = json.loads(response_payload)

    print(f"Received response from {target_lambda_function}: {result}")

    # Parse the body and extract keywords
    parsed_body = json.loads(result['body'])
    jobs = parsed_body
    print("Extracted jobs:", jobs)
    return jobs

def score_jobs(jobs, cv):
    target_lambda_function = "job-scoring"

    payload = {
        "jobs": jobs,
        "cv": cv,
    }

    # Invoke the next Lambda
    response = lambda_client.invoke(
        FunctionName=target_lambda_function,
        InvocationType='RequestResponse',  # can be "Event" as well
        Payload=json.dumps(payload)
    )

    response_payload = response['Payload'].read()
    result = json.loads(response_payload)

    print(f"Received response from {target_lambda_function}: {result}")

    # Parse the body and extract keywords
    parsed_body = json.loads(result['body'])
    scored_jobs = parsed_body["jobs"]
    print("Extracted scored jobs:", scored_jobs)
    return scored_jobs

def store_jobs_to_s3(email, jobs):
    target_lambda_function = "store-job-matches-to-s3"

    payload = {
        "jobs": jobs,
        "email": email,
    }
    try:
        # Invoke the next Lambda
        response = lambda_client.invoke(
            FunctionName=target_lambda_function,
            InvocationType='RequestResponse',  # can be "Event" as well
            Payload=json.dumps(payload)
        )

        response_payload = response['Payload'].read()
        result = json.loads(response_payload)

        print(f"Received response from {target_lambda_function}: {result}")

        # Parse the body and extract keywords
        parsed_body = json.loads(result['body'])
        scored_jobs = parsed_body["jobs"]
        print("Jobs successfully added to respective s3 bucket.")
    except Exception as e:
        print(f"Error while storing scored jobs to s3 bucket: {e}")


def lambda_handler(event, context):
    try:
        text = event["cv_text"]

        prompt = (
            "Extract the following structured fields from this resume:\n"
            "- Full Name\n- Email\n- Skills (comma-separated)\n"
            "- Education (degrees, institutions)\n- Work Experience (title, company, duration)\n\n"
            f"Resume:\n{text}\n\nReturn a JSON object."
        )
        result = llm.invoke(prompt)
        # Store result in S3
        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
        file_key = f"parsed_cv_{timestamp}.json"

        raw_content = result.content.strip()
        # Remove code block markers if present
        if raw_content.startswith("```json"):
            raw_content = raw_content[len("```json"):].strip()
        if raw_content.endswith("```"):
            raw_content = raw_content[:-3].strip()

        # Now parse the cleaned content
        try:
            cv_json = json.loads(raw_content)
        except json.JSONDecodeError as e:
            print("Cleaned model output that failed JSON parse:\n", raw_content)
            raise e

        s3.put_object(
            Bucket=bucket_name,
            Key=file_key,
            Body=json.dumps(cv_json),
            ContentType="application/json"
        )

        print("Successfully added to s3 bucket")
        keywords = fetch_job_keywords(cv_json)

        relevant_jobs = fetch_relevant_jobs(keywords)
        print("Scoring jobs based on CV...")
        scored_jobs = score_jobs(relevant_jobs, cv_json)
        print(f"Successfully scored jobs.")
        print("Storing scored jobs to s3 bucket...")
        store_jobs_to_s3(cv_json.get("Email",""), scored_jobs)
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "CV parsed and stored to S3",
                "s3_key": file_key
            })
        }
    except Exception as e:
        print(f"Error: {e}")
