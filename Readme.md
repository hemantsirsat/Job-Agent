# Job Agent Automation Project

## Overview
This project is an automated job application tool that integrates a browser controller, PDF reader, and language models to help users find and apply for jobs efficiently. It reads a user's CV, searches for relevant job postings, evaluates job fit scores, and generates personalized cover letters for applications.

## Features
- **Read CV**: Extracts text from the user's CV (PDF format) to use as context.
- **Job Search**: Finds job postings for machine learning and data science positions in Germany (Can be changed as per requirements).
- **Job Evaluation**: Rates job postings based on fit with the user's profile.
- **Cover Letter Generation**: Automatically generates cover letters for applications.
- **File Handling**: Saves job postings and reads them back from a CSV file.
- **Logging**: Provides detailed logs for debugging and tracking operations.

## Project Structure
```
Job Agent
|-- Lambda functions
    |-- extract-cv-text.py
    |-- parse-cv.py
    |-- extract-job-keywords.py
    |-- fetch-jobs.py
    |-- job-scoring.py
    |-- store-jobs-matches-to-s3.py
|-- Job Agent.log
|-- jobs.csv
|-- jobAgent.py
|-- .env
```

### Lambda Functions

#### 📄 extract-cv-text.py
- This Lambda function is triggered by an S3 event when a CV PDF is uploaded. It extracts the raw text from the PDF using `PyPDF2`, then invokes the `parse-cv` Lambda function by passing the extracted text.
- This serves as the entry point for processing candidate resumes.

#### 🧠 parse-cv.py
- This Lambda function receives raw resume text, parses it using the Gemini LLM to extract structured information (e.g., name, email, skills, education, experience), and stores it in S3. 
- It then triggers a chain of Lambda functions to extract job-related keywords, fetch relevant job listings, score them based on CV fit, and finally store the top results in another S3 bucket.

#### 🔍 extract-job-keywords.py
- This Lambda function takes a structured CV JSON as input and uses Gemini LLM to extract the top 3 most relevant job field keywords. 
- It filters out tools, libraries, and generic terms, returning only the core areas of expertise suitable for matching relevant job listings.

#### 📄 fetch-jobs.py
- This Lambda function queries the Adzuna Jobs API using a list of relevant job field keywords extracted from a candidate's profile. 
- It retrieves job postings for each keyword and returns a combined list of matching job results.

#### 🎯 job-scoring.py
- This Lambda function evaluates how well each job posting matches a candidate's profile using the Gemini LLM. 
- It generates a relevance score (0–100) and an explanation for each job by comparing the candidate's skills, education, and experience with the job description. 
- The scores are returned in JSON format.

#### 💾 store-job-matches-to-s3.py
- This Lambda function stores scored job matches into an Amazon S3 bucket as a CSV file. 
- Each user has a dedicated folder (based on their email), and job entries are organized in tabular format. If a job with the same ID already exists, it is automatically updated with the new score and details.

### APIs
This project defines multiple secure API endpoints.

#### Job-CV Matching API
- This API securely sends parsed CV and job data to an AWS Lambda function, which uses **prompt engineering** with a Large Language Model (LLM) (Gemini) to evaluate how well a CV matches each job.

    🚀 How to Use This API

    URL: https://aydopiql03.execute-api.eu-central-1.amazonaws.com/development-env

    Make a `POST` request to the API with the following JSON payload:

        {
        "cv": {
            "Full Name": "YOUR NAME",
            "Email": "name@domain.com",
            "Skills": "Some skills like C, Python, R, ...",
            "Education": [
            {
                "Degree": "Master’s in xxx, xxxx",
                "Institution": "xxxx, xxxx",
                "Duration": "xxxx-xx"
            },
            {
                "Degree": "Bachelor of xxxx, xxxx ",
                "Institution": "xxxx, xxxx",
                "Duration": "xxxx-xx"
            }
            ],
            "Work Experience": [
            {
                "Title": "xxxx",
                "Company": "xxxx",
                "Duration": "xxx - Present"
            },
            ]
        },
        "jobs": [
            {
            "id": "xxxx",
            "title": "xxxx",
            "company": {
                "display_name": "xxxx"
            },
            "description": "xxxx",
            "location": {
                "display_name": "xxxx"
            },
            }
        ]
        }

    Response from the API:
    
        {
            "statusCode": 200,
            "body": "{\"jobs\": [{...}]}"
        }

    Each job in the response has the following structure:

        {
            "id": "xxxx",
            "title": "xxxx",
            "company": {
                "display_name": "xxxx"
            },
            "description": "xxxx",
            "location": {
                "display_name": "xxxx"
            },
            "score": {
                "score": "0-100",
                "reason": "xxxx"
            }
        }


### Key Components
- `jobAgent.py`: The main entry point of the project.
- `Job Agent.log`: Log file to track application events.
- `jobs.csv`: File where job postings are saved.
- `.env`: Environment file to store sensitive information such as API keys and file paths.
- `app.py`: Python file to connect with locally hosted deepseek-r1 model.

## Requirements
- Python 3.11+ (browser_use requirement)
- Dependencies listed in `requirements.txt`

### Key Libraries Used
- `PyPDF2`: For reading and extracting text from PDF files.
- `asyncio`: For asynchronous task handling.
- `dotenv`: For managing environment variables.
- `pydantic`: For data validation.
- `csv`: For file operations.
- `logging`: For detailed logging.

## Setup Instructions

### 1. Clone the Repository
```
git clone https://github.com/hemantsirsat/Job-Agent.git
cd Job-Agent
```

### 2. Install Dependencies
```
pip install -r requirements.txt
```

### 3. Set Up Environment Variables
Create a `.env` file with the following variables:
```
CV_PATH=<path_to_your_cv_pdf>
GEMINI_API=<your_gemini_api_key>
```

### 4. Run the Project
```
python jobAgent.py
```

## Logging
Logs are saved in `Job Agent.log`. They include detailed information about operations and errors.

## Example Log Output
```
2025-01-29 Tuesday 10:30:21 INFO:CV path = /path/to/cv.pdf
2025-01-29 Tuesday 10:31:05 INFO:Saved job to file successfully.
```

## Contributions
Contributions are welcome! Please fork the repository and submit a pull request.
