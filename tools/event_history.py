import httpx
from datetime import datetime
def register_event_history(mcp):
    @mcp.tool()
    async def get_event_history(auth_token, request_data):
    
        """
Fetches office event/special occasion history.

Use for queries about office events, festivals, event details, participants, duration, or who created/applied the event.

Returns: event name, date, duration, description, applied by, and created date.

Params: auth_token (required), request_data.
"""

    
        EVENT_HISTORY_API_URL = f"https://api.portal.chicmicstudios.in/v1/timesheet/office/event?index=0&limit=10"

        headers = {
                "Authorization": auth_token,
                "Content-Type": "application/json"
            }
            
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(EVENT_HISTORY_API_URL, headers=headers)

                if response.status_code == 401:
                    return "Unauthorized access. Please login again."

                if response.status_code == 403:
                    return "You are not authorized to access this information."

                if response.status_code != 200:
                    return f"Error: Received {response.status_code} from API."

                event_history_data = response.json().get("data", {}).get("data", [])

                return "\n\n".join([
                    f"(You participated in {event.get('eventName')}\n"
                    f"Event Date: {event.get('date')}\n"
                    f"Duration: {event.get('duration')}\n"
                    f"Description: {event.get('description')}\n"
                    f"Applied By: {event.get('appliedByName')}\n"
                    f"Celebrated On: {datetime.fromisoformat(event.get('createdAt').replace('Z', '+00:00')).strftime('%d %B %Y, %I:%M %p') if event.get('createdAt') else 'N/A'})"
                    
                    for event in event_history_data
                ])

            except Exception as e:
                return f"An error occurred while fetching event history: {str(e)}"