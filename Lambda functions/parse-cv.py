import json
import os
import boto3
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI

# Initialize LLM
gemini_api_key = os.environ["GEMINI_API_KEY"]
llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash-exp', google_api_key=gemini_api_key)

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
        result = {
            "statusCode": 200,
            "body": json.dumps({
                "message": "CV parsed",
                "parsed_cv": cv_json
            })
        }
        print(f"Result: {result}")
        
        return result
    except Exception as e:
        print(f"Error: {e}")
