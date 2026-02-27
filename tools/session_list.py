import httpx

def register_training_session_list(mcp):

    @mcp.tool()
    async def get_training_session_list(
        auth_token: str,
        index: int = 0,
        limit: int = 10
    ):
        """
Fetches training session list from ERP.

Use for queries about: training sessions, session details, upcoming/past sessions, session status, or training modules.

Params:
- auth_token (required)
- index (optional, pagination)
- limit (optional, pagination)

Returns session title, date/time, location, status, approval, MOM, and total count.
"""

        url = f"https://erp-staging.projectlabs.in/v1/training/session?index={index}&limit={limit}"

        headers = {
            "Authorization": auth_token
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers)

        if response.status_code != 200:
            return f"Failed to fetch session list. Status Code: {response.status_code}"

        result = response.json()

        if not result.get("success"):
            return "API returned unsuccessful response."

        sessions = result.get("data", [])
        total_count = result.get("count", 0)

        if not sessions:
            return "No training sessions found."

        formatted_response = []

        for session in sessions:
            title = session.get("title", "N/A")
            date = session.get("date", "N/A")
            time = session.get("time", "N/A")
            location = session.get("locationName", "N/A")
            status = session.get("status", "N/A")
            approved = session.get("isApproved", False)
            mom_message = session.get("mom", {}).get("message", "N/A")

            formatted_response.append(
                f"Title: {title}\n"
                f"Date: {date}\n"
                f"Time: {time}\n"
                f"Location: {location}\n"
                f"Status: {status}\n"
                f"Approved: {approved}\n"
                f"MOM/minutes of meeting: {mom_message}\n"
                f"{'-'*30}"
            )

        return (
            f"Total Sessions: {total_count}\n\n" +
            "\n".join(formatted_response)
        )