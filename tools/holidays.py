from utils.redis_cache import get_cached_or_search

def register_holidays(mcp,vector_store):
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