from langchain.schema import Document
from scrape_data.referral_policy import referral_policies
from langachain_text_splitter import RecursiveCharacterTextSplitter
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

if __name__ == "__main__":
    ingest_referral_policy()