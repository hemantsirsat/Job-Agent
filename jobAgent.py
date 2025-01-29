import csv
import os
import re
import sys
from pathlib import Path
from PyPDF2 import PdfReader

from browser_use.browser.browser import Browser, BrowserConfig
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from typing import List, Optional

from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, SecretStr

from browser_use import ActionResult, Agent, Controller
from browser_use.browser.context import BrowserContext

load_dotenv()
import logging

logging.basicConfig(handlers=[logging.FileHandler(
                                        filename='Job Agent.log', 
                                        encoding='utf-8', 
                                        mode='w+')],
                    format="%(asctime)s %(name)s:%(levelname)s:%(message)s", 
                    datefmt="%F %A %T",
                    level=logging.DEBUG
)

controller = Controller()

CV = os.getenv("CV_PATH")
logging.info(f"CV path = {CV}")

class Job(BaseModel):
    title: str
    link: str
    company: str
    fit_score: float
    location: Optional[str] = None
    salary: Optional[str] = None
    cover_letter: Optional[str] = None

@controller.action("Save jobs to file - with a score how well it fits to my profile", param_model=Job)
def save_jobs(job:Job):
    with open("jobs.csv","a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([job.title, job.company, job.fit_score, job.link, job.salary, job.location, job.cover_letter])
    return "Saved Job to file"

@controller.action("Read jobs from file")
def read_jobs():
    with open("jobs.csv","r", newline="") as f:
        jobs = f.read()
    f.close()
    return jobs

@controller.action("Read my CV for context to fill forms")
def read_cv():
    pdf = PdfReader(CV)
    text = ""
    for page in pdf.pages:
        text += page.extract_text() or ""
	
    logging.info(f"Read CV with {len(text)} characters")
    print(f"Read CV with {len(text)} characters")
    return ActionResult(extracted_content=text, include_in_memory=True)

@controller.action(
	'Upload cv to element - call this function to upload if element is not found, try with different index of the same upload element',
	requires_browser=True,
)
async def upload_cv(index: int, browser: BrowserContext):
	path = str(CV.absolute())
	dom_el = await browser.get_dom_element_by_index(index)

	if dom_el is None:
		return ActionResult(error=f'No element found at index {index}')

	file_upload_dom_el = dom_el.get_file_upload_element()

	if file_upload_dom_el is None:
		logging.info(f'No file upload element found at index {index}')
		return ActionResult(error=f'No file upload element found at index {index}')

	file_upload_el = await browser.get_locate_element(file_upload_dom_el)

	if file_upload_el is None:
		logging.info(f'No file upload element found at index {index}')
		return ActionResult(error=f'No file upload element found at index {index}')

	try:
		await file_upload_el.set_input_files(path)
		msg = f'Successfully uploaded file to index {index}'
		logging.info(msg)
		return ActionResult(extracted_content=msg)
	except Exception as e:
		logging.debug(f'Error in set_input_files: {str(e)}')
		return ActionResult(error=f'Failed to upload file to index {index}')


browser = Browser(
	config=BrowserConfig(
		chrome_instance_path='C:\Program Files\Google\Chrome\Application\chrome.exe',
		disable_security=True,
	)
)

async def main():
	ground_task = (
		'You are a professional job finder. '
		'1. Read my cv with read_cv.'
		'2. Go to https://www.google.de.'
		'3. Find 100 full time jobs in machine learning/data scientist. Go through each job details and save them to a file.'
		'4. Make sure the job is for 0 experience professionals and does not requires German language proficiency.'
		'5. Go through the job description and create a short cover letter implying my strong skills for the job. In salutation add my full name and then my email address.'
		'6. search in all the companies in Germany.'
	)
	tasks = [
		ground_task
	]

	#llm = ChatOpenAI(model="deepseek-r1:8b",base_url="http://localhost:11434/v1",api_key=os.getenv("DEEPSEEK_API"))
	llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash-exp', api_key=os.getenv("GEMINI_API"))

	agents = []
	for task in tasks:
		agent = Agent(task=task, llm=llm, controller=controller, browser=browser)
		agents.append(agent)

	await asyncio.gather(*[agent.run() for agent in agents])


if __name__ == '__main__':
	asyncio.run(main())