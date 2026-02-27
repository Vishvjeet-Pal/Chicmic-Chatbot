from utils.redis_cache import get_cached_or_search

def register_search_policy(mcp,vector_store):
    @mcp.tool()
    async def search_policy(query: str) -> str:
        """
Searches company leave policy documents.

Use for queries about: leave types, leave calculation rules, sandwich rule, holiday counting, compensatory leave, probation/training leave, or leave approval process.

Do NOT use for leave balance queries.

Returns only relevant policy text from official documents.
If nothing matches, returns: "No relevant policy found."
"""

        cache_key = f"leave_policy:{query}"

        # async def search():
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

        # return await get_cached_or_search(cache_key, search)