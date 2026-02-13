import requests
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os, sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from mcp_server import vector_store

API_URL = "http://localhost:8000/timesheets"


def ingest_timesheets():

    print("Fetching timesheets from API...")
    response = requests.get(API_URL)
    timesheets = response.json()

    if not timesheets:
        print("No timesheet data received.")
        return

    docs = []

    text="List of all timesheets/projects:"
    for t in timesheets:
        text += "\n\n"+(
            f"'(Project: {t['projectDetails']['projectName']}\n"
            f"Milestone of project {t['projectDetails']['projectName']}: {t['milestoneDetails']['milestoneName']}\n"
            f"Task of project {t['projectDetails']['projectName']}: {t['taskDetails']['taskName']}\n"
            f"Module of project {t['projectDetails']['projectName']}: {t['taskDetails']['moduleName']}\n"
            f"User ID: {t['userId']}\n"
            f"Time Spent on project {t['projectDetails']['projectName']}: {t['timeSpent']}\n"
            f"Date of creation of project {t['projectDetails']['projectName']}: {t['entryDate']}\n"
            f"Notes of {t['projectDetails']['projectName']}: {t['notes']}\n"
            f"Teams working on project {t['projectDetails']['projectName']} are {', '.join(t['teams']) if t['teams'] else 'None'}\n"
            f"Is {t['projectDetails']['projectName']} a Trainee Task: {'Yes' if t['traineeTask'] else 'No'})'"
        )

    docs.append(
            Document(
                page_content=text,
                metadata={
                    "type": "timesheet"
                }
            )
        )

    splitter= RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )

    split_docs= splitter.split_documents(docs)

    vector_store.add_documents(split_docs)
    print(f"{len(docs)} timesheets stored in vector DB.")


if __name__ == "__main__":
    ingest_timesheets()
