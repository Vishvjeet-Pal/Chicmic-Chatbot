import httpx
from datetime import datetime

def register_relaxation_sheet(mcp):

    @mcp.tool()
    async def get_relaxation_sheet(
        auth_token,
        month: str,
        year: int,
        index: int = 0,
        limit: int = 10
    ):
        """
        Retrieves Relaxation Sheet data (Monthly Timesheet Summary).

        Month can be:
        - jan / january
        - feb / february
        - etc.

        Internally mapped to 1–12
        """

        url = "https://erp-staging.projectlabs.in/v1/timesheet/relaxationSheet"

        # 🔁 Month Mapping (1–12)
        month_map = {
            "jan": 1, "january": 1,
            "feb": 2, "february": 2,
            "mar": 3, "march": 3,
            "apr": 4, "april": 4,
            "may": 5,
            "jun": 6, "june": 6,
            "jul": 7, "july": 7,
            "aug": 8, "august": 8,
            "sep": 9, "sept": 9, "september": 9,
            "oct": 10, "october": 10,
            "nov": 11, "november": 11,
            "dec": 12, "december": 12
        }

        month_key = month.strip().lower()

        if month_key not in month_map:
            return "Invalid month. Please provide month like 'jan' or 'january'."

        mapped_month = str(month_map[month_key])

        payload = {
            "index": int(index),
            "limit": int(limit),
            "month": mapped_month,
            "year": int(year)
        }

        headers = {
            "Authorization": auth_token,
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)

        if response.status_code != 200:
            return f"Error {response.status_code}: {response.text}"

        response_json = response.json()
        employees = response_json.get("data", {}).get("data", [])
        total_count = response_json.get("data", {}).get("count", 0)

        if not employees:
            return "No relaxation sheet data found for this month."

        formatted_output = []

        for idx, emp in enumerate(employees, start=1):

            total_hours_seconds = emp.get("totalHours", 0)
            total_hours = round(total_hours_seconds / 3600, 2)

            # 📅 Created Date Formatting
            created_at = emp.get("createdAt")
            formatted_created = "N/A"

            if created_at:
                try:
                    parsed_date = datetime.fromisoformat(
                        created_at.replace("Z", "+00:00")
                    )
                    formatted_created = parsed_date.strftime("%d-%B-%Y %I:%M %p")
                except:
                    formatted_created = created_at

            formatted_output.append(
                f"{idx}. {emp.get('employeeFullName', 'N/A')}\n"
                f"   Employee ID: {emp.get('employeeId', 'N/A')}\n"
                f"   Working Days: {emp.get('workDays', 0)}\n"
                f"   Total Leaves: {emp.get('totalLeaves', 0)}\n"
                f"   Holidays: {emp.get('holidayCount', 0)}\n"
                f"   Total Hours: {total_hours} hrs\n"
                f"   Created On: {formatted_created}\n"
                f"------------------------------------"
            )

        return (
            f"Month: {month.capitalize()} {year}\n"
            f"Total Records: {total_count}\n\n"
            + "\n\n".join(formatted_output)
        )