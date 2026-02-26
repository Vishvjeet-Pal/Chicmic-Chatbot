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
        This tool retrieves the leave calendar sheet of employees from the ERP system.

Use this tool when the user asks about:
- Leave sheet
- Leave calendar
- Monthly leave report
- Employee leave summary
- Unpaid leaves
- Leave balance
- Leave taken report
- Leave status by date

The tool returns formatted leave data containing:

- Employee Name
- Employee ID
- Joining Date
- Leave Status (per day)
- Unpaid Flag
- Date
- Leaves Taken
- Leave Balance
- Unpaid Leaves
- Total Working Days
- Is Waiver

        args:
        - auth_token: Authentication token for API access.
        - month: Month number (e.g., 1 for January).
        - year: Year (e.g., 2026).
        - index: Pagination index (default 0).
        - limit: Pagination limit (default 10).
        - working_at: Working location filter (default 1).
        - employee_name: (Optional) Filter by employee name.
        - employee_id: (Optional) Filter by employee ID.
        - status: (Optional) Filter by daily leave status (e.g., S, CL, EL, etc.).
        - unpaid: (Optional) Filter by unpaid leave (true/false).
        - is_waiver: (Optional) Filter by waiver flag (true/false).
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