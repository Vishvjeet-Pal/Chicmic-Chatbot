import httpx
from datetime import datetime


def register_sales_partner_tool(mcp):

    @mcp.tool()
    async def get_sales_partner_records(
        auth_token,
    ):
        """
        Use this tool when the user asks about:

        - Sales partner list
        - Partner details
        - Partner company
        - Partner by name
        - Paginated sales partners
        - Search sales partner

        args:
        - auth_token
        - page (default: 1)
        - limit (default: 10)
        - search (optional)
        - isDeleted (default: False)
        """

        SALES_PARTNER_API_URL = "https://erp-staging.projectlabs.in/v1/salesPartner?index=0&limit=10"

        headers = {
            "Authorization": auth_token,
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    SALES_PARTNER_API_URL,
                    headers=headers,
                )

                if response.status_code == 200:
                    result = response.json()
                    partner_data = result.get("data", {}).get("items", [])
                    total_count = result.get("data", {}).get("totalCount", 0)

                    if not partner_data:
                        return "No sales partner records found."

                    formatted_response = []

                    for partner in partner_data:

                        created_date = partner.get("createdAt")
                        formatted_date = (
                            datetime.fromisoformat(created_date.replace("Z", "+00:00"))
                            .strftime('%d %B %Y')
                            if created_date else "N/A"
                        )

                        formatted_response.append(
                            f"Partner Name: {partner.get('name', 'N/A')}\n"
                            f"Company Name: {partner.get('companyName', 'N/A')}\n"
                            f"Email: {partner.get('email', 'N/A')}\n"
                            f"Created On: {formatted_date}\n"
                            f"Deleted: {partner.get('isDeleted', False)}"
                        )

                    return (
                    f"Total Partners: {total_count}\n\n"
                        + "\n\n".join(formatted_response)
                    )

                else:
                    return f"API returned status code: {response.status_code}"

            except Exception as e:
                return f"Error while connecting to sales partner API: {str(e)}"