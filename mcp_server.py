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


import redis.asyncio as redis

# Redis connection
redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True,
    max_connections=10
)

async def get_cached_or_search(cache_key, search_fn, ttl=300):
    # 1. Try cache
    cached = await redis_client.get(cache_key)
    if cached:
        return f"(cached)\n{cached}"

    # 2. Run actual search
    result = await search_fn()

    # 3. Store in Redis
    await redis_client.set(cache_key, result, ex=ttl)
    return result


mcp = FastMCP("Company Assistant")

# 1. Initialize Ollama Embeddings
# This must match the model you used to index the data
# embeddings = OllamaEmbeddings(model="llama3.1")
embeddings = OllamaEmbeddings(model="nomic-embed-text")



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



# @mcp.tool()
# async def get_policy_by_semantic_match(query: str) -> str:
#     """Return company policies such as employee leave policy, sick leave, maternity leave, etc."""

#     cache_key = f"policy:{query}"

#     async def search():
#         docs = vector_store.similarity_search(query, k=4, filter={"type": "policy"})
#         if not docs:
#             return "No matching policies found."
#         return "\n\n".join(
#             [f"Policy: {d.metadata.get('title')}\nDetails: {d.page_content}" for d in docs]
#         )

#     return await get_cached_or_search(cache_key, search)


# @mcp.tool()
# async def login_credentials(query: str) -> str:
#     """Provide login support for various company platforms.
#     Answer queries such as:
#     - "How can i reset my password?" or "What if I forget my ERP password?" 
#     """
#     cache_key = f"login:{query}"

#     async def search():
#         docs = vector_store.similarity_search(query, k=4, filter={"type": "login"})
#         if not docs:
#             return "No relevant credentials found for your query."

#         return "\n\n".join(
#             [f"Question: {d.metadata.get('question')}\nAnswer: {d.page_content}" for d in docs]
#         )

#     return await get_cached_or_search(cache_key, search)

# @mcp.tool()
# async def personal_info(query: str) -> str:
#     """Provide personal information of employees related to the ERP system such as how to access and edit personal details."""
#     cache_key=f"personal_info:{query}"

#     async def search():
#         docs = vector_store.similarity_search(query, k=3, filter={"type": "personal_info"})

#         if not docs:
#             return "No relevant credentials found for your query."
    
#         return "\n\n".join([f"Question: {d.metadata.get('question')}\nAnswer: {d.page_content}" for d in docs])
#     return await get_cached_or_search(cache_key, search)
   
@mcp.tool()
async def search_pdf_policy(query: str) -> str:
    """Search information from uploaded company policy PDF documents.
    Provide information about company policies such as leave policy, sick leave, maternity leave, etc. based on the content of the uploaded PDF documents.
    Provide hol"""

    cache_key = f"pdf_policy:{query}"

    async def search():
        docs = vector_store.similarity_search(
            query,
            k=2,
            filter={"type": "policy_pdf"}
        )
        print(docs)
        if not docs:
            return "No relevant information found in PDF."

        return "\n\n".join([d.page_content for d in docs])

    return await get_cached_or_search(cache_key, search)


if __name__ == "__main__":
    mcp.run(transport="stdio")