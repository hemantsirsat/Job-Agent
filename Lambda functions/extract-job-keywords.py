import os
import re
import json
import logging
from langchain_google_genai import ChatGoogleGenerativeAI

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Load Gemini LLM with API key from environment
llm = ChatGoogleGenerativeAI(
    model='gemini-2.0-flash-exp',
    google_api_key=os.environ.get("GEMINI_API_KEY")
)

def lambda_handler(event, context):
    try:
        # Get structured CV JSON from event
        structured_cv = event.get("structured-cv")
        if not structured_cv:
            raise ValueError("Missing 'structured_cv' in event payload")

        # Create prompt to extract keywords
        prompt = (
            "You are given a structured candidate profile in JSON format that includes skills, work experience, and education.\n"
            "From this profile, extract only the **top 3 most relevant job role or field keywords** that best describe the candidate’s main areas of expertise.\n"
            "Do not include infrastructure tools (e.g., Docker, CI/CD), libraries (e.g., TensorFlow, PyTorch), or general terms (e.g., SQL, AWS) unless they are central to the field.\n\n"
            "Return only a JSON list of exactly 3 most concise and relevant keywords. Examples: [\"data science\", \"machine learning\", \"natural language processing\"]\n\n"
            f"Profile:\n{json.dumps(structured_cv, indent=2)}"
        )

        # Call Gemini model
        result = llm.invoke(prompt)

        # Clean up response text from code fences and whitespace
        clean_result = re.sub(r"^```(?:json)?|```$", "", result.content.strip(), flags=re.MULTILINE).strip()

        # Try parsing model output as JSON
        try:
            keywords = json.loads(clean_result)
            if not isinstance(keywords, list):
                raise ValueError("Output is not a list")
        except Exception as parse_err:
            logger.error(f"Failed to parse model output: {result}")
            raise parse_err

        result = {
            "statusCode": 200,
            "body": json.dumps({
                "keywords": keywords
            })
        }
        logger.info(f"Extracted keywords: {result}")

        return result

    except Exception as e:
        logger.error(f"Error in extract_keywords lambda: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }