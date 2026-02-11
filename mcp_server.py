# # mcp_server.py
# from fastmcp import FastMCP
# from sqlalchemy.future import select
# from database import SessionLocal
# from models import FAQ, Policy

# mcp = FastMCP("Company Assistant")

# @mcp.tool()
# async def search_faq(keyword: str) -> str:
#     """Search for frequently asked questions by a keyword."""
#     async with AsyncSessionLocal() as session:
#         query = select(FAQ).where(FAQ.question.contains(keyword))
#         result = await session.execute(query)
#         faqs = result.scalars().all()
        
#         if not faqs:
#             return "No matching FAQs found."
#         return "\n".join([f"Q: {f.question} | A: {f.answer}" for f in faqs])

# @mcp.tool()
# async def get_policy_by_category(category: str) -> str:
#     """Retrieve all university policies within a specific category (e.g., 'Academic', 'Hostel')."""
#     async with AsyncSessionLocal() as session:
#         query = select(Policy).where(Policy.category == category)
#         result = await session.execute(query)
#         policies = result.scalars().all()
        
#         if not policies:
#             return f"No policies found in category: {category}"
#         return "\n".join([f"Title: {p.title}\nDesc: {p.description}" for p in policies])



# mcp_server.py
from mcp.server.fastmcp import FastMCP
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
import os
from vector_data import vector_store
mcp = FastMCP("Company Assistant")

# 1. Initialize Ollama Embeddings
# This must match the model you used to index the data
# embeddings = OllamaEmbeddings(model="llama3.1")
embeddings = OllamaEmbeddings(model="llama3.1:8b")



@mcp.tool()
async def search_faq(query: str) -> str:
    """Find answers to FAQs using semantic similarity search.
    Answer frequently asked questions such as "How do I reset my password?" or "What are office hours?"."""
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
    mcp.run(transport="stdio")