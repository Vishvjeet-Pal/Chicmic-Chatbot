from langchain_community.vectorstores import Qdrant
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitter import RecursiveCharacterTextSplitter
from llm.rag_data import get_all_documents
# from qdrant_client import QdrantClient

embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")    

# def build_rag_index(db, faiss_):