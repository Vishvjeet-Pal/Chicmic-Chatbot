import httpx

def register_sales_direct_messages(mcp):

    @mcp.tool()
    async def get_sales_direct_messages(
        auth_token: str,
        index: int = 0,
        limit: int = 10
    ):
        """
        This tool fetches Sales Direct Messages (Client List).

        Use this tool when user asks about:
        - Direct messages
        - Sales client list
        - Bid direct messages
        - Upwork client chats
        - Direct client conversation list

        Required:
        - auth_token

        Optional:
        - index (default: 0)
        - limit (default: 10)

        Returns:
        - Client Name
        - Country
        - Job Title
        - Hire Rate
        - Jobs Posted
        - Total Amount Spent
        - Room URL
        - Upwork ID
        - Status
        - Created / Handled By
        - Total Count
        """

        url = f"https://erp-staging.projectlabs.in/v1/bid/directMessage?limit={limit}&index={index}"

        headers = {
            "Authorization": auth_token
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers)

        if response.status_code != 200:
            return f"Failed to fetch direct messages. Status Code: {response.status_code}"

        result = response.json()

        if not result.get("status"):
            return "API returned unsuccessful response."

        main_data = result.get("data", {})
        clients = main_data.get("data", [])
        total_count = main_data.get("totalCount", 0)

        if not clients:
            return "No direct messages found."

        formatted_response = []

        for idx, client in enumerate(clients, start=1):

            client_name = client.get("clientName", "N/A")
            job_title = client.get("jobTitle", "N/A")
            room_url = client.get("roomURL", "N/A")
            upwork_id = client.get("upworkId", "N/A")
            status = client.get("status", "N/A")

            client_details = client.get("clientDetails", {})
            country_list = client_details.get("country", [])
            country_name = ", ".join([c.get("name", "") for c in country_list]) if country_list else "N/A"

            hire_rate = client_details.get("hireRate", 0)
            jobs_posted = client_details.get("jobPosted", 0)
            total_spent = client_details.get("totalAmountSpent", "N/A")

            created_by = client.get("createdBy", {})
            handled_by = client.get("handledBy", {})

            created_by_user = created_by.get("userId", "N/A")
            handled_by_user = handled_by.get("userId", "N/A")

            formatted_response.append(
                f"{idx}. Client Name: {client_name}\n"
                f"   Country: {country_name}\n"
                f"   Job Title: {job_title}\n"
                f"   Hire Rate: {hire_rate}\n"
                f"   Jobs Posted: {jobs_posted}\n"
                f"   Total Amount Spent: {total_spent}\n"
                f"   Upwork ID: {upwork_id}\n"
                f"   Status: {status}\n"
                f"   Created By: {created_by_user}\n"
                f"   Handled By: {handled_by_user}\n"
                f"   Room URL: {room_url}\n"
                f"{'-'*50}"
            )

        return (
            f"Total Direct Message Clients: {total_count}\n\n"
            + "\n".join(formatted_response)
        )