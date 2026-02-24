# import httpx
# from datetime import datetime

# def register_late_arrival_requests(mcp):

#     @mcp.tool()
#     async def late_arrival_requests(auth_token, request_data, employee_name=""):
#         """  
#         This tool retrieves late arrival / attendance request records.

# Use this tool when the user asks about:
# - Late coming requests
# - Attendance correction requests
# - Arrival time records
# - Late entry approvals
# - Attendance request status

# The tool returns formatted attendance request data containing:

# - Employee Name
# - Employee ID
# - Designation
# - Team
# - Date
# - Arrival Time
# - Status
# - Comments
# - Send To
# - Mail To
# - Request Counts (Pending / Approved / Rejected)
# - Created At
#         """

#         ATTENDANCE_API_URL = "https://api.portal.chicmicstudios.in/v1/late/arrival/list"

#         headers = {
#             "Authorization": auth_token,
#             "Content-Type": "application/json"
#         }

#         async with httpx.AsyncClient() as client:
#             try:
#                 response = await client.post(
#                     ATTENDANCE_API_URL,
#                     headers=headers,
#                     json={
#                         "index": request_data["index"],
#                         "limit": request_data["limit"]
#                     }
#                 )

#                 if response.status_code == 401:
#                     return "Unauthorized access. Please login again."

#                 if response.status_code == 403:
#                     return "You are not authorized to access this information."

#                 if response.status_code != 200:
#                     return f"Error: Received {response.status_code} from API."

#                 attendance_requests = response.json().get("data", {}).get("data", [])

#                 if not attendance_requests:
#                     return "No attendance requests found."

#                 STATUS_MAP = {
#                     1: "Pending",
#                     2: "Approved",
#                     3: "Rejected"
#                 }

#                 formatted_requests = []

#                 for req in attendance_requests:

#                     user_data = req.get("userData", {})
#                     mail_to_list = req.get("mailTo", [])
#                     send_to_list = req.get("sendTo", [])
#                     request_counts = req.get("requestsCount", {})

#                     send_to = ", ".join(
#                         [u.get("employeeFullName", "") for u in send_to_list]
#                     )

#                     mail_to = ", ".join(
#                         [u.get("employeeFullName", "") for u in mail_to_list]
#                     )

#                     formatted_requests.append(
#                         f"Employee Name: {req.get('employeeFullName')}\n"
#                         f"Employee ID: {user_data.get('employeeId')}\n"
#                         f"Designation: {user_data.get('designation', {}).get('name')}\n"
#                         f"Team: {req.get('team')}\n"
#                         f"Date: {req.get('date')}\n"
#                         f"Arrival Time: {req.get('arrivalTime')}\n"
#                         f"Status: {STATUS_MAP.get(req.get('status'), 'Unknown')}\n"
#                         f"Comments: {req.get('comments')}\n"
#                         f"Send To: {send_to}\n"
#                         f"Mail To: {mail_to}\n"
#                         f"Request Count - Pending: {request_counts.get('pendingCount', 0)}, "
#                         f"Approved: {request_counts.get('approvedCount', 0)}, "
#                         f"Rejected: {request_counts.get('disApprovedCount', 0)}\n"
#                         f"Created At: {req.get('createdAt')}\n"
#                     )

#                 return "\n\n".join(formatted_requests)

#             except httpx.RequestError as e:
#                 return f"An error occurred while requesting the API: {str(e)}"


import httpx

def register_late_arrival_requests(mcp):

    @mcp.tool()
    async def late_arrival_requests(auth_token, request_data, employee_name="", status=""):
        """
        This tool retrieves late arrival / attendance request records.

Use this tool when the user asks about:
- Late coming requests
- Attendance correction requests
- Arrival time records
- Late entry approvals
- Status of late requests

Filters:
- employee_name (optional)
- status: pending / approved / rejected
        """

        ATTENDANCE_API_URL = "https://api.portal.chicmicstudios.in/v1/late/arrival/list"

        headers = {
            "Authorization": auth_token,
            "Content-Type": "application/json"
        }

        index = 0
        limit = 10
        all_requests = []

        async with httpx.AsyncClient() as client:
            try:
                # 🔁 Pagination Loop
                while True:
                    response = await client.post(
                        ATTENDANCE_API_URL,
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

                    all_requests.extend(batch)
                    index += limit

                if not all_requests:
                    return "No late arrival requests found."

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

                formatted_requests = []

                for req in all_requests:

                    # 👤 Filter by employee name
                    if employee_name:
                        if employee_name.lower() not in (req.get("employeeFullName") or "").lower():
                            continue

                    # 📌 Filter by status
                    if status:
                        if status not in valid_status_map:
                            continue
                        if req.get("status") != valid_status_map[status]:
                            continue

                    user_data = req.get("userData", {})
                    request_counts = req.get("requestsCount", {})

                    send_to = ", ".join(
                        [u.get("employeeFullName", "") for u in req.get("sendTo", [])]
                    )

                    mail_to = ", ".join(
                        [u.get("employeeFullName", "") for u in req.get("mailTo", [])]
                    )

                    formatted_requests.append(
                        f"Employee Name: {req.get('employeeFullName')}\n"
                        f"Designation: {user_data.get('designation', {}).get('name')}\n"
                        f"Team: {req.get('team')}\n"
                        f"Date: {req.get('date')}\n"
                        f"Arrival Time: {req.get('arrivalTime')}\n"
                        f"Comments/reason: {req.get('comments')}\n"
                        f"Status: {STATUS_MAP.get(req.get('status'), 'Unknown')}\n"
                        f"Send To: {send_to}\n"
                        f"Mail To: {mail_to}\n"
                        f"Pending Count: {request_counts.get('pendingCount', 0)}, "
                        f"Approved Count: {request_counts.get('approvedCount', 0)}, "
                        f"Rejected Count: {request_counts.get('disApprovedCount', 0)}\n"
                        f"Created At: {req.get('createdAt')}\n"
                    )

                if not formatted_requests:
                    return "No matching late arrival requests found."

                return "\n\n".join(formatted_requests)

            except httpx.RequestError as e:
                return f"An error occurred while requesting the API: {str(e)}"