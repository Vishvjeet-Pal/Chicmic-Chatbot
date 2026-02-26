import httpx

def register_in_out_others(mcp):
    @mcp.tool()
    async def in_out_others(
        auth_token,
        month,
        year,
        user_id="",
        employee_name="",
        employee_id="",
        team_name="",
        is_wfh="",
        is_holiday="",
        inout_deduction=""
    ):
        """  
        This tool retrieves in/out timesheet details of other employees from the ERP system.

Use this tool when the user asks about:
- In time and out time of other employees
- Monthly attendance report
- Timesheet report of other employees
- In/Out deductions
- WFH details
- Holiday working details
- Employee attendance statistics
- Monthly in/out summary of other employees

The tool returns formatted timesheet data containing:

- Employee Name
- Employee ID
- Official Email
- Role
- Designation
- Team Names
- Min In Time
- Max In Time
- Working Days
- Date
- Is WFH
- Is Holiday
- Leaves Deducted
- In/Out Deduction
- TimeSheet Time

        args:
        - auth_token: The authentication token for API access. Provided in the Authorization header.
        - month: Month number (e.g., 1 for January).
        - year: Year (e.g., 2026).
        - user_id: (Optional) Filter by user ID.
        - employee_name: (Optional) Filter by employee name.
        - employee_id: (Optional) Filter by employee ID.
        - team_name: (Optional) Filter by team name.
        - is_wfh: (Optional) Filter by WFH status (true/false).
        - is_holiday: (Optional) Filter by holiday status (true/false).
        - inout_deduction: (Optional) Filter by in/out deduction (true/false).
        """

        IN_OUT_API_URL = "https://erp-staging.projectlabs.in/v1/timesheet/in/out"

        headers = {
            "Authorization": auth_token,
            "Content-Type": "application/json"
        }

        params = {
            "month": month,
            "year": year,
            "userId": user_id
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    IN_OUT_API_URL,
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
                employee_data = response_json.get("data", {}).get("data", [])

                if not employee_data:
                    return "No in/out records found."

                formatted_records = []

                for emp in employee_data:

                    # Employee level filtering
                    if employee_name and employee_name.lower() not in (emp.get("name") or "").lower():
                        continue

                    if employee_id and employee_id.lower() not in (emp.get("employeeId") or "").lower():
                        continue

                    if team_name and team_name.lower() not in (emp.get("teamNames") or "").lower():
                        continue

                    stats = emp.get("stats", [])

                    for stat in stats:

                        # Stats level filtering
                        if is_wfh and str(stat.get("isWfh")).lower() != is_wfh.lower():
                            continue

                        if is_holiday and str(stat.get("isHoliday")).lower() != is_holiday.lower():
                            continue

                        if inout_deduction and str(stat.get("inOutDeduction")).lower() != inout_deduction.lower():
                            continue

                        formatted_records.append(
                            f"Employee Name: {emp.get('employeeFullName')}\n"
                            f"Employee ID: {emp.get('employeeId')}\n"
                            f"Official Email: {emp.get('officialEmail')}\n"
                            f"Role: {emp.get('role')}\n"
                            f"Designation: {(emp.get('designation') or {}).get('name')}\n"
                            f"Team Names: {emp.get('teamNames')}\n"
                            f"Min In Time: {emp.get('minInTime')}\n"
                            f"Max In Time: {emp.get('maxInTime')}\n"
                            f"Working Days: {emp.get('workingDays')}\n"
                            f"Date: {stat.get('date')}\n"
                            f"Is WFH: {stat.get('isWfh')}\n"
                            f"Is Holiday: {stat.get('isHoliday')}\n"
                            f"Leaves Deducted: {stat.get('leavesDeducted')}\n"
                            f"In/Out Deduction: {stat.get('inOutDeduction')}\n"
                            f"TimeSheet Time: {stat.get('timeSheetTime')}\n"
                        )

                if not formatted_records:
                    return "No in/out records found."

                return "\n\n".join(formatted_records)

            except httpx.RequestError as e:
                return f"An error occurred while requesting the API: {str(e)}"