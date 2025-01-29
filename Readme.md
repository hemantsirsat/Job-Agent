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
|-- Job Agent.log
|-- jobs.csv
|-- jobAgent.py
|-- .env
```

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
