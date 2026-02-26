from datetime import datetime
import httpx

def register_management_skills(mcp):

    @mcp.tool()
    async def management_skill_list(auth_token, search=""):
        """
        This tool retrieves skills from Management → Skills.

Use this tool when user asks about:
- Skills list
- Management skills
- Available skills
- Search skill by name

Filters:
- search: filter by skill name
        """

        SKILL_API_URL = "https://api.portal.chicmicstudios.in/v1/management/skills"

        headers = {
            "Authorization": auth_token,
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(SKILL_API_URL, headers=headers)

                if response.status_code == 401:
                    return "Unauthorized access. Please login again."

                if response.status_code == 403:
                    return "You are not authorized to access this information."

                if response.status_code != 200:
                    return f"Error: Received {response.status_code} from API."

                skills = response.json().get("data", {}).get("items", [])

                if not skills:
                    return "No skills found."

                search = search.strip().lower()
                formatted_output = []

                for skill in skills:

                    skill_name = skill.get("name", "")
                    
                    # 📌 Search Filter
                    if search:
                        if search not in skill_name.lower():
                            continue

                    description = skill.get("description", "N/A")
                    created_by = skill.get("createdByUserName", "N/A")
                    created_at = skill.get("createdAt")

                    # 📅 Format Created Date
                    formatted_date = "N/A"
                    if created_at:
                        parsed_date = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                        formatted_date = parsed_date.strftime("%d-%m-%Y %I:%M %p")

                    formatted_output.append(
                        f"Skill Name: {skill_name}\n"
                        f"Description: {description}\n"
                        f"Created By: {created_by}\n"
                        f"Created On: {formatted_date}\n"
                        f"------------------------------------"
                    )

                if not formatted_output:
                    return "No matching skills found."

                return "\n\n".join(formatted_output)

            except httpx.RequestError as e:
                return f"An error occurred while requesting the API: {str(e)}"