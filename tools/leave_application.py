import httpx

def register_leave_application(mcp):
    @mcp.tool()
    async def leave_application(auth_token, request_data):
        """  
        This tool retrieves leave application records from the ERP system.

Use this tool when the user asks about:
- Leave details of other employees
- Leave history of other employees
- leave applications of other employees
- Employee leave records
- Leave status of other employees
- Leave for a specific year of other employees
- Leave between specific dates of other employees

The tool returns formatted leave application data containing:

- Employee Name
- Team
- Reporting To
- Leave Type
- Reason
- From Date
- To Date
- Total Days
- Actual Days
- Half Days
- Waiver Applied
- Waiver Dates
- Sandwich Applied
- Status
- Send To
- Mail To
- Year

        args:
        - auth_token: The authentication token for API access.
        - request_data: The request data containing necessary parameters for the API call.
        """

        LEAVE_APPLICATION_API_URL = f"https://erp-staging.projectlabs.in/v1/leave/requests"

        headers = {
                "Authorization": auth_token,
                "Content-Type": "application/json"
            }
            
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(LEAVE_APPLICATION_API_URL, headers=headers, json=request_data)

                if response.status_code == 401:
                    return "Unauthorized access. Please login again."

                if response.status_code == 403:
                    return "You are not authorized to access this information."

                if response.status_code != 200:
                    return f"Error: Received {response.status_code} from API."

                leave_applications = response.json().get("data", {}).get("data", [])


                if not leave_applications:
                    return "No leave applications found."

                STATUS_MAP = {
                    1: "Pending",
                    2: "Approved",
                    3: "Rejected",
                    4: "Cancelled"
                }

                formatted_leaves = []

                for leave in leave_applications:
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

                return "\n\n".join(formatted_leaves)

            except httpx.RequestError as e:
                return f"An error occurred while requesting the API: {str(e)}"

