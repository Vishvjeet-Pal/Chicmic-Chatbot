import httpx 

def register_tracker_details(mcp):
    @mcp.tool()
    async def get_tracker_details(auth_token: str) -> str:
        """
        Use this tool when user asks about:
        - Tracker details
        - Allocated users in tracker
        - Project linked to tracker
        - My trackers (backend filters by token)

        args: auth_token
        """

        TRACKER_API_URL = "https://api.portal.chicmicstudios.in/v1/project/trackers/detail"

        # auth_token = config.get("configurable", {}).get("auth_token")

        if not auth_token:
            return "Authorization token is missing."

        headers = {
            "Authorization": auth_token,
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(TRACKER_API_URL, headers=headers)

                if response.status_code == 401:
                    return "Unauthorized access. Please login again."

                if response.status_code == 403:
                    return "You are not authorized to view tracker details."

                if response.status_code != 200:
                    return f"Error: Received {response.status_code} from API."

                response_json = response.json()
                tracker_list = response_json.get("data", {}).get("trackerData", [])

                if not tracker_list:
                    return "No tracker data found."

                formatted_output = []

                for tracker in tracker_list:
                    tracker_name = tracker.get("trackerName", "N/A")
                    tracker_email = tracker.get("email", "N/A")
                    tracker_owner = tracker.get("name", "N/A")

                    for proj in tracker.get("projectDetail", []):
                        project_name = proj.get("projectName", "N/A")

                        allocated_users = proj.get("allocatedUsers", [])
                        user_list = ", ".join(
                            [u.get("userName", "Unknown") for u in allocated_users]
                        ) or "No allocated users"

                        formatted_output.append(
                            f"Tracker Name: {tracker_name}\n"
                            f"Tracker Owner: {tracker_owner}\n"
                            f"Email: {tracker_email}\n"
                            f"Project: {project_name}\n"
                            f"Allocated Users: {user_list}\n"
                            f"{'-'*40}"
                        )

                return "\n".join(formatted_output)

            except Exception as e:
                return f"Failed to fetch tracker details: {str(e)}"