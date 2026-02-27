import httpx

def register_in_out_others(mcp):
    @mcp.tool()
    async def attendance_others(
        auth_token,
        request_data,
        month,
        year,
        user_id="",
        employee_name="",
        team_name="",
        is_wfh="",
        is_holiday="",
        inout_deduction=""
    ):
        """
Fetches monthly in/out attendance details of employees.

Use for queries about: employee in/out time, attendance report, WFH/holiday status, in/out deductions, or monthly attendance summary.

Filters supported:
- user_id, employee_name, employee_id, team_name
- is_wfh, is_holiday, inout_deduction
- month, year (required)

Param: auth_token (required), others optional.
"""

        IN_OUT_API_URL = "https://erp-staging.projectlabs.in/v1/timesheet/in/out"

        headers = {
            "Authorization": auth_token,
            "Content-Type": "application/json"
        }

        params = {
            "month": month,
            "year": year,
            "userId": request_data['_id']
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