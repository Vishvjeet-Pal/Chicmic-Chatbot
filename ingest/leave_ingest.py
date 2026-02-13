import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from langchain_core.documents import Document
from scrape_data.leave_policy import leave_policies
from langchain_text_splitters import RecursiveCharacterTextSplitter
from mcp_server import vector_store

def ingest_leave_policy():
    docs=[
        Document(
            page_content = leave_policies,
            metadata = {"source": "leave_policy", "type":"leave_policy"}
        )
    ]

    splitter= RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )

    split_docs= splitter.split_documents(docs)

    vector_store.add_documents(split_docs)

if __name__ == "__main__":
    ingest_leave_policy()