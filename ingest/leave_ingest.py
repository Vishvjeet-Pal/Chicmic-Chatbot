import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from langchain_core.documents import Document
from scrape_data.leave_policy import leave_policies
from langchain_text_splitters import RecursiveCharacterTextSplitter
from mcp_server import vector_store
import hashlib
import datetime

def get_chunk_id(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()

def ingest_leave_policy(policy_text=None):
    if policy_text is None:
        from scrape_data.leave_policy import leave_policies as policy_text

    docs = [
        Document(
            page_content=policy_text,
            metadata={"source": "leave_policy", "type": "leave_policy"}
        )
    ]

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )
    split_docs = splitter.split_documents(docs)

    # 🔹 Get existing metadata from Chroma (dict format)
    existing = vector_store._collection.get(where={"type": "leave_policy"})
    existing_metadatas = existing.get("metadatas", []) or []

    existing_ids = {
        m.get("chunk_id")
        for m in existing_metadatas
        if m and m.get("chunk_id")
    }

    new_chunks = []
    new_chunk_ids = set()

    # 🔹 Prepare new chunks
    for chunk in split_docs:
        chunk_id = get_chunk_id(chunk.page_content)

        chunk.metadata["chunk_id"] = chunk_id
        chunk.metadata["updated_at"] = datetime.date.today().isoformat()
        chunk.metadata["source"] = "leave_policy"
        chunk.metadata["type"] = "leave_policy"

        new_chunk_ids.add(chunk_id)

        if chunk_id not in existing_ids:
            new_chunks.append(chunk)

    # 🔹 Delete removed/changed chunks
    chunks_to_delete = existing_ids - new_chunk_ids

    for cid in chunks_to_delete:
        vector_store._collection.delete(where={"chunk_id": cid})

    # 🔹 Add new chunks
    if new_chunks:
        vector_store.add_documents(new_chunks)
        print(f"✅ {len(new_chunks)} new/updated chunks added to vector DB")
    else:
        print("✅ No changes detected. Vector DB already up to date.")

