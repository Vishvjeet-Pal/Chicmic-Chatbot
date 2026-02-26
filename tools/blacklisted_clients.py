import httpx

def register_blacklisted_clients(mcp):
    @mcp.tool()
    async def blacklisted_clients(
        auth_token,
        index=0,
        limit=10,
        client_name="",
        country_name="",
        min_hired_ratio="",
        min_total_jobs="",
        min_amount_spent=""
    ):
        """
        This tool retrieves the list of blacklisted clients from the ERP system.

Use this tool when the user asks about:
- Blacklisted clients
- Restricted clients
- Clients with low hire ratio
- Risky clients
- Client blacklist report
- Country-wise blacklisted clients
- Spending details of blacklisted clients

The tool returns formatted blacklisted client data containing:

- Client Name
- Country
- Blacklisted Date
- Hired Ratio
- Total Jobs Posted
- Total Amount Spent
- Created By
- Updated By

        args:
        - auth_token: Authentication token for API access.
        - index: Pagination index (default 0).
        - limit: Pagination limit (default 10).
        - client_name: (Optional) Filter by client name.
        - country_name: (Optional) Filter by country name.
        - min_hired_ratio: (Optional) Minimum hired ratio filter.
        - min_total_jobs: (Optional) Minimum total jobs posted filter.
        - min_amount_spent: (Optional) Minimum total amount spent filter.
        """

        BLACKLIST_API_URL = "https://erp-staging.projectlabs.in/v1/bid/blacklistedClient"

        headers = {
            "Authorization": auth_token,
            "Content-Type": "application/json"
        }

        params = {
            "index": index,
            "limit": limit
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    BLACKLIST_API_URL,
                    headers=headers,
                    params=params
                )

                if response.status_code == 401:
                    return "Unauthorized access. Please login again."

                if response.status_code == 403:
                    return "You are not authorized to access this information."

                if response.status_code != 200:
                    return f"Error: Received {response.status_code} from API."

                response_json = response.json()
                clients = response_json.get("data", {}).get("data", [])
                total_count = response_json.get("data", {}).get("totalCount", 0)

                if not clients:
                    return "No blacklisted clients found."

                formatted_records = []

                for client_data in clients:

                    # Filtering
                    if client_name and client_name.lower() not in (client_data.get("clientName") or "").lower():
                        continue

                    if country_name and country_name.lower() not in (client_data.get("countryName") or "").lower():
                        continue

                    if min_hired_ratio and int(client_data.get("hiredRatio", 0)) < int(min_hired_ratio):
                        continue

                    if min_total_jobs and int(client_data.get("totalJobsPosted", 0)) < int(min_total_jobs):
                        continue

                    if min_amount_spent and float(client_data.get("totalAmountSpentInNumbers", 0)) < float(min_amount_spent):
                        continue

                    formatted_records.append(
                        f"Client Name: {client_data.get('clientName')}\n"
                        f"Country: {client_data.get('countryName')}\n"
                        f"Blacklisted Date: {client_data.get('date')}\n"
                        f"Hired Ratio: {client_data.get('hiredRatio')}%\n"
                        f"Total Jobs Posted: {client_data.get('totalJobsPosted')}\n"
                        f"Total Amount Spent: {client_data.get('totalAmountSpent')}{client_data.get('amountSymbol')}\n"
                        f"Created By User ID: {(client_data.get('createdBy') or {}).get('userId')}\n"
                        f"Updated By User ID: {(client_data.get('updatedBy') or {}).get('userId')}\n"
                    )

                if not formatted_records:
                    return "No blacklisted clients found."

                return (
                    f"Total Blacklisted Clients Count: {total_count}\n\n" +
                    "\n\n".join(formatted_records)
                )

            except httpx.RequestError as e:
                return f"An error occurred while requesting the API: {str(e)}"