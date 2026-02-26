import httpx
from datetime import datetime

def register_campus_placement_list(mcp):

    @mcp.tool()
    async def get_campus_placement_list(
        auth_token,
        employee_name: str = "",
        team: str = "",
        status: int | None = None,
        from_date: str = "",
        to_date: str = ""
    ):
        """
        Retrieves Campus Placement list.

        Fetches ALL records dynamically.

        Filters:
        - employee_name
        - team
        - status (1 or 2)
        - from_date
        - to_date
        """

        url = "https://erp-staging.projectlabs.in/v1/campus/placement/list"

        headers = {
            "Authorization": auth_token,
            "Content-Type": "application/json"
        }

        index = 0
        limit = 10
        all_placements = []
        total_count = 0

        async with httpx.AsyncClient() as client:

            while True:

                payload = {
                    "index": index,
                    "limit": limit
                }

                response = await client.post(url, headers=headers, json=payload)

                if response.status_code == 401:
                    return "Unauthorized access. Please login again."

                if response.status_code == 403:
                    return "You are not authorized to access this information."

                if response.status_code != 200:
                    return f"Error {response.status_code}: {response.text}"

                response_json = response.json()
                data_section = response_json.get("data", {})
                placements = data_section.get("data", [])
                total_count = data_section.get("count", 0)

                if not placements:
                    break

                all_placements.extend(placements)

                # Stop when all fetched
                if len(all_placements) >= total_count:
                    break

                index += limit   # 🔥 increase dynamically

        if not all_placements:
            return "No campus placements found."

        # ---------------- DATE PARSER ----------------
        def parse_any_date(date_str):
            if not date_str:
                return None

            formats = [
                "%Y-%m-%d",
                "%d-%m-%Y",
                "%d %b %Y",
                "%d %B %Y",
                "%b %d %Y",
                "%B %d %Y"
            ]

            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except:
                    continue

            try:
                return datetime.fromisoformat(date_str.replace("Z", ""))
            except:
                return None

        from_date_obj = parse_any_date(from_date)
        to_date_obj = parse_any_date(to_date)

        # ---------------- FILTERING ----------------
        filtered_results = []

        for item in all_placements:

            emp_name = item.get("employeeFullName") or ""
            team_names = item.get("teams") or ""
            item_status = item.get("status")
            created_at_obj = parse_any_date(item.get("createdAt", ""))

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

        # ---------------- FORMAT OUTPUT ----------------
        formatted_output = []

        for idx, item in enumerate(filtered_results, start=1):

            location = item.get("location", "N/A")
            status_value = item.get("status", 0)
            status_text = "Active" if status_value == 1 else "Completed"

            from_date_val = parse_any_date(item.get("fromDate", ""))
            to_date_val = parse_any_date(item.get("toDate", ""))
            created_at_val = parse_any_date(item.get("createdAt", ""))

            formatted_output.append(
                f"{idx}. {item.get('employeeFullName', 'N/A')}\n"
                f"   Location: {location}\n"
                f"   Teams: {item.get('teams', 'N/A')}\n"
                f"   Status: {status_text}\n"
                f"   From: {from_date_val.strftime('%d-%b-%Y') if from_date_val else 'N/A'}\n"
                f"   To: {to_date_val.strftime('%d-%b-%Y') if to_date_val else 'N/A'}\n"
                f"   Created At: {created_at_val.strftime('%d-%b-%Y %H:%M') if created_at_val else 'N/A'}\n"
                f"--------------------------------------"
            )

        return (
            f"Total Records (API): {total_count}\n"
            f"Filtered Records: {len(filtered_results)}\n\n"
            + "\n\n".join(formatted_output)
        )