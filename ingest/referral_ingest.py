from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os, sys

current_dir = os.path.dirname(os.path.abspath(__file__))

# Parent directory
parent_dir = os.path.dirname(current_dir)

# Add to system path
sys.path.append(parent_dir)
from scrape_data.referral_policy import referral_policies
from mcp_server import vector_store


def ingest_referral_policy():
    docs=[
        Document(
            page_content = referral_policies,
            metadata = {"source": "referral_policy", "type":"referral_policy"}
        )
    ]

    splitter= RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )

    split_docs= splitter.split_documents(docs)

    vector_store.add_documents(split_docs)
    print("Referral policy ingested successfully")

if __name__ == "__main__":
    ingest_referral_policy()