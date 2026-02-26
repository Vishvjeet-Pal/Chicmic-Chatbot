from datetime import datetime
import httpx

def register_approval_project_list(mcp):

    @mcp.tool()
    async def approval_project_list(auth_token, status=""):
        """
        This tool retrieves Approval Project List.

Use this tool when user asks about:
- Project approval list
- Approval projects
- Pending project approvals
- Approved or rejected projects

Filters:
- status: pending / approved / rejected
        """

        APPROVAL_PROJECT_API_URL = "https://erp-staging.projectlabs.in/v1/project/projectRequests/list"

        headers = {
            "Authorization": auth_token,
            "Content-Type": "application/json"
        }

        index = 0
        limit = 10
        all_projects = []

        async with httpx.AsyncClient() as client:
            try:
                # 🔁 Pagination
                while True:
                    response = await client.post(
                        APPROVAL_PROJECT_API_URL,
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

                    all_projects.extend(batch)
                    index += limit

                if not all_projects:
                    return "No approval projects found."

                # 🧠 Status Mapping
                STATUS_MAP = {
                    1: "Pending",
                    2: "Approved",
                    3: "Rejected"
                }

                valid_status_map = {
                    "pending": 1,
                    "approved": 2,
                    "rejected": 3
                }

                status = status.strip().lower()
                formatted_projects = []

                for project in all_projects:

                    # 📌 Filter by status
                    if status:
                        if status not in valid_status_map:
                            continue
                        if project.get("approvalStatus") != valid_status_map[status]:
                            continue

                    # 📅 Requested Date Formatting
                    requested_on = project.get("requestedOn")
                    formatted_date = "N/A"

                    if requested_on:
                        parsed_date = datetime.fromisoformat(requested_on.replace("Z", "+00:00"))
                        formatted_date = parsed_date.strftime("%d-%m-%Y %I:%M %p")

                    # 🧾 Hours Request Data
                    hours_data = project.get("hoursRequestData", {})

                    formatted_projects.append(
                        f"Project Name: {project.get('name')}\n"
                        f"Client Name: {project.get('clientName')}\n"
                        f"Requested By: {project.get('requestedBy')}\n"
                        f"Requested On: {formatted_date}\n"
                        f"Billing Type: {project.get('billingType')}\n"
                        f"Request Type: {project.get('requestType')}\n"
                        f"Approval Status: {STATUS_MAP.get(project.get('approvalStatus'), 'Unknown')}\n"
                        f"Hours Description: {hours_data.get('description', 'N/A')}\n"
                        f"Requested Hours (Seconds): {hours_data.get('requestedHoursInSeconds', 0)}\n"
                        f"Approved Hours (Seconds): {hours_data.get('approvedHoursInSeconds', 0)}\n"
                        f"Team Name: {hours_data.get('teamName', 'N/A')}\n"
                        f"------------------------------------"
                    )

                if not formatted_projects:
                    return "No matching approval projects found."

                return "\n\n".join(formatted_projects)

            except httpx.RequestError as e:
                return f"An error occurred while requesting the API: {str(e)}"