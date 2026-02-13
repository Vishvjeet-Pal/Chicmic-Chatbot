import os
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

embeddings = OllamaEmbeddings(model="nomic-embed-text")
CHROMA_PATH = os.path.join(os.getcwd(), "chroma_db")
vector_store = Chroma(
    persist_directory=CHROMA_PATH,
    embedding_function=embeddings,
    collection_name="company_data"
)
# from langchain.docstore.document import Document

# def get_all_documents(filter=None):
#     """
#     Fetch all documents from Chroma as Document objects.
#     Optional filter by metadata.
#     """
#     data = vector_store._collection.get(include=["documents", "metadatas"])
#     documents = []

#     for doc_text, metadata in zip(data["documents"], data["metadatas"]):
#         if filter:
#             # Only keep docs matching filter
#             match = all(metadata.get(k) == v for k, v in filter.items())
#             if not match:
#                 continue

#         documents.append(Document(page_content=doc_text, metadata=metadata))

#     return documents
