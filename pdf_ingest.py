# pdf_ingest.py
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import os
from mcp_server import vector_store

# PERSIST_DIR = "./chroma_db"
PDF_PATH = "./data/leave_policy.pdf"   # <-- your pdf path

def extract_pdf_text(path):
    reader = PdfReader(path)
    text = ""
    for page in reader.pages:
        t = page.extract_text()
        if t:
            text += t + "\n"
    # print(text)  # Print the first 500 characters to verify extraction
    return text


def main():
    print("Reading PDF...")
    text = extract_pdf_text(PDF_PATH)

    print("Chunking...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )
    chunks = splitter.split_text(text)

    print("Embedding + storing in Chroma...")

    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    # vector_store = Chroma(
    #     persist_directory=PERSIST_DIR,
    #     embedding_function=embeddings
    # )

    docs = []
    for chunk in chunks:
        # print(chunk)
        docs.append(
            Document(
                page_content=chunk,
                metadata={
                    "type": "policy_pdf",   # IMPORTANT filter tag
                    "source": "policy.pdf"
                }
            )
        )

    vector_store.add_documents(docs)
    # vector_store.persist()
    # print(docs)
    print(f"Stored {len(docs)} PDF chunks successfully!")


if __name__ == "__main__":
    main()
