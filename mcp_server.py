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

    cached = await redis_client.get(cache_key)
    if cached:
        return f"(cached)\n{cached}"


    result = await search_fn()

    await redis_client.set(cache_key, result, ex=ttl)
    return result


mcp = FastMCP("Company Assistant")


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
   
# @mcp.tool()
# async def search_policy(query: str) -> str:
#     """
#     Search and extract information from company policy documents.

#     This tool retrieves accurate policy details from official company documents such as:
#     - Leave Policy (annual leave, earned leave, casual/sick leave, maternity leave, training leave, probation leave)
#     - Leave Calculation Rules (sandwich rule, pro-rata leave, 5+2 rule, leave deduction, compensatory leave)
#     - Work rules related to leave (approval process, leave during training, leave during probation)

#     Use this tool when the user asks about:
#     - Leave entitlement, leave balance, leave types
#     - How leave is calculated or deducted
#     - Sandwich rule or weekend/holiday leave counting
#     - Working on holidays or compensatory leave
#     - Leave during probation or training
#     - Leave approval process
#     - Any question combining leave + holidays

#     Instructions:
#     - Extract only relevant policy information matching the user query.
#     - If multiple policies are relevant, combine them logically.
#     - If exact answer is not found, return the closest matching policy rule.
#     - If nothing relevant exists, return: "No relevant policy found."
#     - Do NOT generate information outside the documents.
#     """

#     cache_key = f"pdf_policy:{query}"

#     async def search():
#         docs = vector_store.similarity_search(
#             query,
#             k=5
#         )
#         print(docs)
#         if not docs:
#             return "No relevant information found in PDF."

#         return "\n\n".join([d.page_content for d in docs])

#     return await get_cached_or_search(cache_key, search)


@mcp.tool()
async def search_policy(query: str) -> str:
    """
    Search and extract information from company policy documents.

    This tool retrieves accurate policy details from official company documents such as:
    - Leave Policy (annual leave, earned leave, casual/sick leave, maternity leave, training leave, probation leave)
    - Leave Calculation Rules (sandwich rule, pro-rata leave, 5+2 rule, leave deduction, compensatory leave)
    - Work rules related to leave (approval process, leave during training, leave during probation)

    Use this tool when the user asks about:
    - Leave entitlement, leave balance, leave types
    - How leave is calculated or deducted
    - Sandwich rule or weekend/holiday leave counting
    - Working on holidays or compensatory leave
    - Leave during probation or training
    - Leave approval process
    - Any question combining leave + holidays

    Instructions:
    - Extract only relevant policy information matching the user query.
    - If multiple policies are relevant, combine them logically.
    - If exact answer is not found, return the closest matching policy rule.
    - If nothing relevant exists, return: "No relevant policy found."
    - Do NOT generate information outside the documents.
    """

    cache_key = f"leave_policy:{query}"

    async def search():
        docs = vector_store.similarity_search(
            query,
            k=5,
            filter=({"type": {
            "$in": ["leave_policy", "leave_calculation_policy"]
        }})
        )
        print(docs)
        if not docs:
            return "No relevant information found in PDF."

        return "\n\n".join([d.page_content for d in docs])

    return await get_cached_or_search(cache_key, search)


@mcp.tool()
async def referral_policy(query: str) -> str:
    """Provide information about the employee referral policy based on the content of the uploaded PDF documents."""

    cache_key = f"referral_policy:{query}"

    async def search():
        docs = vector_store.similarity_search(
            query,
            k=2,
            filter={"type": "referral_policy"}
        )
        # print(docs)
        if not docs:
            return "No relevant information found in PDF."

        return "\n\n".join([d.page_content for d in docs])

    return await get_cached_or_search(cache_key, search)

@mcp.tool()
async def timesheet_search(query: str) -> str:
    """
    Use this tool ONLY when the user asks about:
    - projects
    - teams
    - timesheets
    - tasks
    - time spent
    - milestones
    - modules
    - work logs
    - employee work details

    This tool searches timesheet/project information from the vector database.
    """
    cache_key = f"timesheet:{query}"

    async def search():
        docs = vector_store.similarity_search(
            query,
            k=2,
            filter={"type": "timesheet"}
        )
        # print(docs)
        if not docs:
            return "No relevant information found."

        return "\n\n".join([d.page_content for d in docs])

    return await get_cached_or_search(cache_key, search)

@mcp.tool()
async def list_holidays(query: str) -> str:
    """
    Use this tool ONLY when the user asks about holidays.
    - Company holiday dates or holiday rules
    - Upcoming holidays or next holiday
    - Holiday calendar for a specific year
    - Leave planning with holidays
    This tool searches holidays calendar from the vector database.
    """
    cache_key = f"holiday:{query}"

    async def search():
        docs = vector_store.similarity_search(
            query,
            k=2,
            filter={"type": "holiday_calendar"}
        )
        # print(docs)
        if not docs:
            return "No relevant information found."

        return "\n\n".join([d.page_content for d in docs])

    return await get_cached_or_search(cache_key, search)

if __name__ == "__main__":
    mcp.run(transport="stdio")