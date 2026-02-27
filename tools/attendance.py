import httpx
from datetime import datetime, timezone, timedelta
from utils.format_date import normalize_date

def register_attendance(mcp):

    @mcp.tool()
    async def get_daily_attendence(
        auth_token,
        request_data,
        date="",
        status="",
        month=""
    ):
        """
Returns user daily attendance details.

Use only for: present/absent status, entry/exit time, main gate time, leaves deducted, timesheet or upwork status.

Rules:
- No official office timing.
- If date provided → return that date only.
- If status provided → filter by present/absent.
- If month provided → use that month.
- If no date → return current month.
- If asking for today and no record → "Details not mentioned."

Params: auth_token, request_data (_id required), date, status, month.
"""

        if not request_data.get("_id"):
            return "User ID not found."

        try:
            final_date = normalize_date(date or request_data.get("date"))
        except Exception:
            return "Invalid date provided. Please use format like '19 Feb' or '19-02-2026'."
        
        MONTH_MAP = {
    "january": '0', "jan": '0',
    "february": '1', "feb": '1',
    "march": '2', "mar": '2',
    "april": '3', "apr": '3',
    "may": '4',
    "june": '5', "jun": '5',
    "july": '6', "jul": '6',
    "august": '7', "aug": '7',
    "september": '8', "sep": '8', "sept": '8',
    "october": '9', "oct": '9',
    "november": '10', "nov": '10',
    "december": '11', "dec": '11',
}

        API_URL = f"https://api.portal.chicmicstudios.in/v1/timesheet/in/out?month={MONTH_MAP.get(month.lower(),MONTH_MAP[str(datetime.today().strftime('%b')).lower()])}&year=2026&userId={request_data['_id']}&limit=31"

        headers = {
            "Authorization": auth_token,
            "Content-Type": "application/json"
        }

        IST = timezone(timedelta(hours=5, minutes=30))

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(API_URL, headers=headers)

                if response.status_code == 401:
                    return "Unauthorized access. Please login again."

                if response.status_code == 403:
                    return "You are not authorized to access this information."

                if response.status_code != 200:
                    return f"Error: Received {response.status_code} from API."

                attendance_data = response.json()["data"]["data"][0]["stats"]

                present_days = []
                absent_days = []
                result = ""
                for attendance in attendance_data:
                    raw_date = attendance.get("date")
                    if not raw_date:
                        continue

                    formatted_date = datetime.fromisoformat(
                        raw_date.replace("Z", "+00:00")
                    ).strftime("%d-%m-%Y")

                    if attendance.get("guardInTime"):
                        present_days.append(f"{formatted_date} or {datetime.fromisoformat(raw_date.replace('Z', '+00:00')).strftime('%d-%B-%Y')} or {'today' if datetime.today().strftime('%d-%m-%Y') == formatted_date else datetime.fromisoformat(raw_date.replace('Z', '+00:00')).strftime('%d-%b')}")
                    else:
                        absent_days.append(f"{formatted_date} or {datetime.fromisoformat(raw_date.replace('Z', '+00:00')).strftime('%d-%B-%Y')} or {'today' if datetime.today().strftime('%d-%m-%Y') == formatted_date else datetime.fromisoformat(raw_date.replace('Z', '+00:00')).strftime('%d-%b')}")
                if status.lower() == "absent":
                    if not absent_days:
                        return "You have no absent records.\n"
                    else:
                        return "You were absent on:\n" + "\n".join(absent_days) + "\n"

                if status.lower() == "present":
                    if not present_days:
                        return "You have no present records.\n"
                    else:
                        return "You were present on:\n" + "\n".join(present_days) + "\n"

                # 🔹 If user asked for specific date
                if (date and final_date) or (not date and not month):
                    for attendance in attendance_data:
                        raw_date = attendance.get("date")
                        if not raw_date:
                            continue

                        formatted_date = datetime.fromisoformat(
                            raw_date.replace("Z", "+00:00")
                        ).strftime("%d-%m-%Y")

                        if formatted_date == final_date:
                            return (
                                f"Attendance for {formatted_date} or {datetime.fromisoformat(raw_date.replace('Z', '+00:00')).strftime('%d-%B-%Y')} or {'today' if datetime.today().strftime('%d-%m-%Y') == formatted_date else datetime.fromisoformat(raw_date.replace('Z', '+00:00')).strftime('%d-%b')}:\n\n"
                                f"Status: {'PRESENT' if attendance.get('guardInTime') else 'ABSENT'}\n"
                                f"Work Zone In Time: "
                                f"{datetime.strptime(attendance.get('inTime'), '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc).astimezone(IST).strftime('%I:%M %p') if attendance.get('inTime') else 'Not mentioned'}\n"
                                f"Work Zone Out Time: "
                                f"{datetime.strptime(attendance.get('outTime'), '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc).astimezone(IST).strftime('%I:%M %p') if attendance.get('outTime') else 'Not mentioned'}\n"
                                f"Main Gate In Time or entry in office: "
                                f"{datetime.strptime(attendance.get('guardInTime'), '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc).astimezone(IST).strftime('%I:%M %p') if attendance.get('guardInTime') else 'Not mentioned'}\n"
                                f"Main Gate Out Time or exit from office: "
                                f"{datetime.strptime(attendance.get('guardOutTime'), '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc).astimezone(IST).strftime('%I:%M %p') if attendance.get('guardOutTime') else 'Not mentioned'}\n"
                                f"Leaves Deducted: {attendance.get('leavesDeducted', 0)}\n"
                                f"Timesheet Status: "
                                f"{'Approved' if attendance.get('timesheetStatus') == 2 else 'Pending'}\n"
                                f"Upwork Status: "
                                f"{'Approved' if attendance.get('upworkStatus') == 2 else 'Pending'}\n"
                            )
                
                leave_deducted=sum([attendance.get('leavesDeducted', 0) for attendance in attendance_data])
                result+=f"Total Leaves Deducted : {leave_deducted}\n"
                return result+"\n\n".join([
                        f"Attendance for {datetime.fromisoformat(attendance.get('date').replace('Z', '+00:00')).strftime('%d-%m-%Y')} or {datetime.fromisoformat(attendance.get('date').replace('Z', '+00:00')).strftime('%d-%B-%Y')} or {'today' if datetime.today().strftime('%d-%m-%Y') == datetime.fromisoformat(attendance.get('date').replace('Z', '+00:00')).strftime('%d-%m-%Y') else datetime.fromisoformat(attendance.get('date').replace('Z', '+00:00')).strftime('%d-%b')}:\n\n"
                                f"Status: {'PRESENT' if attendance.get('guardInTime') else 'ABSENT'}\n"
                                f"Work Zone In Time: "
                                f"{datetime.strptime(attendance.get('inTime'), '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc).astimezone(IST).strftime('%I:%M %p') if attendance.get('inTime') else 'Not mentioned'}\n"
                                f"Work Zone Out Time: "
                                f"{datetime.strptime(attendance.get('outTime'), '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc).astimezone(IST).strftime('%I:%M %p') if attendance.get('outTime') else 'Not mentioned'}\n"
                                f"Main Gate In Time or entry in office: "
                                f"{datetime.strptime(attendance.get('guardInTime'), '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc).astimezone(IST).strftime('%I:%M %p') if attendance.get('guardInTime') else 'Not mentioned'}\n"
                                f"Main Gate Out Time or exit from office: "
                                f"{datetime.strptime(attendance.get('guardOutTime'), '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc).astimezone(IST).strftime('%I:%M %p') if attendance.get('guardOutTime') else 'Not mentioned'}\n"
                                f"Leaves Deducted: {attendance.get('leavesDeducted', 0)}\n"
                                f"Timesheet Status: "
                                f"{'Approved' if attendance.get('timesheetStatus') == 2 else 'Pending'}\n"
                                f"Upwork Status: "
                                f"{'Approved' if attendance.get('upworkStatus') == 2 else 'Pending'}\n"
                                for attendance in attendance_data
                    ])

            except Exception as e:
                return f"Error while connecting to attendance API: {str(e)}"