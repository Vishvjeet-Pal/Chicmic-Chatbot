import httpx

def register_management_permission(mcp):

    @mcp.tool()
    async def management_permission_list(auth_token, role="", search=""):
        """
        This tool retrieves employee permissions from Management → Permission.

Use this tool when user asks about:
- Employee roles
- Employee permissions list
- Which team an employee belongs to
- Role-wise employee list

Filters:
- role: PM / TL / IND etc.
- search: filter by employee name or email
        """

        PERMISSION_API_URL = "https://api.portal.chicmicstudios.in/v1/management/permission"

        headers = {
            "Authorization": auth_token,
            "Content-Type": "application/json"
        }

        index = 0
        limit = 10
        all_employees = []

        async with httpx.AsyncClient() as client:
            try:
                # 🔁 Pagination
                while True:
                    response = await client.post(
                        PERMISSION_API_URL,
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

                    all_employees.extend(batch)
                    index += limit

                if not all_employees:
                    return "No employee permission data found."

                role = role.strip().upper()
                search = search.strip().lower()

                formatted_output = []

                for emp in all_employees:

                    emp_role = emp.get("role", "").upper()
                    emp_name = emp.get("name", "")
                    emp_email = emp.get("email", "")

                    # 📌 Role Filter
                    if role and emp_role != role:
                        continue

                    # 📌 Search Filter
                    if search:
                        if search not in emp_name.lower() and search not in emp_email.lower():
                            continue

                    # 👥 Teams Formatting
                    team_names = ", ".join(
                        [team.get("name", "") for team in emp.get("teams", [])]
                    ) or "No Teams Assigned"

                    formatted_output.append(
                        f"Employee Name: {emp_name}\n"
                        f"Employee ID: {emp.get('employeeId')}\n"
                        f"Role: {emp_role}\n"
                        f"Email: {emp_email}\n"
                        f"Teams: {team_names}\n"
                        f"------------------------------------"
                    )

                if not formatted_output:
                    return "No matching employees found."

                return "\n\n".join(formatted_output)

            except httpx.RequestError as e:
                return f"An error occurred while requesting the API: {str(e)}"