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


    docs = [
        Document(
            page_content=policy_text,
            metadata={"source": "holiday_calendar", "type": "holiday_calendar"}
        )
    ]

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )
    split_docs = splitter.split_documents(docs)

    # Existing chunks in vector DB
    existing_docs = vector_store._collection.get(filter={"type": "holiday_calendar"})
    existing_ids = [d.metadata.get("chunk_id") for d in existing_docs if d.metadata.get("chunk_id")]

    new_chunks = []
    new_chunk_ids = []

    for chunk in split_docs:
        chunk_id = get_chunk_id(chunk.page_content)
        chunk.metadata["chunk_id"] = chunk_id
        chunk.metadata["updated_at"] = datetime.date.today().isoformat()
        new_chunk_ids.append(chunk_id)
        if chunk_id not in existing_ids:
            new_chunks.append(chunk)

    # Delete removed chunks
    for d in existing_docs:
        if d.metadata.get("chunk_id") not in new_chunk_ids:
            vector_store.delete(filter={"chunk_id": d.metadata.get("chunk_id")})

    # Add new chunks
    if new_chunks:
        vector_store.add_documents(new_chunks)
        print(f"✅ {len(new_chunks)} new chunks added to vector DB")
    else:
        print("✅ No new updates found. Vector DB is up to date.")
