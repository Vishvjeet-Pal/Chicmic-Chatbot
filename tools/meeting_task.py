import httpx
from datetime import datetime, timezone, timedelta

def register_meeting_tool(mcp):

    @mcp.tool()
    async def meeting_history(auth_token):
        """
        Use this tool when the user asks about:
        - Meetings
        - Scheduled meetings
        - Upcoming meetings
        - Meeting details
        - Meeting with CEO
        - Who is attending a meeting
        - Meeting time or description

        Args:
        - auth_token
        """
        MEETING_API_URL = "https://api.portal.chicmicstudios.in/v1/meeting/list?index=0&limit=10"
        headers = {
            "Authorization": auth_token,
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    MEETING_API_URL,
                    headers=headers,
                )

                if response.status_code != 200:
                    return f"API Error {response.status_code}: {response.text}"

                response_json = response.json()
                meeting_data = response_json.get("data", {}).get("data", [])

                if not meeting_data:
                    return "No meeting records found."

                formatted_meetings = []

                for meeting in meeting_data:

                    resources = ", ".join([
                        f"{r.get('employeeFullName')} ({r.get('teamNames')})"
                        for r in meeting.get("resources", [])
                    ])

                    meeting_time = meeting.get("meetingTime")
                    formatted_time = (
                        datetime.fromisoformat(meeting_time.replace("Z", "+00:00"))
                        .strftime("%d %B %Y, %I:%M %p")
                        if meeting_time else "N/A"
                    )


                    created_at = meeting.get("createdAt")

                    formatted_created = (
                        datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                        .astimezone(timezone(timedelta(hours=5, minutes=30)))
                        .strftime("%d %B %Y, %I:%M %p")
                        if created_at else "N/A"
                    )

                    formatted_meetings.append(
                        f"Meeting Title: {meeting.get('title')}\n"
                        f"Meeting Time: {formatted_time}\n"
                        f"Duration: {meeting.get('time')}\n"
                        f"Description: {meeting.get('description')}\n"
                        f"Attendees: {resources}\n"
                        f"Created On: {formatted_created}"
                    )

                return "\n\n".join(formatted_meetings)

            except Exception as e:
                return f"Error while connecting to meeting API: {str(e)}"
