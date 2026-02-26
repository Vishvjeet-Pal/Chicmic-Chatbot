import httpx
from datetime import datetime

def register_organisation_users(mcp):

    @mcp.tool()
    async def get_organisation_users(
        auth_token,
        index: int = 0,
        limit: int = 10,
        name: str = "",
        team: str = "",
        role: str = "",
        active: str = "",  # true / false
        verification_status: str = "",
        from_date: str = "",  # format: YYYY-MM-DD
        to_date: str = ""     # format: YYYY-MM-DD
    ):
        """

        Use this tool when the user asks about:
        - Organisation users list
        - Employee directory
        - List of employees
        - Active or inactive employees
        - Employees by team
        - Employees by role
        - Employees by verification status
        - Employees who joined between specific dates
        - Paginated employee list

        Pagination:
        - index → Page index (default: 0)
        - limit → Records per page (default: 10)

        Filters:
        - name
        - team
        - role
        - active (true/false)
        - verification_status
        - from_date (YYYY-MM-DD)
        - to_date (YYYY-MM-DD)
        """

        url = "https://erp-staging.projectlabs.in/v1/user/list"

        headers = {
            "Authorization": auth_token,
            "Content-Type": "application/json"
        }

        all_items = []
        current_index = 0
        page_limit = limit

        async with httpx.AsyncClient() as client:

            while True:

                body = {
                    "index": current_index,
                    "limit": page_limit
                }

                response = await client.post(
                    url,
                    headers=headers,
                    json=body
                )

                if response.status_code == 401:
                    return "Unauthorized access. Please login again."

                if response.status_code == 403:
                    return "You are not authorized to access this information."

                if response.status_code != 200:
                    return f"Failed to fetch users. Status Code: {response.status_code}"

                response_json = response.json()
                items = response_json.get("data", {}).get("items", [])
                total_count = response_json.get("data", {}).get("totalCount", 0)

                if not items:
                    break

                all_items.extend(items)
                current_index += page_limit

                if len(all_items) >= total_count:
                    break

        if not all_items:
            return "No users found."

        filtered_users = []

        for user in all_items:

            employee_name = user.get("employeeFullName", "")
            team_names = user.get("teamNames", "")
            user_role = user.get("role", "")
            is_active = str(user.get("active")).lower()
            verification = user.get("verificationStatus", "")
            joining_date_raw = user.get("joiningDate", "")

            joining_date_obj = None
            if joining_date_raw:
                try:
                    joining_date_obj = datetime.fromisoformat(
                        joining_date_raw.replace("Z", "")
                    )
                except:
                    pass

            if name and name.lower() not in employee_name.lower():
                continue

            if team and team.lower() not in team_names.lower():
                continue

            if role and role.lower() != user_role.lower():
                continue

            if active and active.lower() != is_active:
                continue

            if verification_status and verification_status.lower() != verification.lower():
                continue

            if from_date and joining_date_obj:
                if joining_date_obj.date() < datetime.strptime(from_date, "%Y-%m-%d").date():
                    continue

            if to_date and joining_date_obj:
                if joining_date_obj.date() > datetime.strptime(to_date, "%Y-%m-%d").date():
                    continue

            filtered_users.append(user)

        if not filtered_users:
            return "No users matched the given filters."

        formatted_response = []

        for idx, user in enumerate(filtered_users, start=1):

            name_val = user.get("employeeFullName", "N/A")
            email = user.get("officialEmail", "N/A")
            role_val = user.get("role", "N/A")
            designation = user.get("designation", {}).get("name", "N/A")
            team_names = user.get("teamNames", "No Team")
            active_status = "Active" if user.get("active") else "Inactive"
            verification = user.get("verificationStatus", "N/A")
            joining_date_raw = user.get("joiningDate", "")

            formatted_joining_date = "N/A"

            if joining_date_raw:
                try:
                    date_obj = datetime.fromisoformat(
                        joining_date_raw.replace("Z", "")
                    )
                    formatted_joining_date = date_obj.strftime("%d-%m-%Y")
                except:
                    pass

            formatted_response.append(
                f"{idx}. {name_val}\n"
                f"   Email: {email}\n"
                f"   Role: {role_val}\n"
                f"   Designation: {designation}\n"
                f"   Team: {team_names}\n"
                f"   Joining Date: {formatted_joining_date}\n"
                f"   Status: {active_status}\n"
                f"   Verification: {verification}"
            )

        return (
            f"Total Users (API): {len(all_items)}\n"
            f"Filtered Users: {len(filtered_users)}\n\n"
            + "\n\n".join(formatted_response)
        )