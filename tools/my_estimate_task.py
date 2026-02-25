import httpx
from datetime import datetime

def register_estimate_task(mcp):

    @mcp.tool()
    async def estimate_task_summary(
        auth_token,
        client_name="",
        project_name="",
        status=""
    ):
        """
        This tool retrieves estimate task details with timesheet entries.

Use this tool when the user asks about:
- My Estimated tasks
- Client project effort details
- Timesheet entries inside my estimate tasks
- Time spent on my estimate projects
- My Estimate task status

args:
- auth_token: Authorization header token
- client_name (optional): filter by client name
- project_name (optional): filter by project name
- status (optional): pending / approved / rejected
        """

        headers = {
            "Authorization": auth_token,
            "Content-Type": "application/json"
        }

        index = 0
        limit = 10
        all_estimates = []

        async with httpx.AsyncClient() as client:
            try:
                # 🔁 Pagination Loop
                while True:
                    response = await client.get(
                        f"https://api.portal.chicmicstudios.in/v1/estimate/userList?index={index}&limit={limit}",
                        headers=headers
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

                    all_estimates.extend(batch)
                    index += limit

                if not all_estimates:
                    return "No estimate records found."

                # 🧠 Status Mapping
                STATUS_MAP = {
                    1: "Pending",
                    2: "Approved",
                    3: "Rejected"
                }

                VALID_STATUS_MAP = {
                    "pending": 1,
                    "approved": 2,
                    "rejected": 3
                }

                status = status.strip().lower()
                formatted_records = []

                for record in all_estimates:

                    # 🔍 Client Filter
                    if client_name:
                        if client_name.lower() not in (record.get("clientName") or "").lower():
                            continue

                    # 🔍 Project Filter
                    if project_name:
                        if project_name.lower() not in (record.get("projectName") or "").lower():
                            continue

                    # 🔍 Status Filter
                    if status:
                        if status not in VALID_STATUS_MAP:
                            continue
                        if record.get("taskStatus") != VALID_STATUS_MAP[status]:
                            continue

                    # 📅 Format Main Entry Date
                    entry_date_raw = record.get("entryDate")
                    try:
                        formatted_date = datetime.strptime(
                            entry_date_raw, "%d/%m/%Y"
                        ).strftime("%d-%B-%Y")
                    except:
                        formatted_date = entry_date_raw

                    timesheet = record.get("timesheet", {})
                    time_entries = timesheet.get("time", [])

                    entry_details = []
                    total_time_spent = 0

                    for entry in time_entries:
                        entry_date = entry.get("entryDate", "")[:10]

                        try:
                            formatted_entry_date = datetime.strptime(
                                entry_date, "%Y-%m-%d"
                            ).strftime("%d-%b-%Y")
                        except:
                            formatted_entry_date = entry_date

                        time_spent = entry.get("timeSpent", "00:00")

                        entry_details.append(
                            f"- {formatted_entry_date}: {time_spent} ({entry.get('notes','No notes')})"
                        )

                    formatted_records.append(
                        f"Client Name: {record.get('clientName')}\n"
                        f"Project Name: {record.get('projectName')}\n"
                        f"Created By: {record.get('createdBy')}\n"
                        f"Entry Date: {formatted_date}\n"
                        f"Task Status: {STATUS_MAP.get(record.get('taskStatus'), 'Unknown')}\n"
                        f"Timesheet Owner: {timesheet.get('name')}\n"
                        f"Timesheet Status: {STATUS_MAP.get(timesheet.get('taskStatus'), 'Unknown')}\n"
                        f"Timesheet Entries:\n"
                        f"{chr(10).join(entry_details) if entry_details else 'No time entries found.'}\n"
                    )

                if not formatted_records:
                    return "No matching estimate records found."

                return "\n\n".join(formatted_records)

            except httpx.RequestError as e:
                return f"An error occurred while requesting the API: {str(e)}"