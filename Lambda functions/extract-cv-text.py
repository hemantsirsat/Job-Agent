import io
import boto3
import json
from PyPDF2 import PdfReader

s3 = boto3.client("s3")
lambda_client = boto3.client("lambda")

def lambda_handler(event, context):
    # Get bucket/key from event
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = event["Records"][0]["s3"]["object"]["key"]

    response = s3.get_object(Bucket=bucket, Key=key)
    file_stream = io.BytesIO(response["Body"].read())

    pdf_reader = PdfReader(file_stream)
    text = "".join([page.extract_text() or "" for page in pdf_reader.pages])

    # Prepare payload to invoke the next Lambda function
    payload = {
        "cv_text": text,
        "source_bucket": bucket,
        "source_key": key
    }

    target_lambda_function = "parse-cv"

    # Invoke the next Lambda
    response = lambda_client.invoke(
        FunctionName=target_lambda_function,
        InvocationType='RequestResponse',  # can be "Event" as well
        Payload=json.dumps(payload)
    )

    response_payload = response['Payload'].read()
    result = json.loads(response_payload)

    print(f"Received response from {target_lambda_function}: {result}")

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "PDF text extracted and parsed",
            "parse_cv_result": result
        })
    }