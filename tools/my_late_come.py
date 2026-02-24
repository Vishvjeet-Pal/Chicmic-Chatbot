from datetime import datetime
import httpx

def register_my_late_come_requests(mcp):

    @mcp.tool()
    async def my_late_come_requests(auth_token, request_data, status=""):
        """
        This tool retrieves Late Come requests of employees.

Use this tool when user asks about:
- Late come records
- Late arrival requests
- Late punch approval
- Late coming history

Filters:
- status: pending / approved / rejected
        """

        LATE_COME_API_URL = "https://api.portal.chicmicstudios.in/v1/late/arrival/user"

        headers = {
            "Authorization": auth_token,
            "Content-Type": "application/json"
        }

        index = 0
        limit = 10
        all_requests = []

        async with httpx.AsyncClient() as client:
            try:
                # 🔁 Pagination
                while True:
                    response = await client.post(
                        LATE_COME_API_URL,
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
                    return "No late come records found."

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

                    # 📌 Filter by status
                    if status:
                        if status not in valid_status_map:
                            continue
                        if req.get("status") != valid_status_map[status]:
                            continue

                    # 📅 Format Date (YYYY-MM-DD → DD-MM-YYYY)
                    raw_date = req.get("date")
                    formatted_date = "N/A"

                    if raw_date:
                        parsed_date = datetime.strptime(raw_date, "%Y-%m-%d")
                        formatted_date = parsed_date.strftime("%d-%m-%Y")

                    # 🕒 Format Arrival Time (24hr → 12hr)
                    arrival_time = req.get("arrivalTime")
                    formatted_time = "N/A"

                    if arrival_time:
                        parsed_time = datetime.strptime(arrival_time, "%H:%M:%S")
                        formatted_time = parsed_time.strftime("%I:%M %p")

                    # 👥 Send To Names
                    send_to_list = ", ".join(
                        [user.get("employeeFullName", "") for user in req.get("sendTo", [])]
                    )

                    formatted_requests.append(
                        f"Employee Name: {req.get('name')}\n"
                        f"Date: {formatted_date}\n"
                        f"Arrival Time: {formatted_time}\n"
                        f"Reason: {req.get('reason')}\n"
                        f"Comments: {req.get('comments')}\n"
                        f"Status: {STATUS_MAP.get(req.get('status'), 'Unknown')}\n"
                        f"Approved By: {req.get('approvedBy', 'Not Approved Yet')}\n"
                        f"Sent To: {send_to_list}\n"
                        f"------------------------------------"
                    )

                if not formatted_requests:
                    return "No matching late come records found."

                return "\n\n".join(formatted_requests)

            except httpx.RequestError as e:
                return f"An error occurred while requesting the API: {str(e)}"