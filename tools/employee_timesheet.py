import httpx
from datetime import datetime

def register_timesheet_summary_tool(mcp):

    @mcp.tool()
    async def timesheet_summary(
        auth_token,
        employee_name="",
        status=""
    ):
        """
        This tool retrieves employee timesheet summary records.

Use this tool when the user asks about:
- Timesheet entries
- Daily work hours
- Timesheet approval status
- Who has submitted timesheet
- Pending timesheet approvals

args:
- auth_token: Authorization header token
- request_data: request body (if required)
- employee_name (optional): filter by employee name
- status (optional): pending / approved / rejected
        """

        

        headers = {
            "Authorization": auth_token,
            "Content-Type": "application/json"
        }

        index = 0
        limit = 10
        all_timesheets = []

        async with httpx.AsyncClient() as client:
            try:
                # 🔁 Pagination Loop
                while True:
                    response = await client.post(
                        f"https://api.portal.chicmicstudios.in/v1/timesheet/timesheetApprove?index={index}&limit=10",
                        headers=headers,
                        json={}
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

                    all_timesheets.extend(batch)
                    index += limit

                if not all_timesheets:
                    return "No timesheet records found."

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

                for ts in all_timesheets:

                    # 🔍 Employee Filter
                    if employee_name:
                        if employee_name.lower() not in (ts.get("name") or "").lower():
                            continue

                    # 🔍 Status Filter
                    if status:
                        if status not in VALID_STATUS_MAP:
                            continue
                        if ts.get("timesheetStatus") != VALID_STATUS_MAP[status]:
                            continue

                    # ⏳ Convert Seconds → HH:MM format
                    total_seconds = ts.get("totalTimeSpentInSeconds", 0)
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60

                    entry_date_raw = ts.get("entryDate")
                    entry_date = datetime.strptime(
                        entry_date_raw[:10], "%Y-%m-%d"
                    )

                    formatted_date = entry_date.strftime("%d-%m-%Y")

                    formatted_records.append(
                        f"Employee Name: {ts.get('name')}\n"
                        f"Employee ID: {ts.get('employeeId')}\n"
                        f"Team: {ts.get('teamName')}\n"
                        f"Entry Date: {formatted_date} or {datetime.strptime(formatted_date,'%d-%m-%Y').strftime('%d-%B-%Y')} or {datetime.strptime(formatted_date,'%d-%m-%Y').strftime('%d-%b')}\n"
                        f"Projects Worked On: {', '.join(ts.get('projects', []))}\n"
                        f"Total Time Spent: {hours} hours {minutes} minutes\n"
                        f"Timesheet Status: {STATUS_MAP.get(ts.get('timesheetStatus'), 'Unknown')}\n"
                        f"Can Approve: {'Yes' if ts.get('canApprove') else 'No'}\n"
                    )

                if not formatted_records:
                    return "No matching timesheet records found."

                return "\n\n".join(formatted_records)

            except httpx.RequestError as e:
                return f"An error occurred while requesting the API: {str(e)}"