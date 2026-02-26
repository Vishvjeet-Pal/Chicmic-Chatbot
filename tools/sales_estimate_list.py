import httpx
from datetime import datetime

def register_sales_estimate_list(mcp):

    @mcp.tool()
    async def get_sales_estimate_list(
        auth_token: str,
        limit: int = 10
    ):
        """
        Fetches the complete Sales → Estimate List using automatic pagination.

        Use this tool when user asks about:
        - Sales estimates
        - Estimate list
        - Client estimates
        - Estimate details
        - Estimate assigned teams
        - Bid estimate details

        Required:
        - auth_token

        Optional:
        - limit: number of records per request (default: 10)

        Returns:
        - Client Name
        - Needed By Date
        - Job Title
        - Portal
        - Job URL
        - Country
        - Budget Info
        - Teams Involved
        - Estimate Status
        - Created Date
        - Last Updated
        - Total Count
        """

        BASE_URL = "https://erp-staging.projectlabs.in/v2/estimate"
        index = 0
        all_estimates = []

        headers = {
            "Authorization": auth_token
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                while True:
                    params = {
                        "index": index,
                        "limit": limit
                    }

                    response = await client.get(BASE_URL, headers=headers, params=params)

                    if response.status_code != 200:
                        return f"Failed to fetch estimate list. Status Code: {response.status_code}"

                    result = response.json()
                    if not result.get("status"):
                        return "API returned unsuccessful response."

                    data = result.get("data", {})
                    estimates = data.get("data", [])
                    total_count = data.get("totalCount", 0)

                    if not estimates:
                        break

                    all_estimates.extend(estimates)

                    index += limit
                    if len(all_estimates) >= total_count:
                        break

                if not all_estimates:
                    return "No estimates found."

                def format_date(date_str):
                    try:
                        return datetime.fromisoformat(date_str.replace("Z", "+00:00")).strftime("%d-%m-%Y %I:%M %p")
                    except:
                        return date_str or "N/A"

                formatted_output = []

                for idx, est in enumerate(all_estimates, start=1):
                    client_name = est.get("clientName", "N/A")
                    needed_by = format_date(est.get("neededBy"))
                    created_at = format_date(est.get("createdAt"))
                    updated_at = format_date(est.get("updatedAt"))
                    status = est.get("status", "N/A")

                    bid_details = est.get("bidDetails", {})
                    job_title = bid_details.get("jobTitle", "N/A")
                    job_url = bid_details.get("jobUrl", "N/A")

                    client_details = bid_details.get("clientDetails", {})
                    country_list = client_details.get("country", [])
                    country = ", ".join([c.get("name", "") for c in country_list]) if country_list else "N/A"
                    total_spent = client_details.get("totalAmountSpent", "N/A")
                    spent_type = client_details.get("totalAmountSpentType", "")

                    team_estimates = est.get("teamEstimate", [])
                    team_names = []
                    for team_group in team_estimates:
                        teams = team_group.get("team", [])
                        for t in teams:
                            team_names.append(t.get("name", ""))
                    teams_display = ", ".join(team_names) if team_names else "N/A"

                    formatted_output.append(
                        f"{idx}. Client: {client_name}\n"
                        f"   Needed By: {needed_by}\n"
                        f"   Job Title: {job_title}\n"
                        f"   Job URL: {job_url}\n"
                        f"   Country: {country}\n"
                        f"   Total Spent: {total_spent} {spent_type}\n"
                        f"   Teams: {teams_display}\n"
                        f"   Status: {status}\n"
                        f"   Created At: {created_at}\n"
                        f"   Updated At: {updated_at}\n"
                        f"{'-'*60}"
                    )

                return (
                    f"Total Estimates: {total_count}\n"
                    f"Fetched: {len(all_estimates)}\n\n"
                    + "\n".join(formatted_output)
                )

            except httpx.RequestError as e:
                return f"Error while requesting the API: {str(e)}"