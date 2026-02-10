import os
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

embeddings = OllamaEmbeddings(model="llama3.1")
CHROMA_PATH = os.path.join(os.getcwd(), "chroma_db")
vector_store = Chroma(
    persist_directory=CHROMA_PATH,
    embedding_function=embeddings,
    collection_name="company_data"
)
