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
embeddings = OllamaEmbeddings(model="llama3.1")



# @mcp.tool()
# async def search_faq(query: str) -> str:
#     """Find answers to FAQs using semantic similarity search.
#     Answer frequently asked questions such as "How do I reset my password?" or "What are office hours?"."""
#     # Perform similarity search instead of SQL WHERE
#     docs = vector_store.similarity_search(query, k=3, filter={"type": "faq"})
    
#     if not docs:
#         return "No relevant FAQ found for your query."
    
#     results = []
#     for doc in docs:
#         results.append(f"Q: {doc.metadata.get('question')}\nA: {doc.page_content}")
    
#     return "\n---\n".join(results)



@mcp.tool()
async def get_policy_by_semantic_match(query: str) -> str:
    """Find company policies based on the meaning of your query."""
    docs = vector_store.similarity_search(query, k=4, filter={"type": "policy"})
    
    if not docs:
        return "No matching policies found."
    for d in docs:
        print(f"Title: {d.metadata.get('title')}, Content: {d.page_content}\n")
    return "\n\n".join([f"Policy: {d.metadata.get('title')}\nDetails: {d.page_content}" for d in docs])


@mcp.tool()
async def login_credentials(query: str) -> str:
    """Provide login support for various company platforms.
    Answer queries such as:
    - "How can i reset my password?" or "What if I forget my ERP password?" 
    - "How can I access my personal and official information in the ERP system?"
    - "How do I edit my personal information in the ERP system?"
    """
    docs = vector_store.similarity_search(query, k=4,filter={"type": "login"})

    if not docs:
        return "No relevant credentials found for your query."
    
    return "\n\n".join([f"Question: {d.metadata.get('question')}\nAnswer: {d.page_content}" for d in docs])
   
@mcp.tool()
async def personal_info(query: str) -> str:
    """Provide personal information of employees related to the ERP system such as how to access and edit personal details"""
    docs = vector_store.similarity_search(query, k=2, filter={"type": "personal_info"})

    if not docs:
        return "No relevant credentials found for your query."
    
    return "\n\n".join([f"Question: {d.metadata.get('question')}\nAnswer: {d.page_content}" for d in docs])
   
if __name__ == "__main__":
    mcp.run(transport="stdio")