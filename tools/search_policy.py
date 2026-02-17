from utils.redis_cache import get_cached_or_search

def register_search_policy(mcp,vector_store):
    @mcp.tool()
    async def search_policy(query: str) -> str:
        """
        Search and extract information from company policy documents.
        DO NOT use this tool if user asks about LEAVE BALANCE
        This tool retrieves accurate policy details from official company documents such as:
        - Leave Policy (annual leave, earned leave, casual/sick leave, maternity leave, training leave, probation leave)
        - Leave Calculation Rules (sandwich rule, pro-rata leave, 5+2 rule, leave deduction, compensatory leave)
        - Work rules related to leave (approval process, leave during training, leave during probation)

        Use this tool when the user asks about:
        - leave types
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