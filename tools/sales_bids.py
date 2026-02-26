import httpx
from datetime import datetime


def register_sales_bid_list(mcp):

    @mcp.tool()
    async def get_sales_bid_list(
        auth_token: str,
        index: int = 0,
        limit: int = 10
    ):
        """
        This tool fetches the Sales Bid List (List of Bids).

        Supports pagination using index and limit.
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
            try:
                response = await client.post(url, headers=headers, json=payload)

                if response.status_code == 401:
                    return "Unauthorized access. Please login again."

                if response.status_code == 403:
                    return "You are not authorized to access this information."

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

                # ✅ Proper Pagination Indexing Logic
                starting_number = (int(index) * int(limit)) + 1

                for idx, bid in enumerate(bids, start=starting_number):

                    job_title = bid.get("jobTitle", "N/A")
                    job_url = bid.get("jobUrl", "N/A")
                    job_type = bid.get("jobType", "N/A")
                    status = bid.get("status", "N/A")
                    client_name = bid.get("clientName", "N/A")

                    portal_details = bid.get("portalIdDetails", {})
                    portal_name = portal_details.get("name", "N/A")

                    client_details = bid.get("clientDetails", {})
                    country_list = client_details.get("country", [])
                    country_name = (
                        ", ".join([c.get("name", "") for c in country_list])
                        if country_list else "N/A"
                    )

                    hire_rate = client_details.get("hireRate", 0)
                    total_spent = client_details.get("totalAmountSpent", 0)

                    booked_by_name = bid.get("bookedByDetails", {}).get("name", "N/A")
                    created_by_name = bid.get("createdByDetails", {}).get("name", "N/A")

                    # 📅 Date Formatting
                    created_at_raw = bid.get("createdAt")
                    created_at = "N/A"
                    if created_at_raw:
                        try:
                            parsed = datetime.fromisoformat(
                                created_at_raw.replace("Z", "+00:00")
                            )
                            created_at = parsed.strftime("%d-%B-%Y %I:%M %p")
                        except:
                            created_at = created_at_raw

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

                ending_number = starting_number + len(bids) - 1

                return (
                    f"Showing {starting_number}–{ending_number} of {total_count} Total Bids\n\n"
                    + "\n".join(formatted_response)
                )

            except httpx.RequestError as e:
                return f"An error occurred while requesting the API: {str(e)}"