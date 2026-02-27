import httpx

def register_leave_application(mcp):
    @mcp.tool()
    async def leave_application(auth_token, request_data, employee_name="", status=""):
        """
Fetches leave applications of other employees.

Use for queries about: employee leave history, leave status, leave between dates, or leave records by year.

Filters supported:
- employee_name
- status (Pending/Approved/Rejected/Cancelled)

Param: auth_token (required), request_data (required), others optional.
"""

        LEAVE_APPLICATION_API_URL = "https://api.portal.chicmicstudios.in/v1/leave/requests"

        headers = {
            "Authorization": auth_token,
            "Content-Type": "application/json"
        }

        index = 0
        limit = 10
        all_leave_applications = []

        async with httpx.AsyncClient() as client:
            try:
                while True:
                    response = await client.post(
                        LEAVE_APPLICATION_API_URL,
                        headers=headers,
                        json={"index": index, "limit": limit}
                    )

                    if response.status_code == 401:
                        return "Unauthorized access. Please login again."

                    if response.status_code == 403:
                        return "You are not authorized to access this information."

                    if response.status_code != 200:
                        return f"Error: Received {response.status_code} from API."

                    leave_batch = response.json().get("data", {}).get("data", [])

                    if not leave_batch:
                        break

                    all_leave_applications.extend(leave_batch)
                    index += 10

                if not all_leave_applications:
                    return "No leave applications found."

                STATUS_MAP = {
                    1: "Pending",
                    2: "Approved",
                    3: "Rejected",
                    4: "Cancelled"
                }

                # Normalize status filter
                status = status.strip().lower()
                valid_status_map = {
                    "pending": 1,
                    "approved": 2,
                    "rejected": 3,
                    "cancelled": 4
                }

                formatted_leaves = []

                for leave in all_leave_applications:

                    # Filter by employee_name if provided
                    if employee_name:
                        if employee_name.lower() not in (leave.get("employeeFullName") or "").lower():
                            continue

                    # Filter by status if provided
                    if status:
                        if status not in valid_status_map:
                            continue
                        if leave.get("status") != valid_status_map[status]:
                            continue

                    leave_reason = leave.get("leaveReason", {})
                    send_to = ", ".join([u.get("employeeFullName", "") for u in leave.get("sendTo", [])])
                    mail_to = ", ".join([u.get("employeeFullName", "") for u in leave.get("mailTo", [])])
                    teams = leave.get("team", "")

                    formatted_leaves.append(
                        f"Employee Name: {leave.get('employeeFullName')} belongs to "
                        f"Team: {teams} and is "
                        f"Reporting To : {leave.get('reportingTo')}, "
                        f"has applied leave From Date: {leave.get('fromDate')} "
                        f"To Date: {leave.get('toDate')}\n"
                        f"the Leave Type is : {leave.get('leaveType')}\n"
                        f"Reason of leave: {leave_reason.get('name')}\n"
                        f"Total Days of leaves: {leave.get('totalDays')}\n"
                        f"Half Days: {leave.get('halfDays')}\n"
                        f"Waiver Applied: {leave.get('waiver')}\n"
                        f"Waiver Dates: {leave.get('waiverDates')}\n"
                        f"Sandwich Applied: {leave.get('isSandwichApplied')}\n"
                        f"Status of leave: {STATUS_MAP.get(leave.get('status'), 'Unknown')}\n"
                        f"leave request Send To: {send_to}\n"
                        f"leave request Mail To: {mail_to}\n"
                        f"Year: {leave.get('year')}\n"
                    )

                if not formatted_leaves:
                    return "No leave applications found."

                return "\n\n".join(formatted_leaves)

            except httpx.RequestError as e:
                return f"An error occurred while requesting the API: {str(e)}"