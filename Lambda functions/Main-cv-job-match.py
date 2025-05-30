import json
import boto3

lambda_client = boto3.client("lambda")

def extract_text_from_pdf(bucket, key):
    try:
        # Implementation of text extraction from PDF
        target_lambda_function = "extract-cv-text"
        
        payload = {
            "bucket": bucket,
            "key": key,
        }
        # Invoke the next Lambda
        response = lambda_client.invoke(
            FunctionName=target_lambda_function,
            InvocationType='RequestResponse',  # can be "Event" as well
            Payload=json.dumps(payload)
        )

        response_payload = response['Payload'].read()
        result = json.loads(response_payload)
        result_body = json.loads(result['body'])
        cv_text = result_body.get("cv_text", [])
        return cv_text
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")

def parse_cv(cv_text):
    try:
        # Implementation of CV parsing
        target_lambda_function = "parse-cv"
        
        payload = {
            "cv_text": cv_text,
        }

        # Invoke the next Lambda
        response = lambda_client.invoke(
            FunctionName=target_lambda_function,
            InvocationType='RequestResponse',  # can be "Event" as well
            Payload=json.dumps(payload)
        )

        response_payload = response['Payload'].read()
        result = json.loads(response_payload)
        result_body = json.loads(result['body'])
        structured_cv = result_body['parsed_cv']
        return structured_cv
    except Exception as e:
        raise Exception(f"Error parsing CV: {str(e)}")

def extract_job_keywords(structured_cv):
    try:
        target_lambda_function = "extract-job-keywords"

        payload = {
            "structured-cv": json.dumps(structured_cv),
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
    except Exception as e:
        raise Exception(f"Error extracting keywords: {str(e)}")

def fetch_jobs(keywords):
    try:
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
        jobs = json.loads(result['body'])
        print("Extracted jobs:", jobs)
        return jobs
    except Exception as e:
        raise Exception(f"Error fetching jobs: {str(e)}")

def score_jobs(jobs, structured_cv):
    try:
        target_lambda_function = "job-scoring"

        payload = {
            "jobs": jobs,
            "cv": structured_cv,
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
        if result['statusCode'] != 200:
            raise Exception(f"Error scoring jobs: {result['body']}")
            return
        # Parse the body and extract keywords
        parsed_body = json.loads(result['body'])
        scored_jobs = parsed_body["jobs"]
        print("Extracted scored jobs:", scored_jobs)
        return scored_jobs
    except Exception as e:
        raise Exception(f"Error scoring jobs: {str(e)}")

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
        if result['statusCode'] != 200:
            raise Exception(f"Error while storing scored jobs to s3 bucket: {result['body']}")
            return

        parsed_body = json.loads(result['body'])
        scored_jobs = parsed_body["jobs"]
        print("Jobs successfully added to respective s3 bucket.")
    except Exception as e:
        print(f"Error while storing scored jobs to s3 bucket: {e}")

def lambda_handler(event, context):
    try:
        bucket = event["Records"][0]["s3"]["bucket"]["name"]
        key = event["Records"][0]["s3"]["object"]["key"]

        # Step 1: Extract text
        text = extract_text_from_pdf(bucket, key)

        # Step 2: Parse CV
        structured_cv = parse_cv(text)

        # Step 3: Extract keywords
        keywords = extract_job_keywords(structured_cv)

        # Step 4: Fetch jobs
        jobs = fetch_jobs(keywords)

        # Step 5: Score jobs
        jobs = score_jobs(jobs, structured_cv)

        # Step 6: Save CSV to S3
        email = structured_cv.get("Email", "anonymous@example.com")
        #csv_key = save_jobs_to_csv(email, jobs)
        store_jobs_to_s3(email, jobs)

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Processing complete",
                #"csv_key": csv_key
            })
        }

    except Exception as e:
        print(f"Error: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }