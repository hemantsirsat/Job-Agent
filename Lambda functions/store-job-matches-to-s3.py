import json
import os
import boto3
import logging
import csv
from io import StringIO

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client("s3")
BUCKET_NAME = "matching-cv-jobs-bucket"  # Set this as a Lambda env variable

def parse_score(score_string):
    try:
        return json.loads(score_string)
    except:
        return {"score": 0, "reason": "Score parsing failed."}

import json
import os
import boto3
import logging
import csv
from io import StringIO

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client("s3")
BUCKET_NAME = "matching-cv-jobs-bucket"  # Set this as a Lambda env variable

def parse_score(score_string):
    try:
        return json.loads(score_string)
    except:
        return {"score": 0, "reason": "Score parsing failed."}

def lambda_handler(event, context):
    try:
        email = event.get("email", "")
        job_matches = event.get("jobs", [])

        if not email or not job_matches:
            return {"statusCode": 400, "body": "Missing 'cv_json' or 'job_matches'"}

        csv_key = f"{email}/job_matches.csv"

        # Load existing rows
        existing_jobs = load_existing_csv(BUCKET_NAME, csv_key)

        # Update or insert new job matches
        for job in job_matches:
            score_data = parse_score(job.get("score", "{}"))
            job_id = job.get("id", "")
            existing_jobs[job_id] = {
                "Job ID": job_id,
                "Title": job.get("title", ""),
                "Company": job.get("company", {}).get("display_name", ""),
                "Location": job.get("location", {}).get("display_name", ""),
                "Salary": job.get("salary_min", "N/A"),
                "Contract Type": job.get("contract_time", ""),
                "Description": job.get("description", ""),  # Optional truncation
                "Link": job.get("redirect_url", ""),
                "Score": score_data.get("score", 0),
                "Reason": score_data.get("reason", "")
            }

        # Write final CSV
        output = StringIO()
        fieldnames = [
            "Job ID", "Title", "Company", "Location", "Salary", "Contract Type",
            "Description", "Link", "Score", "Reason"
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for row in existing_jobs.values():
            writer.writerow(row)

        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=csv_key,
            Body=output.getvalue(),
            ContentType="text/csv"
        )

        logger.info(f"CSV updated in S3: {csv_key}")
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": f"CSV uploaded/updated for {email}",
                "s3_key": csv_key
            })
        }

    except Exception as e:
        logger.error(f"Error storing matches to CSV: {str(e)}")
        return {"statusCode": 500, "body": str(e)}

def load_existing_csv(bucket, key):
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        content = response['Body'].read().decode('utf-8')
        reader = csv.DictReader(StringIO(content))
        return {row['Job ID']: row for row in reader}
    except s3.exceptions.NoSuchKey:
        return {}  # No existing file
    except Exception as e:
        logger.error(f"Error reading existing CSV: {e}")
        return {}

def lambda_handler(event, context):
    try:
        email = event.get("email", "")
        job_matches = event.get("jobs", [])

        if not email or not job_matches:
            return {"statusCode": 400, "body": "Missing 'cv_json' or 'job_matches'"}

        csv_key = f"{email}/job_matches.csv"

        # Load existing rows
        existing_jobs = load_existing_csv(BUCKET_NAME, csv_key)

        # Update or insert new job matches
        for job in job_matches:
            score_data = parse_score(job.get("score", "{}"))
            job_id = job.get("id", "")
            existing_jobs[job_id] = {
                "Job ID": job_id,
                "Title": job.get("title", ""),
                "Company": job.get("company", {}).get("display_name", ""),
                "Location": job.get("location", {}).get("display_name", ""),
                "Salary": job.get("salary_min", "N/A"),
                "Contract Type": job.get("contract_time", ""),
                "Description": job.get("description", ""),  # Optional truncation
                "Link": job.get("redirect_url", ""),
                "Score": score_data.get("score", 0),
                "Reason": score_data.get("reason", "")
            }

        # Write final CSV
        output = StringIO()
        fieldnames = [
            "Job ID", "Title", "Company", "Location", "Salary", "Contract Type",
            "Description", "Link", "Score", "Reason"
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for row in existing_jobs.values():
            writer.writerow(row)

        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=csv_key,
            Body=output.getvalue(),
            ContentType="text/csv"
        )

        logger.info(f"CSV updated in S3: {csv_key}")
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": f"CSV uploaded/updated for {email}",
                "s3_key": csv_key
            })
        }

    except Exception as e:
        logger.error(f"Error storing matches to CSV: {str(e)}")
        return {"statusCode": 500, "body": str(e)}
