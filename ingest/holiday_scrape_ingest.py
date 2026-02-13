from langchain_core.documents import Document
from scrape_data.holiday_calendar import holiday_calendar
from langachain_text_splitters import RecursiveCharacterTextSplitter
from mcp_server import vector_store
import os, sys

current_dir = os.path.dirname(os.path.abspath(__file__))

# Parent directory
parent_dir = os.path.dirname(current_dir)

# Add to system path
sys.path.append(parent_dir)


def ingest_holiday_calendar():
    docs=[
        Document(
            page_content = holiday_calendar,
            metadata = {"source": "holiday_calendar", "type":"holiday_calendar"}
        )
    ]

    splitter= RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )
    split_docs= splitter.split_documents(docs)

    vector_store.add_documents(split_docs)

if __name__ == "__main__":
    ingest_holiday_calendar()