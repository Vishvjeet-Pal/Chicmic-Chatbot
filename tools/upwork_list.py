from datetime import datetime
import httpx

def register_management_upwork_ids(mcp):

    @mcp.tool()
    async def management_upwork_id_list(auth_token, search=""):
        """
        This tool retrieves Upwork ID list from Management → Upwork ID List.

Use this tool when user asks about:
- Upwork ID list
- Upwork accounts
- Tracker emails
- Upwork usernames

Filters:
- search: filter by email or username
        """

        UPWORK_ID_API_URL = "https://erp-staging.projectlabs.in/v1/hours/upworkEmails"

        headers = {
            "Authorization": auth_token,
            "Content-Type": "application/json"
        }

        index = 0
        limit = 10
        all_ids = []

        async with httpx.AsyncClient() as client:
            try:
                # 🔁 Pagination
                while True:
                    response = await client.post(
                        UPWORK_ID_API_URL,
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

                    all_ids.extend(batch)
                    index += limit

                if not all_ids:
                    return "No Upwork IDs found."

                search = search.strip().lower()
                formatted_ids = []

                for item in all_ids:

                    email = item.get("email", "")
                    username = item.get("userName", "")
                    tracker_name = item.get("trackerFullName", "")
                    created_at = item.get("createdAt")

                    # 📌 Search Filter
                    if search:
                        if search not in email.lower() and search not in username.lower():
                            continue

                    # 📅 Format Date
                    formatted_date = "N/A"
                    if created_at:
                        parsed_date = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                        formatted_date = parsed_date.strftime("%d-%m-%Y %I:%M %p")

                    formatted_ids.append(
                        f"Email: {email}\n"
                        f"Username: {username}\n"
                        f"Created On: {formatted_date}\n"
                        f"Tracker Name: {tracker_name}\n"
                        f"------------------------------------"
                    )

                if not formatted_ids:
                    return "No matching Upwork IDs found."

                return "\n\n".join(formatted_ids)

            except httpx.RequestError as e:
                return f"An error occurred while requesting the API: {str(e)}"