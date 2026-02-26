import httpx

def register_sales_bid_list(mcp):

    @mcp.tool()
    async def get_sales_bid_list(
        auth_token: str,
        index: int = 0,
        limit: int = 10
    ):
        """
        This tool fetches the Sales Bid List (List of Bids).

        Use this tool when user asks about:
        - Sales bids
        - Bid list
        - Upwork bid details
        - Posted job bids
        - Booked bids
        - Bid status list

        Required:
        - auth_token

        Optional:
        - index (default: 0)
        - limit (default: 10)

        Returns:
        - Job Title
        - Portal Name
        - Job URL
        - Job Type
        - Status
        - Client Name
        - Country
        - Hire Rate
        - Total Amount Spent
        - Booked By
        - Created By
        - Created Date
        - Total Count
        """

        url = "https://erp-staging.projectlabs.in/v1/bid/details"

        payload = {
            "index": int(index),
            "limit": int(limit)
        }

        headers = {
            "Authorization": auth_token,
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)

        if response.status_code != 200:
            return f"Failed to fetch bid list. Status Code: {response.status_code}"

        result = response.json()

        if not result.get("status"):
            return "API returned unsuccessful response."

        main_data = result.get("data", {})
        bids = main_data.get("data", [])
        total_count = main_data.get("totalCount", 0)

        if not bids:
            return "No bids found."

        formatted_response = []

        for idx, bid in enumerate(bids, start=1):

            job_title = bid.get("jobTitle", "N/A")
            job_url = bid.get("jobUrl", "N/A")
            job_type = bid.get("jobType", "N/A")
            status = bid.get("status", "N/A")
            client_name = bid.get("clientName", "N/A")

            portal_details = bid.get("portalIdDetails", {})
            portal_name = portal_details.get("name", "N/A")

            client_details = bid.get("clientDetails", {})
            country_list = client_details.get("country", [])
            country_name = ", ".join([c.get("name", "") for c in country_list]) if country_list else "N/A"
            hire_rate = client_details.get("hireRate", 0)
            total_spent = client_details.get("totalAmountSpent", 0)

            booked_by_details = bid.get("bookedByDetails", {})
            booked_by_name = booked_by_details.get("name", "N/A")

            created_by_details = bid.get("createdByDetails", {})
            created_by_name = created_by_details.get("name", "N/A")

            created_at = bid.get("createdAt", "N/A")

            formatted_response.append(
                f"{idx}. Job Title: {job_title}\n"
                f"   Portal: {portal_name}\n"
                f"   Job URL: {job_url}\n"
                f"   Job Type: {job_type}\n"
                f"   Status: {status}\n"
                f"   Client Name: {client_name}\n"
                f"   Country: {country_name}\n"
                f"   Hire Rate: {hire_rate}\n"
                f"   Total Amount Spent: {total_spent}\n"
                f"   Booked By: {booked_by_name}\n"
                f"   Created By: {created_by_name}\n"
                f"   Created At: {created_at}\n"
                f"{'-'*60}"
            )

        return (
            f"Total Bids: {total_count}\n\n"
            + "\n".join(formatted_response)
        )