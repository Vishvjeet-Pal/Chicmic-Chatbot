from datetime import datetime
import httpx

def register_manual_hour_requests(mcp):

    @mcp.tool()
    async def manual_hour_requests(auth_token, request_data, status=""):
        """
        This tool retrieves Hubstaff manual hour entry requests.

Use this tool when user asks about:
- Manual hour requests
- Hubstaff manual entries
- Manual time entries
- Missing biometric entries
- Manual duration approvals

 args:
        - auth_token: The authentication token for API access. Provided in the Authorization header of the request.
        - request_data: The request data containing necessary parameters for the API call. Provided in the body of the request.
        - status: [pending, approved, cancelled, rejected/dissapproved]. If no value is mentioned, return all leave application record.

Filters:
- status: pending / approved / rejected
        """

        MANUAL_HOUR_API_URL = "https://api.portal.chicmicstudios.in/v1/hubstaff/manual/list"

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
                        if req.get("PMstatus") != valid_status_map[status]:
                            continue
                    raw_date = req.get("date")
                    formatted_date = "N/A"
                    if raw_date:
                        formatted_date = datetime.fromisoformat(
                            raw_date.replace("Z", "+00:00")
                        ).strftime("%d-%m-%Y")

                    pm_list = ", ".join(
                        [pm.get("employeeFullName", "") for pm in req.get("PMList", [])]
                    )

                    formatted_requests.append(
                        f"Employee Name: {req.get('user', {}).get('employeeFullName')}\n"
                        f"Date: {formatted_date} or {datetime.fromisoformat(raw_date.replace('Z', '+00:00')).strftime('%d-%B-%Y')} or {'today' if datetime.today().strftime('%d-%m-%Y') == formatted_date else datetime.fromisoformat(raw_date.replace('Z', '+00:00')).strftime('%d-%b')}\n"
                        f"Duration: {req.get('duration')}\n"
                        f"From Time: {req.get('fromTime')}\n"
                        f"End Time: {req.get('endTime')}\n"
                        f"Comment: {req.get('comment')}\n"
                        f"Status: {STATUS_MAP.get(req.get('PMstatus'), 'Unknown')}\n"
                        f"Approved By: {req.get('approvedBy')}\n"
                        f"Project Managers: {pm_list}\n"
                    )

                if not formatted_requests:
                    return "No matching manual hour requests found."

                return "\n\n".join(formatted_requests)

            except httpx.RequestError as e:
                return f"An error occurred while requesting the API: {str(e)}"