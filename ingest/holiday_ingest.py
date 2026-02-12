import requests
from langchain_core.documents import Document
import os, sys

current_dir = os.path.dirname(os.path.abspath(__file__))

# Parent directory
parent_dir = os.path.dirname(current_dir)

# Add to system path
sys.path.append(parent_dir)

from mcp_server import vector_store

API_URL = "http://localhost:8000/holidays"


def ingest_holidays_from_api():

    print("Fetching holidays from API...")

    response = requests.get(API_URL)
    holidays = response.json()

    if not holidays:
        print("No holiday data received.")
        return

    docs = []
    text=""
    for h in holidays:
        text += (
            f"Holiday: {h['holiday']}\n"
            f"Date: {h['date']}\n"
            f"Year: {h['year']}"
        )

    docs.append(
            Document(
                page_content=text,
                metadata={
                    "type": "holiday",
                    "year": "2026",
                }
            )
        )

    vector_store.add_documents(docs)

    print(f"{len(docs)} holidays stored in vector DB.")

if __name__ == "__main__":
    ingest_holidays_from_api()
