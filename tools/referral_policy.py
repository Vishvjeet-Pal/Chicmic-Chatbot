from utils.redis_cache import get_cached_or_search

def register_referral(mcp,vector_store):
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