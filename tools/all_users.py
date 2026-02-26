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
        - limit → Number of records per page (default: 10)

         Supported Filters:
        - name → Filter by employee full name
        - team → Filter by team name
        - role → Filter by role (e.g., IND, ADMIN)
        - active → true / false
        - verification_status → Verified / Un-Verified
        - from_date → Joining date from (YYYY-MM-DD)
        - to_date → Joining date to (YYYY-MM-DD)

         Date Format:
        All date filters must be provided in YYYY-MM-DD format.

         Returns:
        - Total user count (from API)
        - Filtered user count
        - Detailed formatted user list
        """

        url = f"https://erp-staging.projectlabs.in/v1/organisation/users?index={index}&limit={limit}"

        headers = {
            "Authorization": auth_token
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)

        if response.status_code != 200:
            return f"Failed to fetch users. Status Code: {response.status_code}"

        response_json = response.json()
        items = response_json.get("data", {}).get("items", [])
        total_count = response_json.get("data", {}).get("totalCount", 0)

        if not items:
            return "No users found."

        filtered_users = []

        for user in items:

            employee_name = user.get("employeeFullName", "")
            team_names = user.get("teamNames", "")
            user_role = user.get("role", "")
            is_active = str(user.get("active")).lower()
            verification = user.get("verificationStatus", "")
            joining_date_raw = user.get("joiningDate", "")

            # Date conversion
            joining_date_obj = None
            if joining_date_raw:
                try:
                    joining_date_obj = datetime.fromisoformat(
                        joining_date_raw.replace("Z", "")
                    )
                except:
                    pass

            # ---- Filtering ----
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

            name = user.get("employeeFullName", "N/A")
            email = user.get("officialEmail", "N/A")
            role = user.get("role", "N/A")
            designation = user.get("designation", {}).get("name", "N/A")
            team_names = user.get("teamNames", "No Team")
            active_status = "Active" if user.get("active") else "Inactive"
            verification = user.get("verificationStatus", "N/A")
            joining_date = user.get("joiningDate", "")

            if joining_date:
                try:
                    joining_date = datetime.fromisoformat(joining_date.replace("Z", "")).strftime("%d-%m-%Y")
                except:
                    pass

            formatted_response.append(
                f"{idx}. {name}\n"
                f"   Email: {email}\n"
                f"   Role: {role}\n"
                f"   Designation: {designation}\n"
                f"   Team: {team_names}\n"
                f"   Joining Date: {joining_date} or {datetime.fromisoformat(joining_date.replace("Z", "")).strftime("%d-%B-%Y")}  or {datetime.fromisoformat(joining_date.replace("Z", "")).strftime("%d-%b-%Y")}\n"
                f"   Status: {active_status}\n"
                f"   Verification: {verification}"
            )

        return (
            f"Total Users (API): {total_count}\n"
            f"Filtered Users: {len(filtered_users)}\n\n"
            + "\n\n".join(formatted_response)
        )