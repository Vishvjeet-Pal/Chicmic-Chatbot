import httpx
from datetime import datetime, timezone, timedelta

def register_attendance(mcp):
    @mcp.tool()
    async def get_daily_attendence(auth_token,request_data):
        """
    This tool provides daily timesheet and attendance details of a user.

Use this tool when the user asks about:
- Daily attendance
- In-time or out-time
- Total working hours
- Time spent in office or work zone
- Work from home status
- Holiday status
- How much of my Leaves deducted
- Timesheet status
- Upwork status
- Main Gate in/out time

    args:
    - auth_token
    - request_data
    """
        DAILY_ATTENDENCE_API_URL = f"https://api.portal.chicmicstudios.in/v1/timesheet/in/out?month=1&year=2026&userId={request_data['_id']}"

        headers = {
        "Authorization": auth_token,
        "Content-Type": "application/json"
        }

        IST = timezone(timedelta(hours=5, minutes=30))

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(DAILY_ATTENDENCE_API_URL, headers=headers)

                if response.status_code == 401:
                    return "Unauthorized access. Please login again."

                if response.status_code == 403:
                    return "You are not authorized to access this information."

                if response.status_code != 200:
                    return f"Error: Received {response.status_code} from API."

                attendance_data = response.json()["data"]["data"][0]['stats']

                return "\n\n".join([
    f"(Day: {attendance.get('day')}\n"
    f"work zone in Time: {datetime.strptime(attendance.get('inTime'), '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc).astimezone(IST).strftime('%I:%M %p') if attendance.get('inTime') else 'N/A'}\n"
    f"work zone Out Time: {datetime.strptime(attendance.get('outTime'), '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc).astimezone(IST).strftime('%I:%M %p') if attendance.get('outTime') else 'N/A'}\n"
    f"Date: {datetime.fromisoformat(attendance.get('date').replace('Z','+00:00')).strftime('%d %B %Y') if attendance.get('date') else 'N/A'}\n"
    f"Is it Work From Home: {'Yes' if attendance.get('isWfh') else 'No'}\n"
    f"Is it Holiday: {'Yes' if attendance.get('isHoliday') else 'No'}\n"
    f"Leaves Deducted: {attendance.get('leavesDeducted', 0)}\n"
    f"Main gate Out Time: {datetime.strptime(attendance.get('guardOutTime'), '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc).astimezone(IST).strftime('%I:%M %p') if attendance.get('guardOutTime') else 'N/A'}\n"
    f"main gate in Time: {datetime.strptime(attendance.get('guardInTime'), '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc).astimezone(IST).strftime('%I:%M %p') if attendance.get('guardInTime') else 'N/A'}\n"
    f"Timesheet Time: {attendance.get('timeSheetTime', 'N/A')}\n"
    f"Total Time in Office: {attendance.get('totalTimeInOffice', 'N/A')}\n"
    f"Total Time in Work Zone: {attendance.get('totalTimeInWorkZone', 'N/A')}\n"
    f"Timesheet Status: {'Approved' if attendance.get('timesheetStatus') == 2 else 'Pending'}\n"
    f"Upwork Status: {'Approved' if attendance.get('upworkStatus') == 2 else 'Pending'})\n"
    for attendance in attendance_data
])

            except Exception as e:
                return f"Error while connecting to daily attendence API: {str(e)}"