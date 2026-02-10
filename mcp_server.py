# mcp_server.py
from mcp.server.fastmcp import FastMCP
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
import os
from vector_data import vector_store
mcp = FastMCP("Company Assistant")

# 1. Initialize Ollama Embeddings
# This must match the model you used to index the data
embeddings = OllamaEmbeddings(model="llama3.1")

@mcp.tool()
async def search_faq(query: str) -> str:
    """Find answers to FAQs using semantic similarity search."""
    # Perform similarity search instead of SQL WHERE
    docs = vector_store.similarity_search(query, k=3, filter={"type": "faq"})
    
    if not docs:
        return "No relevant FAQ found for your query."
    
    results = []
    for doc in docs:
        results.append(f"Q: {doc.metadata.get('question')}\nA: {doc.page_content}")
    
    return "\n---\n".join(results)

@mcp.tool()
async def get_policy_by_semantic_match(query: str) -> str:
    """Find university policies based on the meaning of your query."""
    docs = vector_store.similarity_search(query, k=2, filter={"type": "policy"})
    
    if not docs:
        return "No matching policies found."
    
    return "\n\n".join([f"Policy: {d.metadata.get('title')}\nDetails: {d.page_content}" for d in docs])

if __name__ == "__main__":
    mcp.run(transport="stdio", show_banner=False)