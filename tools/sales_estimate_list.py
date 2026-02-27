import httpx
from datetime import datetime

def register_sales_estimate_list(mcp):

    @mcp.tool()
    async def get_sales_estimate_list(
        auth_token: str,
        index: int = 0,
        limit: int = 10
    ):
        """
Fetches sales estimate list from ERP.

Use for queries about: sales estimates, client estimates, estimate details, assigned teams, or bid estimate status.

Params:
- auth_token (required)
- index (optional, pagination)
- limit (optional, pagination)

Returns client info, job details, budget, teams, status, dates, and total count.
"""

        url = "https://erp-staging.projectlabs.in/v2/estimate"

        params = {
            "index": int(index),
            "limit": int(limit)
        }

        headers = {
            "Authorization": auth_token
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers, params=params)

        if response.status_code != 200:
            return f"Failed to fetch estimate list. Status Code: {response.status_code}"

        result = response.json()

        if not result.get("status"):
            return "API returned unsuccessful response."

        main_data = result.get("data", {})
        estimates = main_data.get("data", [])
        total_count = main_data.get("totalCount", 0)

        if not estimates:
            return "No estimates found."

        formatted_output = []

        for idx, est in enumerate(estimates, start=1):

            client_name = est.get("clientName", "N/A")
            needed_by = est.get("neededBy", "N/A")
            created_at = est.get("createdAt", "N/A")
            updated_at = est.get("updatedAt", "N/A")
            status = est.get("status", "N/A")

            # Format dates safely
            def format_date(date_str):
                try:
                    return datetime.fromisoformat(date_str.replace("Z", "+00:00")).strftime("%d-%m-%Y %I:%M %p")
                except:
                    return date_str

            needed_by = format_date(needed_by)
            created_at = format_date(created_at)
            updated_at = format_date(updated_at)

            bid_details = est.get("bidDetails", {})
            job_title = bid_details.get("jobTitle", "N/A")
            job_url = bid_details.get("jobUrl", "N/A")

            client_details = bid_details.get("clientDetails", {})
            country_list = client_details.get("country", [])
            country = ", ".join([c.get("name", "") for c in country_list]) if country_list else "N/A"

            total_spent = client_details.get("totalAmountSpent", "N/A")
            spent_type = client_details.get("totalAmountSpentType", "")

            # Extract Teams
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
            f"Total Estimates: {total_count}\n\n"
            + "\n".join(formatted_output)
        )