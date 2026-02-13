import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# print(sys.path)
from scrape_data.leave_calculation_policy import leave_calculation_policies
from mcp_server import vector_store 
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

def ingest_leave_calculation_policy():

    # Original full policy → single large text
    docs = [
        Document(
            page_content=leave_calculation_policies,
            metadata={"type": "leave_calculation_policy"}
        )
    ]

    # 🔥 Split into chunks (VERY IMPORTANT)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,      # good for policy text
        chunk_overlap=100
    )

    split_docs = splitter.split_documents(docs)

    print(f"Total chunks created: {len(split_docs)}")

    # Store in vector DB
    vector_store.add_documents(split_docs)

    print("Leave calculation policy stored in vector DB ✔")

if __name__ == "__main__":
    ingest_leave_calculation_policy()

