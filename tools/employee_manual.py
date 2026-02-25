# import httpx
# from datetime import datetime


# def register_manual_hours_request_tool(mcp):

#     @mcp.tool()
#     async def manual_hours_requests(
#         auth_token,
#         employee_name="",
#         status="",
#         month=""
#     ):
#         """
#         Use this tool when user asks about:
#         - Manual hour requests
#         - Pending/Approved/Rejected requests
#         - Requests of specific employee
#         - Requests of specific month

#         Args:
#         - auth_token (required)
#         - employee_name (optional)
#         - status (optional): pending / approved / rejected
#         - month (optional): January / Jan
#         """

#         MANUAL_HOUR_API_URL = "https://erp-staging.projectlabs.in/v1/hubstaff/manual/requests"

#         headers = {
#             "Authorization": auth_token,
#             "Content-Type": "application/json"
#         }

#         index = 0
#         limit = 20
#         all_requests = []

#         # Status Mapping
#         STATUS_MAP = {
#             1: "Pending",
#             2: "Approved",
#             3: "Rejected"
#         }

#         VALID_STATUS = {
#             "pending": 1,
#             "approved": 2,
#             "rejected": 3
#         }

#         # Safe input cleaning
#         employee_name = (employee_name or "").strip().lower()
#         status = (status or "").strip().lower()
#         month = (month or "").strip()

#         # Month Handling
#         month_number = None
#         if month:
#             try:
#                 try:
#                     month_number = datetime.strptime(month, "%B").month
#                 except ValueError:
#                     month_number = datetime.strptime(month, "%b").month
#             except ValueError:
#                 return "Please provide month like 'February' or 'Feb'."

#         async with httpx.AsyncClient(timeout=30.0) as client:
#             try:
#                 # Pagination Loop
#                 while True:
#                     response = await client.post(
#                         MANUAL_HOUR_API_URL,
#                         headers=headers,
#                         json={
#                             "index": index,
#                             "limit": limit
#                         }
#                     )

#                     if response.status_code == 401:
#                         return "Unauthorized access. Please login again."

#                     if response.status_code == 403:
#                         return "You are not authorized to access this information."

#                     if response.status_code != 200:
#                         return f"Error: Received {response.status_code} from API."

#                     data = response.json()
#                     batch = data.get("data", {}).get("data", [])

#                     if not batch:
#                         break

#                     all_requests.extend(batch)
#                     index += limit

#                 if not all_requests:
#                     return "No manual hour requests found."

#                 formatted_records = []

#                 for req in all_requests:

#                     # Safe Employee Name Extraction
#                     employee_name_from_api = (
#                         req.get("employeeFullName")
#                         or req.get("user", {}).get("employeeFullName")
#                         or ""
#                     )

#                     # Employee Filter
#                     if employee_name:
#                         if employee_name not in employee_name_from_api.lower():
#                             continue

#                     # Status Filter
#                     if status:
#                         if status not in VALID_STATUS:
#                             return "Invalid status. Use: pending, approved, rejected."
#                         if req.get("PMstatus") != VALID_STATUS[status]:
#                             continue

#                     # Date Handling
#                     entry_date_raw = req.get("date")
#                     if not entry_date_raw:
#                         continue

#                     try:
#                         entry_date = datetime.strptime(entry_date_raw[:10], "%Y-%m-%d")
#                     except ValueError:
#                         continue

#                     # Month Filter
#                     if month_number:
#                         if entry_date.month != month_number:
#                             continue

#                     formatted_records.append(
#                         f"Employee Name: {employee_name_from_api}\n"
#                         f"Date: {entry_date.strftime('%d-%m-%Y')}\n"
#                         f"Duration: {req.get('duration', 'N/A')}\n"
#                         f"From: {req.get('fromTime', 'N/A')}  To: {req.get('endTime', 'N/A')}\n"
#                         f"Comment: {req.get('comment', 'N/A')}\n"
#                         f"Project: {req.get('projectName', 'N/A')}\n"
#                         f"Team: {req.get('team', 'N/A')}\n"
#                         f"Status: {STATUS_MAP.get(req.get('PMstatus'), 'Unknown')}\n"
#                         f"{'-'*40}"
#                     )

#                 if not formatted_records:
#                     return "No matching manual hour requests found."

#                 return "\n\n".join(formatted_records)

#             except httpx.RequestError as e:
#                 return f"An error occurred while requesting the API: {str(e)}"

import httpx
from datetime import datetime


def register_manual_hours_request_tool(mcp):

    @mcp.tool()
    async def manual_hours_requests(
        auth_token,
        employee_name="",
        status="",
        month="",
        date=""
    ):
        """
        Use this tool when user asks about:
        - Manual hour requests
        - Pending/Approved/Rejected requests
        - Requests of specific employee
        - Requests of specific month
        - Requests of specific date (19 Feb, 19-02-2023, 2023-02-19, etc.)

        Args:
        - auth_token (required)
        - employee_name (optional)
        - status (optional): pending / approved / rejected
        - month (optional): January / Jan
        - date (optional): 19 / 19 Feb / 19-02-2023 / 2023-02-19
        """

        MANUAL_HOUR_API_URL = "https://erp-staging.projectlabs.in/v1/hubstaff/manual/requests"

        headers = {
            "Authorization": auth_token,
            "Content-Type": "application/json"
        }

        index = 0
        limit = 20
        all_requests = []

        STATUS_MAP = {
            1: "Pending",
            2: "Approved",
            3: "Rejected"
        }

        VALID_STATUS = {
            "pending": 1,
            "approved": 2,
            "rejected": 3
        }

        # Clean inputs safely
        employee_name = (employee_name or "").strip().lower()
        status = (status or "").strip().lower()
        month = (month or "").strip()
        date = (date or "").strip()

        # -------------------------
        # Month Parsing
        # -------------------------
        month_number = None
        if month:
            try:
                try:
                    month_number = datetime.strptime(month, "%B").month
                except ValueError:
                    month_number = datetime.strptime(month, "%b").month
            except ValueError:
                return "Invalid month. Use format like 'February' or 'Feb'."

        # -------------------------
        # Date Parsing
        # -------------------------
        filter_day = None
        filter_month = None
        filter_year = None

        if date:
            try:
                # Full ISO date: 2023-02-19
                if "-" in date and len(date.split("-")[0]) == 4:
                    parsed = datetime.strptime(date, "%Y-%m-%d")
                    filter_day = parsed.day
                    filter_month = parsed.month
                    filter_year = parsed.year

                # DD-MM-YYYY
                elif "-" in date:
                    parsed = datetime.strptime(date, "%d-%m-%Y")
                    filter_day = parsed.day
                    filter_month = parsed.month
                    filter_year = parsed.year

                # 19 Feb or 19 February
                elif " " in date:
                    try:
                        parsed = datetime.strptime(date, "%d %B")
                    except ValueError:
                        parsed = datetime.strptime(date, "%d %b")
                    filter_day = parsed.day
                    filter_month = parsed.month

                # Only day (19)
                else:
                    filter_day = int(date)

            except Exception:
                return "Invalid date format. Use 19, 19 Feb, 19-02-2023 or 2023-02-19."

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                while True:
                    response = await client.post(
                        MANUAL_HOUR_API_URL,
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
                    return "No manual hour requests found."

                formatted_records = []

                for req in all_requests:

                    employee_name_from_api = (
                        req.get("employeeFullName")
                        or req.get("user", {}).get("employeeFullName")
                        or ""
                    )

                    # Employee filter
                    if employee_name:
                        if employee_name not in employee_name_from_api.lower():
                            continue

                    # Status filter
                    if status:
                        if status not in VALID_STATUS:
                            return "Invalid status. Use pending, approved, rejected."
                        if req.get("PMstatus") != VALID_STATUS[status]:
                            continue

                    entry_date_raw = req.get("date")
                    if not entry_date_raw:
                        continue

                    try:
                        entry_date = datetime.strptime(entry_date_raw[:10], "%Y-%m-%d")
                    except ValueError:
                        continue

                    # Month filter
                    if month_number and entry_date.month != month_number:
                        continue

                    # Advanced date filter
                    if filter_day and entry_date.day != filter_day:
                        continue
                    if filter_month and entry_date.month != filter_month:
                        continue
                    if filter_year and entry_date.year != filter_year:
                        continue

                    formatted_records.append(
                        f"Employee Name: {employee_name_from_api}\n"
                        f"Date: {entry_date.strftime('%d-%m-%Y')}\n"
                        f"Duration: {req.get('duration', 'N/A')}\n"
                        f"From: {req.get('fromTime', 'N/A')}  To: {req.get('endTime', 'N/A')}\n"
                        f"Comment: {req.get('comment', 'N/A')}\n"
                        f"Project: {req.get('projectName', 'N/A')}\n"
                        f"Team: {req.get('team', 'N/A')}\n"
                        f"Status: {STATUS_MAP.get(req.get('PMstatus'), 'Unknown')}\n"
                        f"{'-'*40}"
                    )

                if not formatted_records:
                    return "No matching manual hour requests found."

                return "\n\n".join(formatted_records)

            except httpx.RequestError as e:
                return f"API request error: {str(e)}"