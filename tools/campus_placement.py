import httpx
from datetime import datetime

def register_campus_placement_list(mcp):

    @mcp.tool()
    async def get_campus_placement_list(
        auth_token,
        index: int = 0,
        limit: int = 10,
        employee_name: str = "",
        team: str = "",
        status: int | None = None ,        # 1 = Active, 2 = Completed (example)
        from_date: str = "",         # any format
        to_date: str = ""            # any format
    ):
        """
        Retrieves Campus Placement list.

        Use this tool when user asks about:
        - Campus placements
        - Placement drives
        - Campus event list
        - Who attended placement
        - Placement by employee
        - Placement by team
        - Placement by date range

        Pagination:
        - index → Page index (default 0)
        - limit → Records per page (default 10)

        Filters:
        - employee_name
        - team
        - status (1 or 2)
        - from_date
        - to_date

        Dates can be in any readable format (e.g., 10 May 2023, 2023-05-10, May 10).
        """

        url = "https://erp-staging.projectlabs.in/v1/campus/placement/list"

        payload = {
            "index": int(index),
            "limit": int(limit)
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
        placements = response_json.get("data", {}).get("data", [])
        total_count = response_json.get("data", {}).get("count", 0)

        if not placements:
            return "No campus placements found."

        # Date parsing helper
        def parse_date(date_str):
            try:
                return datetime.fromisoformat(date_str.replace("Z", ""))
            except:
                return None

        from_date_obj = None
        to_date_obj = None

        try:
            if from_date:
                from_date_obj = datetime.strptime(from_date, "%Y-%m-%d")
        except:
            pass

        try:
            if to_date:
                to_date_obj = datetime.strptime(to_date, "%Y-%m-%d")
        except:
            pass

        filtered_results = []

        for item in placements:

            emp_name = item.get("employeeFullName") or ""
            team_names = item.get("teams") or ""
            item_status = item.get("status")
            created_at_raw = item.get("createdAt", "")

            created_at_obj = parse_date(created_at_raw)

            # 🔎 Filtering

            if employee_name and employee_name.lower() not in emp_name.lower():
                continue

            if team and team.lower() not in team_names.lower():
                continue

            if status is not None and item_status != status:
                continue

            if from_date_obj and created_at_obj:
                if created_at_obj.date() < from_date_obj.date():
                    continue

            if to_date_obj and created_at_obj:
                if created_at_obj.date() > to_date_obj.date():
                    continue

            filtered_results.append(item)

        if not filtered_results:
            return "No placements matched the given filters."

        formatted_output = []

        for idx, item in enumerate(filtered_results, start=1):

            location = item.get("location", "N/A")
            status_value = item.get("status", 0)
            status_text = "Active" if status_value == 1 else "Completed"

            from_date = item.get("fromDate", "")
            to_date = item.get("toDate", "")
            created_at = item.get("createdAt", "")

            try:
                from_date = datetime.fromisoformat(from_date.replace("Z", "")).strftime("%d-%b-%Y")
            except:
                pass

            try:
                to_date = datetime.fromisoformat(to_date.replace("Z", "")).strftime("%d-%b-%Y")
            except:
                pass

            try:
                created_at = datetime.fromisoformat(created_at.replace("Z", "")).strftime("%d-%b-%Y %H:%M")
            except:
                pass

            formatted_output.append(
                f"{idx}. {item.get('employeeFullName', 'N/A')}\n"
                f"   Location: {location}\n"
                f"   Teams: {item.get('teams', 'N/A')}\n"
                f"   Status: {status_text}\n"
                f"   From: {from_date}\n"
                f"   To: {to_date}\n"
                f"   Created At: {created_at}\n"
                f"--------------------------------------"
            )

        return (
            f"Total Records (API): {total_count}\n"
            f"Filtered Records: {len(filtered_results)}\n\n"
            + "\n\n".join(formatted_output)
        )