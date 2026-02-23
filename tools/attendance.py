import httpx
from datetime import datetime, timezone, timedelta
from utils.format_date import normalize_date

def register_attendance(mcp):

    @mcp.tool()
    async def get_daily_attendence(
        auth_token,
        request_data,
        date="",
        status=""  # present / absent
    ):
        """
            This tool provides daily timesheet and attendance details of a user.
            Use this tool when the user asks ONLY about:

            Daily attendance
            Attendance sheet
            At what time I came to office on specified day. It DOES NOT tells the office timing of the user.
            User was absent or present on specified day/date.
            Total working hours
            Time spent in office or work zone
            Work from home status
            Holiday status
            How much of my Leaves deducted
            Timesheet status (pending or approved)
            Upwork status
            Main Gate in/out time of the user. It DOES NOT tell the office timing of the user.
            Note: This tool does not provide the office timing of the user. It only tells the timing when user came to office/workzone. Office timing may be different from main gate/office in time of user. 

            args:
            - auth_token
            - request_data
            - date
            """

        if not request_data.get("_id"):
            return "User ID not found."

        try:
            final_date = normalize_date(date or request_data.get("date"))
        except Exception:
            return "Invalid date provided. Please use format like '19 Feb' or '19-02-2026'."

        API_URL = f"https://api.portal.chicmicstudios.in/v1/timesheet/in/out?month=1&year=2026&userId={request_data['_id']}&limit=31"

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

                for attendance in attendance_data:
                    raw_date = attendance.get("date")
                    if not raw_date:
                        continue

                    formatted_date = datetime.fromisoformat(
                        raw_date.replace("Z", "+00:00")
                    ).strftime("%d-%m-%Y")

                    if attendance.get("guardInTime"):
                        present_days.append(formatted_date)
                    else:
                        absent_days.append(formatted_date)

                # 🔹 If user asked for absent list
                if status.lower() == "absent":
                    if not absent_days:
                        return "You have no absent records."
                    return "You were absent on:\n" + "\n".join(absent_days)

                # 🔹 If user asked for present list
                if status.lower() == "present":
                    if not present_days:
                        return "You have no present records."
                    return "You were present on:\n" + "\n".join(present_days)

                # 🔹 If user asked for specific date
                if date and final_date:
                    for attendance in attendance_data:
                        raw_date = attendance.get("date")
                        if not raw_date:
                            continue

                        formatted_date = datetime.fromisoformat(
                            raw_date.replace("Z", "+00:00")
                        ).strftime("%d-%m-%Y")

                        if formatted_date == final_date:
                            return (
                                f"Attendance for {formatted_date}:\n\n"
                                f"Status: {'PRESENT' if attendance.get('guardInTime') else 'ABSENT'}\n"
                                f"Work Zone In Time: "
                                f"{datetime.strptime(attendance.get('inTime'), '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc).astimezone(IST).strftime('%I:%M %p') if attendance.get('inTime') else 'Not mentioned'}\n"
                                f"Work Zone Out Time: "
                                f"{datetime.strptime(attendance.get('outTime'), '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc).astimezone(IST).strftime('%I:%M %p') if attendance.get('outTime') else 'Not mentioned'}\n"
                                f"Timesheet Status: "
                                f"{'Approved' if attendance.get('timesheetStatus') == 2 else 'Pending'}\n"
                                f"Upwork Status: "
                                f"{'Approved' if attendance.get('upworkStatus') == 2 else 'Pending'}\n"
                            )
                
                return "\n\n".join([
                        f"Attendance for {attendance.get('date')}:\n\n"
                                f"Status: {'PRESENT' if attendance.get('guardInTime') else 'ABSENT'}\n"
                                f"Work Zone In Time: "
                                f"{datetime.strptime(attendance.get('inTime'), '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc).astimezone(IST).strftime('%I:%M %p') if attendance.get('inTime') else 'Not mentioned'}\n"
                                f"Work Zone Out Time: "
                                f"{datetime.strptime(attendance.get('outTime'), '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc).astimezone(IST).strftime('%I:%M %p') if attendance.get('outTime') else 'Not mentioned'}\n"
                                f"Timesheet Status: "
                                f"{'Approved' if attendance.get('timesheetStatus') == 2 else 'Pending'}\n"
                                f"Upwork Status: "
                                f"{'Approved' if attendance.get('upworkStatus') == 2 else 'Pending'}\n"
                                for attendance in attendance_data
                    ])

                # 🔹 Default summary
                return (
                    f"Attendance Summary:\n\n"
                    f"Total Present Days: {len(present_days)}\n"
                    f"Total Absent Days: {len(absent_days)}\n"
                )

            except Exception as e:
                return f"Error while connecting to attendance API: {str(e)}"