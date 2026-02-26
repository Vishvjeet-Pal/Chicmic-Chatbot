from datetime import datetime
import httpx
from dateutil import parser
from typing import Optional

def register_wfh_list(mcp):

    @mcp.tool()
    async def get_wfh_list(
        auth_token,
        employee_name: str = "",
        status: Optional[int] = None,
        from_date: str = "",
        to_date: str = "",
        limit: int = 10
    ):
        """
        This tool retrieves Work From Home (WFH) records.

        Use this tool when user asks about:
        - WFH list
        - Work from home records
        - Employee WFH details
        - WFH by employee name
        - WFH by team
        - WFH by date
        - WFH by status (approved/pending/rejected)

        Filters:
        - employee_name: Filter by employee full name
        - status: Filter by status (1=Approved, 0=Pending, 2=Rejected)
        - from_date: Filter WFH starting from this date (any format)
        - to_date: Filter WFH ending till this date (any format)
        - limit: Records per API call (default 10)

        Pagination:
        - Automatically fetches all pages using while loop
        - Index increases dynamically
        """

        WFH_API_URL = "https://erp-staging.projectlabs.in/v1/WFH/list"

        headers = {
            "Authorization": auth_token,
            "Content-Type": "application/json"
        }

        index = 0
        all_records = []

        # 🔁 Dynamic Pagination Loop
        while True:

            body = {
                "index": index,
                "limit": limit
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(WFH_API_URL, headers=headers, json=body)

            if response.status_code != 200:
                return f"Error: {response.status_code} while fetching WFH records."

            data = response.json().get("data", {})
            records = data.get("data", [])

            if not records:
                break

            all_records.extend(records)

            if len(records) < limit:
                break

            index += limit  # 📌 Increase index dynamically

        if not all_records:
            return "No WFH records found."

        # 📅 Date Parsing Helper
        def parse_user_date(date_str):
            try:
                return parser.parse(date_str)
            except:
                return None

        user_from_date = parse_user_date(from_date) if from_date else None
        user_to_date = parse_user_date(to_date) if to_date else None

        formatted_output = []

        for record in all_records:

            employee_full_name = record.get("employeeFullName", "")
            team_name = record.get("team", "")
            record_status = record.get("status")
            record_tracker = record.get("trackerType")
            reason = record.get("reason", "")

            record_from_date = parser.parse(record.get("fromDate"))
            record_to_date = parser.parse(record.get("toDate"))

            # 🔎 Apply Filters

            if employee_name and employee_name.lower() not in employee_full_name.lower():
                continue
            if status is not None and record_status != status:
                continue

            if user_from_date and record_from_date < user_from_date:
                continue

            if user_to_date and record_to_date > user_to_date:
                continue

            # 📅 Format Dates
            formatted_from = record_from_date.strftime("%d-%m-%Y")
            formatted_to = record_to_date.strftime("%d-%m-%Y")

            status_map = {
                0: "Pending",
                1: "Approved",
                2: "Rejected"
            }

            tracker_map = {
                1: "Self",
                2: "Manager"
            }

            formatted_output.append(
                f"Employee: {employee_full_name}\n"
                f"Team: {team_name}\n"
                f"From: {formatted_from} or {record_from_date.strftime('%d-%B-%Y')} or {record_from_date.strftime('%d-%b-%Y')}\n"
                f"To: {formatted_to}\n"
                f"Total Days: {record.get('totalDays')}\n"
                f"Reason: {reason}\n"
                f"Status: {status_map.get(record_status, 'Unknown')}\n"
                f"Tracker Type: {tracker_map.get(record_tracker, 'Unknown')}\n"
                f"----------------------------------------"
            )

        if not formatted_output:
            return "No matching WFH records found."

        return "\n\n".join(formatted_output)