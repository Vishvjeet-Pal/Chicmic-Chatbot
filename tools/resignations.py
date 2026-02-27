import httpx

def register_resignations(mcp):
    @mcp.tool()
    async def resignations(
        auth_token,
        index=0,
        limit=10,
        listing_type=2,
        employee_name="",
        team_name="",
        status="",
        is_early_release=""
    ):
        """
Fetches employee resignation records from ERP.

Use for queries about: resignation list, exit records, early release cases, last working day, or resignation status.

Filters supported:
- employee_name
- team_name
- status
- is_early_release (true/false)
- index, limit, listing_type (pagination/control)

Param: auth_token (required).
"""

        RESIGNATION_API_URL = "https://erp-staging.projectlabs.in/v1/resignation/list"

        headers = {
            "Authorization": auth_token,
            "Content-Type": "application/json"
        }

        params = {
            "index": index,
            "limit": limit,
            "listingType": listing_type
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    RESIGNATION_API_URL,
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
                resignations_data = response_json.get("data", {}).get("data", [])
                total_count = response_json.get("data", {}).get("totalCount", 0)

                if not resignations_data:
                    return "No resignation records found."

                formatted_records = []

                for record in resignations_data:

                    # Filtering
                    if employee_name and employee_name.lower() not in (record.get("employeeName") or "").lower():
                        continue

                    teams = ", ".join(
                        [team.get("name") for team in record.get("teamsData", [])]
                    )

                    if team_name and team_name.lower() not in teams.lower():
                        continue

                    if status and str(record.get("status")) != str(status):
                        continue

                    if is_early_release and str(record.get("isEarlyRelease")).lower() != is_early_release.lower():
                        continue

                    formatted_records.append(
                        f"Employee Name: {record.get('employeeName')}\n"
                        f"Team(s): {teams}\n"
                        f"Status: {record.get('status')}\n"
                        f"Early Release: {record.get('isEarlyRelease')}\n"
                        f"Early Release Date: {record.get('earlyReleaseDate')}\n"
                        f"Last Working Day: {record.get('lastWorkingDay')}\n"
                        f"Reason: {record.get('reasonForResignation')}\n"
                        f"Created At: {record.get('createdAt')}\n"
                        f"Actioned By: {record.get('actionedBy')}\n"
                    )

                if not formatted_records:
                    return "No resignation records found."

                return (
                    f"Total Resignations Count: {total_count}\n\n" +
                    "\n\n".join(formatted_records)
                )

            except httpx.RequestError as e:
                return f"An error occurred while requesting the API: {str(e)}"