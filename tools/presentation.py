import httpx
from datetime import datetime, timezone, timedelta

def register_presentation_tool(mcp):

    @mcp.tool()
    async def presentation_details(auth_token):
        """
        Use this tool when the user asks about:
        - Presentations
        - Presentation schedule
        - Presentation topic
        - Who is assigned to presentation
        - Who created the presentation
        - Presentation date or details

        args:
        - auth_token
        """
        PRESENTATION_API_URL="https://erp-staging.projectlabs.in/v1/presentation/list?index=0&limit=10"
        headers = {
            "Authorization": auth_token,
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(PRESENTATION_API_URL, headers=headers)

                if response.status_code != 200:
                    return f"Error: Received {response.status_code} from API."

                presentation_data = response.json().get("data", {}).get("data", [])

                if not presentation_data:
                    return "No presentations found."

                formatted_presentations = []

                for presentation in presentation_data:

                    # Convert to IST
                    utc_time = datetime.fromisoformat(
                        presentation.get("presentationDate").replace("Z", "+00:00")
                    )
                    ist_time = utc_time.astimezone(
                        timezone(timedelta(hours=5, minutes=30))
                    )

                    formatted_date = ist_time.strftime("%d %B %Y, %I:%M %p")

                    resources = ", ".join(
                        [r.get("employeeFullName", "") for r in presentation.get("resources", [])]
                    )

                    formatted_presentations.append(
                        f"Topic: {presentation.get('topic')}\n"
                        f"Presentation Date: {formatted_date}\n"
                        f"Description: {presentation.get('description')}\n"
                        f"Assigned To: {resources}\n"
                        f"Created By: {presentation.get('createdBy')}\n"
                    )

                return "\n\n".join(formatted_presentations)

            except Exception as e:
                return f"Error while connecting to presentation API: {str(e)}"
