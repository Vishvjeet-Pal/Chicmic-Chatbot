import httpx
from datetime import datetime

def register_training_session_list(mcp):

    @mcp.tool()
    async def get_training_session_list(
        auth_token: str,
        limit: int = 10
    ):
        """
        Retrieves all training sessions with automatic pagination.

        Features:
        - Automatic pagination using while loop
        - Fetches all sessions
        - Formats session details cleanly

        Use this tool when user asks about:
        - Training session list
        - Upcoming or past sessions
        - Session status
        - Training module sessions
        """

        base_url = "https://erp-staging.projectlabs.in/v1/training/session"
        index = 0
        all_sessions = []

        headers = {
            "Authorization": auth_token
        }

        async with httpx.AsyncClient(timeout=30.0) as client:

            while True:
                url = f"{base_url}?index={index}&limit={limit}"
                response = await client.get(url, headers=headers)

                if response.status_code != 200:
                    return f"Failed to fetch session list. Status Code: {response.status_code}"

                result = response.json()

                if not result.get("success"):
                    return "API returned unsuccessful response."

                sessions = result.get("data", [])
                total_count = result.get("count", 0)

                if not sessions:
                    break

                all_sessions.extend(sessions)
                index += limit

                if len(all_sessions) >= total_count:
                    break

        if not all_sessions:
            return "No training sessions found."

        # Format output
        formatted_response = []
        for idx, session in enumerate(all_sessions, start=1):
            title = session.get("title", "N/A")
            date = session.get("date", "N/A")
            time = session.get("time", "N/A")
            location = session.get("locationName", "N/A")
            status = session.get("status", "N/A")
            approved = session.get("isApproved", False)
            mom_message = session.get("mom", {}).get("message", "N/A")

            # Optional: Combine date & time into readable format
            date_time = f"{date} {time}" if date != "N/A" and time != "N/A" else "N/A"
            try:
                parsed = datetime.fromisoformat(date_time.replace("Z", "+00:00"))
                date_time = parsed.strftime("%d-%B-%Y %I:%M %p")
            except:
                pass

            formatted_response.append(
                f"{idx}. Title: {title}\n"
                f"   Date & Time: {date_time}\n"
                f"   Location: {location}\n"
                f"   Status: {status}\n"
                f"   Approved: {'Yes' if approved else 'No'}\n"
                f"   MOM: {mom_message}\n"
                f"{'-'*40}"
            )

        return (
            f"Total Sessions: {total_count}\n"
            f"Fetched: {len(all_sessions)}\n\n"
            + "\n".join(formatted_response)
        )