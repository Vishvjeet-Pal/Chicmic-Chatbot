from vector_data import vector_store

# Get ALL stored documents
all_docs = vector_store.get(include=["documents", "metadatas"])

documents = all_docs.get("documents", [])
metadatas = all_docs.get("metadatas", [])

print(f"Total docs in vector store: {len(documents)}\n")

for i, (doc, meta) in enumerate(zip(documents, metadatas), 1):
    print(f"--- Document {i} ---")
    print("Content:")
    print(doc[:200])
    print("\nMetadata:")
    print(meta)
    print("\n" + "="*50 + "\n")

# from scrape_data.leave_calculation_policy import leave_calculation_policies
# print(leave_calculation_policies)