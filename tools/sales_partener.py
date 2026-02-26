import httpx
from datetime import datetime

def register_sales_partner_tool(mcp):

    @mcp.tool()
    async def get_sales_partner_records(auth_token: str):
        """
        Fetches the complete Sales Partner list with pagination.

        Use this tool when the user asks about:
        - Sales partner list
        - Partner details
        - Partner company
        - Partner by name
        - Paginated sales partners
        - Search sales partner

        Args:
        - auth_token: provided in Authorization header of the request
        """

        BASE_URL = "https://erp-staging.projectlabs.in/v1/salesPartner"
        index = 0
        limit = 10
        all_partners = []

        headers = {
            "Authorization": auth_token,
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                # 🔁 Pagination loop
                while True:
                    url = f"{BASE_URL}?index={index}&limit={limit}"
                    response = await client.get(url, headers=headers)

                    if response.status_code != 200:
                        return f"API returned status code: {response.status_code}"

                    result = response.json()
                    partners = result.get("data", {}).get("items", [])
                    total_count = result.get("data", {}).get("totalCount", 0)

                    if not partners:
                        break

                    all_partners.extend(partners)
                    index += limit

                    if len(all_partners) >= total_count:
                        break

                if not all_partners:
                    return "No sales partner records found."

                # Format output
                formatted_response = []
                for idx, partner in enumerate(all_partners, start=1):
                    created_date = partner.get("createdAt")
                    formatted_date = "N/A"
                    readable_date = "N/A"

                    if created_date:
                        try:
                            parsed_date = datetime.fromisoformat(created_date.replace("Z", "+00:00"))
                            formatted_date = parsed_date.strftime("%d-%m-%Y")
                            readable_date = parsed_date.strftime("%d-%B-%Y")
                        except:
                            formatted_date = created_date
                            readable_date = created_date

                    # Optional human-readable comparison
                    today_str = datetime.today().strftime("%d-%m-%Y")
                    short_label = "today" if formatted_date == today_str else parsed_date.strftime("%d-%b") if created_date else "N/A"

                    formatted_response.append(
                        f"{idx}. Partner Name: {partner.get('name', 'N/A')}\n"
                        f"   Company Name: {partner.get('companyName', 'N/A')}\n"
                        f"   Email: {partner.get('email', 'N/A')}\n"
                        f"   Created On: {formatted_date} | {readable_date} | {short_label}\n"
                        f"   Deleted: {partner.get('isDeleted', False)}"
                    )

                return (
                    f"Total Partners: {total_count}\n"
                    f"Fetched: {len(all_partners)}\n\n"
                    + "\n\n".join(formatted_response)
                )

            except Exception as e:
                return f"Error while connecting to sales partner API: {str(e)}"