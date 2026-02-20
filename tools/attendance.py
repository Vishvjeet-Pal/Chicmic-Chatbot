import httpx
from datetime import datetime, timezone, timedelta
from utils.redis_cache import get_cached_or_search
import json

def format_attendance_json(attendance_data, IST):
    result = []

    for attendance in attendance_data:
        date_obj = datetime.fromisoformat(
            attendance.get('date').replace('Z', '+00:00')
        ) if attendance.get('date') else None

        formatted_date_full = date_obj.strftime('%d %B %Y') if date_obj else None
        formatted_date_dash = date_obj.strftime('%d-%m-%Y') if date_obj else None
        formatted_date_short = date_obj.strftime('%d %b') if date_obj else None

        def convert_time(value):
            if not value:
                return None
            return (
                datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')
                .replace(tzinfo=timezone.utc)
                .astimezone(IST)
                .strftime('%I:%M %p')
            )

        result.append({
            "day": attendance.get("day"),
            "date": {
                "full": formatted_date_full,
                "dash": formatted_date_dash,
                "short": formatted_date_short
            },
            "attendanceStatus": "PRESENT" if attendance.get("inTime") else "ABSENT",
            "workZoneInTime": convert_time(attendance.get("inTime")),
            "workZoneOutTime": convert_time(attendance.get("outTime")),
            "isWorkFromHome": bool(attendance.get("isWfh")),
            "isHoliday": bool(attendance.get("isHoliday")),
            "leavesDeducted": attendance.get("leavesDeducted", 0),
            "guardInTime": convert_time(attendance.get("guardInTime")),
            "guardOutTime": convert_time(attendance.get("guardOutTime")),
            "timesheetTime": attendance.get("timeSheetTime"),
            "timesheetStatus": "Approved" if attendance.get("timesheetStatus") == 2 else "Pending",
            "upworkStatus": "Approved" if attendance.get("upworkStatus") == 2 else "Pending"
        })

    return json.dumps(result, indent=2)

def register_attendance(mcp):
    @mcp.tool()
    async def get_daily_attendence(auth_token,request_data):
        """
    This tool provides daily timesheet and attendance details of a user.

Use this tool when the user asks ONLY about:
- Daily attendance
- Attendance sheet
- At what time I came to office on specified day. It DOES NOT tells the office timing of the user.
- User was absent or present on specified day/date.
- Total working hours
- Time spent in office or work zone
- Work from home status
- Holiday status
- How much of my Leaves deducted
- Timesheet status (pending or approved)
- Upwork status
- Main Gate in/out time of the user. It DOES NOT tell the office timing of the user.

Note: This tool does not provide the office timing of the user. It only tells the timing when user came to office/workzone. Office timing may be different from main gate/office in time of user. 

    args:
    - auth_token
    - request_data
    """
        cache_key=f"attendance:{request_data['_id']}"
        async def search():
            DAILY_ATTENDENCE_API_URL = f"https://api.portal.chicmicstudios.in/v1/timesheet/in/out?month=1&year=2026&userId={request_data['_id']}&limit=10"

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

                    attendance_data = response.json()["data"]["data"][0]['stats'][-10:]

                    return format_attendance_json(attendance_data,IST)

    #                 return "\n\n".join([
    #     f"(Day: {attendance.get('day')}\n"
    #     f"You were {'PRESENT' if attendance.get('inTime') else 'ABSENT'} on date {datetime.fromisoformat(attendance.get('date').replace('Z','+00:00')).strftime('%d %B %Y')} or {datetime.fromisoformat(attendance.get('date').replace('Z','+00:00')).strftime('%d-%m-%Y')} or {datetime.fromisoformat(attendance.get('date').replace('Z','+00:00')).strftime('%d %b')} \n"
    #     f"Your work zone in Time: {datetime.strptime(attendance.get('inTime'), '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc).astimezone(IST).strftime('%I:%M %p') if attendance.get('inTime') else 'N/A'}\n"
    #     f"Your work zone Out Time: {datetime.strptime(attendance.get('outTime'), '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc).astimezone(IST).strftime('%I:%M %p') if attendance.get('outTime') else 'N/A'}\n"
    #     f"This attendance is of Date: {datetime.fromisoformat(attendance.get('date').replace('Z','+00:00')).strftime('%d %B %Y')} or {datetime.fromisoformat(attendance.get('date').replace('Z','+00:00')).strftime('%d-%m-%Y')} or {datetime.fromisoformat(attendance.get('date').replace('Z','+00:00')).strftime('%d %b')}\n"
    #     f"Is it Work From Home: {'Yes' if attendance.get('isWfh') else 'No'}\n"
    #     f"Is it Holiday: {'Yes' if attendance.get('isHoliday') else 'No'}\n"
    #     f"Leaves Deducted on date {datetime.fromisoformat(attendance.get('date').replace('Z','+00:00')).strftime('%d %B %Y') if attendance.get('date') else 'N/A'}: {attendance.get('leavesDeducted', 0)} of your one day salary\n"
    #     f"You left the office or your main gate Out Time on date {datetime.fromisoformat(attendance.get('date').replace('Z','+00:00')).strftime('%d %B %Y') if attendance.get('date') else 'N/A'} is: {datetime.strptime(attendance.get('guardOutTime'), '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc).astimezone(IST).strftime('%I:%M %p') if attendance.get('guardOutTime') else 'N/A'}\n"
    #     f"You came to office or your main gate in Time on date {datetime.fromisoformat(attendance.get('date').replace('Z','+00:00')).strftime('%d %B %Y') if attendance.get('date') else 'N/A'} is: {datetime.strptime(attendance.get('guardInTime'), '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc).astimezone(IST).strftime('%I:%M %p') if attendance.get('guardInTime') else 'N/A'}\n"
    #     f"Timesheet Time on date {datetime.fromisoformat(attendance.get('date').replace('Z','+00:00')).strftime('%d %B %Y') if attendance.get('date') else 'N/A'} is: {attendance.get('timeSheetTime', 'N/A')}\n"
    #     # f"Total Time in Office on date {datetime.fromisoformat(attendance.get('date').replace('Z','+00:00')).strftime('%d %B %Y') if attendance.get('date') else 'N/A'} is: {attendance.get('totalTimeInOffice', 'N/A')}\n"
    #     # f"Total Time in Work Zone on date {datetime.fromisoformat(attendance.get('date').replace('Z','+00:00')).strftime('%d %B %Y') if attendance.get('date') else 'N/A'} is: {attendance.get('totalTimeInWorkZone', 'N/A')}\n"
    #     f"Timesheet Status: {'Approved' if attendance.get('timesheetStatus') == 2 else 'Pending'}\n"
    #     f"Upwork Status: {'Approved' if attendance.get('upworkStatus') == 2 else 'Pending'})\n"
    #     for attendance in attendance_data
    # ])

                except Exception as e:
                    return f"Error while connecting to daily attendence API: {str(e)}"
            
        return await get_cached_or_search(cache_key,search,1800)