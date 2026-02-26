import httpx

def register_manage_resource(mcp):

    @mcp.tool()
    async def manage_resource_status(auth_token, status=""):
        """
        This tool retrieves resource vacancy status from Project → Manage Resource.

Use this tool when user asks about:
- Which employees are vacant
- Which employees are occupied
- Team resource availability
- Resource status list

Filters:
- status: vacant / occupied
        """

        MANAGE_RESOURCE_API_URL = "https://api.portal.chicmicstudios.in/v1/project/manage/resource"

        headers = {
            "Authorization": auth_token,
            "Content-Type": "application/json"
        }

        index = 0
        limit = 10
        all_teams = []

        async with httpx.AsyncClient() as client:
            try:
                # 🔁 Pagination
                while True:
                    response = await client.post(
                        MANAGE_RESOURCE_API_URL,
                        headers=headers,
                        json={"index": index, "limit": limit}
                    )

                    if response.status_code == 401:
                        return "Unauthorized access. Please login again."

                    if response.status_code == 403:
                        return "You are not authorized to access this information."

                    if response.status_code != 200:
                        return f"Error: Received {response.status_code} from API."

                    batch = response.json().get("data", {}).get("data", [])

                    if not batch:
                        break

                    all_teams.extend(batch)
                    index += limit

                if not all_teams:
                    return "No resource data found."

                # 🧠 Status Mapping
                STATUS_MAP = {
                    1: "Vacant",
                    2: "Occupied"
                }

                valid_status_map = {
                    "vacant": 1,
                    "occupied": 2
                }

                status = status.strip().lower()
                formatted_output = []

                for team in all_teams:

                    team_name = team.get("teamName", "N/A")
                    vacant_count = team.get("vacant", 0)
                    occupied_count = team.get("occupied", 0)

                    team_block = [
                        f"Team: {team_name}",
                        f"Total Vacant: {vacant_count}",
                        f"Total Occupied: {occupied_count}",
                        "Employees:"
                    ]

                    for resource in team.get("resources", []):

                        resource_status = resource.get("vacantStatus")

                        # 📌 Filter by status
                        if status:
                            if status not in valid_status_map:
                                continue
                            if resource_status != valid_status_map[status]:
                                continue

                        employee_status = STATUS_MAP.get(resource_status, "Unknown")

                        team_block.append(
                            f"- {resource.get('name')} "
                            f"(Status: {employee_status}, "
                            f"InHouse Time: {resource.get('inHouseProjectTime')} sec, "
                            f"Client Time: {resource.get('clientProjectTime')} sec)"
                        )

                    formatted_output.append("\n".join(team_block))
                    formatted_output.append("------------------------------------")

                if not formatted_output:
                    return "No matching resources found."

                return "\n\n".join(formatted_output)

            except httpx.RequestError as e:
                return f"An error occurred while requesting the API: {str(e)}"