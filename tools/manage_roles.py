import httpx

def register_management_roles(mcp):

    @mcp.tool()
    async def management_roles(auth_token, status="", limit: int = 10):
        """
        This tool retrieves roles from Management → Roles.

Use this tool when user asks about:
- List of roles
- Management roles
- Role permissions
- Active or inactive roles

Filters:
- status: active / inactive

Pagination:
- limit: number of records per page (default 10)
  (index auto-increases internally)
        """

        headers = {
            "Authorization": auth_token,
            "Content-Type": "application/json"
        }

        valid_status_map = {
            "active": True,
            "inactive": False
        }

        status = status.strip().lower()
        formatted_roles = []

        index = 0  # ✅ Start from 0

        async with httpx.AsyncClient() as client:
            try:

                while True:  # ✅ Dynamic pagination loop

                    ROLES_API_URL = f"https://erp-staging.projectlabs.in/v1/roles?index={index}&limit={limit}"

                    response = await client.get(ROLES_API_URL, headers=headers)

                    if response.status_code == 401:
                        return "Unauthorized access. Please login again."

                    if response.status_code == 403:
                        return "You are not authorized to access this information."

                    if response.status_code != 200:
                        return f"Error: Received {response.status_code} from API."

                    roles = response.json().get("data", {}).get("items", [])

                    # 🛑 Stop loop if no more data
                    if not roles:
                        break

                    for role in roles:

                        role_status = role.get("status", False)

                        # 📌 Filter by status
                        if status:
                            if status not in valid_status_map:
                                continue
                            if role_status != valid_status_map[status]:
                                continue

                        permissions = role.get("permissions", [])
                        permissions_text = ", ".join(permissions) if permissions else "No specific permissions"

                        formatted_roles.append(
                            f"Role Name: {role.get('name')}\n"
                            f"Role Code: {role.get('role')}\n"
                            f"Status: {'Active' if role_status else 'Inactive'}\n"
                            f"Permissions: {permissions_text}\n"
                            f"Description: {role.get('description', 'N/A')}\n"
                            f"------------------------------------"
                        )

                    # ✅ Increase index dynamically
                    index += 10

                if not formatted_roles:
                    return "No matching roles found."

                return "\n\n".join(formatted_roles)

            except httpx.RequestError as e:
                return f"An error occurred while requesting the API: {str(e)}"