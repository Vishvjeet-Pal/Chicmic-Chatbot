from langchain.schema import Document
from scrape_data.holiday_calendar import holiday_calendar
from langachain_text_splitter import RecursiveCharacterTextSplitter
from mcp_server import vector_store

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