from datetime import datetime
import httpx

def register_management_designations(mcp):

    @mcp.tool()
    async def management_designation_list(auth_token, status=""):
        """
        This tool retrieves designations from Management → Designations.

Use this tool when user asks about:
- Designation list
- Active designations
- Inactive designations
- Management designation records

Filters:
- status: active / inactive
        """

        DESIGNATION_API_URL = "https://api.portal.chicmicstudios.in/v1/management/designations"

        headers = {
            "Authorization": auth_token,
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(DESIGNATION_API_URL, headers=headers)

                if response.status_code == 401:
                    return "Unauthorized access. Please login again."

                if response.status_code == 403:
                    return "You are not authorized to access this information."

                if response.status_code != 200:
                    return f"Error: Received {response.status_code} from API."

                designations = response.json().get("data", {}).get("items", [])

                if not designations:
                    return "No designations found."

                valid_status_map = {
                    "active": True,
                    "inactive": False
                }

                status = status.strip().lower()
                formatted_output = []

                for des in designations:

                    is_active = des.get("isActive", False)

                    # 📌 Status Filter
                    if status:
                        if status not in valid_status_map:
                            continue
                        if is_active != valid_status_map[status]:
                            continue

                    # 📅 Format Dates
                    created_at = des.get("createdAt")
                    updated_at = des.get("updatedAt")

                    formatted_created = "N/A"
                    formatted_updated = "N/A"

                    if created_at:
                        parsed_created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                        formatted_created = parsed_created.strftime("%d-%m-%Y %I:%M %p")

                    if updated_at:
                        parsed_updated = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
                        formatted_updated = parsed_updated.strftime("%d-%m-%Y %I:%M %p")

                    formatted_output.append(
                        f"Designation Name: {des.get('name')}\n"
                        f"Status: {'Active' if is_active else 'Inactive'}\n"
                        f"Deleted: {'Yes' if des.get('isDeleted') else 'No'}\n"
                        f"Created On: {formatted_created}\n"
                        f"Updated On: {formatted_updated}\n"
                        f"------------------------------------"
                    )

                if not formatted_output:
                    return "No matching designations found."

                return "\n\n".join(formatted_output)

            except httpx.RequestError as e:
                return f"An error occurred while requesting the API: {str(e)}"