import io
import boto3
import json
from PyPDF2 import PdfReader

s3 = boto3.client("s3")

def lambda_handler(event, context):
    try:
        # Get bucket and key from event
        bucket = event["bucket"]
        key = event["key"]

        response = s3.get_object(Bucket=bucket, Key=key)
        file_stream = io.BytesIO(response["Body"].read())

        pdf_reader = PdfReader(file_stream)
        text = "".join([page.extract_text() or "" for page in pdf_reader.pages])    

        result = {
            "statusCode": 200,
            "body": json.dumps({
                "message": "PDF text extracted",
                "cv_text": text
            })
        }
        print(f"Result: {result}")
        return result
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Error extracting text from PDF",
                "error": str(e)
            })
        }
