import httpx

def register_leave_sheet(mcp):
    @mcp.tool()
    async def leave_sheet(
        auth_token,
        month,
        year,
        index=0,
        limit=10,
        working_at=1,
        employee_name="",
        employee_id="",
        status="",
        unpaid="",
        is_waiver=""
    ):
        """
Fetches monthly employee leave sheet (calendar view).

Use for queries about: leave calendar, monthly leave report, leave balance, unpaid leaves, or leave status by date.

Filters supported:
- employee_name, employee_id
- status (daily leave code)
- unpaid (true/false)
- is_waiver (true/false)
- month, year (required)

Param: auth_token (required), others optional.
"""

        LEAVE_SHEET_API_URL = "https://erp-staging.projectlabs.in/v1/leave/calender"

        headers = {
            "Authorization": auth_token,
            "Content-Type": "application/json"
        }

        params = {
            "index": index,
            "limit": limit,
            "month": month,
            "year": year,
            "workingAt": working_at
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    LEAVE_SHEET_API_URL,
                    headers=headers,
                    params=params
                )

                if response.status_code == 401:
                    return "Unauthorized access. Please login again."

                if response.status_code == 403:
                    return "You are not authorized to access this information."

                if response.status_code != 200:
                    return f"Error: Received {response.status_code} from API."

                response_json = response.json()
                employees = response_json.get("data", {}).get("data", [])
                total_count = response_json.get("data", {}).get("totalCount", 0)

                if not employees:
                    return "No leave records found."

                formatted_records = []

                for emp in employees:

                    # Employee-level filtering
                    if employee_name and employee_name.lower() not in (emp.get("name") or "").lower():
                        continue

                    if employee_id and employee_id.lower() not in (emp.get("employeeId") or "").lower():
                        continue

                    if is_waiver and str(emp.get("isWaiver")).lower() != is_waiver.lower():
                        continue

                    attendance = emp.get("attendance", {})
                    stats = emp.get("stats", [])

                    for stat in stats:

                        # Day-level filtering
                        if status and status != stat.get("status"):
                            continue

                        if unpaid and str(stat.get("unPaid")).lower() != unpaid.lower():
                            continue

                        formatted_records.append(
                            f"Employee Name: {emp.get('employeeFullName')}\n"
                            f"Employee ID: {emp.get('employeeId')}\n"
                            f"Joining Date: {emp.get('joiningDate')}\n"
                            f"Date: {stat.get('stats')}\n"
                            f"Leave Status: {stat.get('status') or 'Present'}\n"
                            f"Unpaid: {stat.get('unPaid')}\n"
                            f"Leaves Taken: {attendance.get('leavesTaken')}\n"
                            f"Leave Balance (Start of Month): {attendance.get('monthStartedLeaveBalance')}\n"
                            f"Unpaid Leaves: {attendance.get('unpaidLeaves')}\n"
                            f"Total Working Days: {attendance.get('totalWorkinDays')}\n"
                            f"Is Waiver: {emp.get('isWaiver')}\n"
                        )

                if not formatted_records:
                    return "No leave records found."

                return (
                    f"Total Employees Count: {total_count}\n\n" +
                    "\n\n".join(formatted_records)
                )

            except httpx.RequestError as e:
                return f"An error occurred while requesting the API: {str(e)}"