import httpx
from utils.format_date import normalize_date
from datetime import datetime

def register_time_spent(mcp):
    @mcp.tool()
    async def time_spent(auth_token, request_data, date=datetime.today().strftime('%d-%m-%Y')):
        """
        Use this tool when user asks ONLY about:
        - time spent of the day
        - time spent in office/company
        - total working hours/time in office
        - my biometric data
        Note: This tool DOES NOT provide the office timings of the user.  Office timing is different from the time spent by user in the office.
        args:
        - auth_token
        - request_data
        - date: provided by user in the query, if no date is mentioned in the query take date from request_data argument

        INSTRUCTIONS:
        - If year is not mentioned in user's query, DO NOT ASSUME year. Just provide date without year.

        STRICT RULES:
        - If no year is mentioned in date, Do NOT assume the year.
        """

        TIME_SPENT_API_URL = "https://api.portal.chicmicstudios.in/v1/biometric/time-spent"

        headers = {
            "Authorization": auth_token,
            "Content-Type": "application/json"
        }

        display_date_full = "today"
        display_date_short = "today"

        try:
            final_date = normalize_date(date or request_data.get("date"))
        except Exception:
            return "Invalid date provided. Please use format like '19 Feb' or '19-02-2026'."
        
        if final_date:
            dt = datetime.strptime(final_date, "%d-%m-%Y")
            display_date_full = dt.strftime("%d %b %Y")   
            display_date_short = dt.strftime("%d %b")

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(TIME_SPENT_API_URL, headers=headers, json={"date":datetime.strptime(final_date, "%d-%m-%Y").strftime("%Y-%m-%d") or request_data['date'],"empId":request_data['empId']})

                if response.status_code == 401:
                    return "Unauthorized access. Please login again."

                if response.status_code == 403:
                    return "You are not authorized to access this information."

                if response.status_code != 200:
                    return f"Error: Received {response.status_code} from API."

                biometric_time = response.json()["data"]

                return "\n\n".join([
                f"total time spent in work zone on {display_date_full} or {display_date_short} or {final_date} is : {biometric_time.get('totalTimeInWorkZone')}\n"
                f"total time spent in office on {display_date_full} or {display_date_short} or {final_date} is : {biometric_time.get('totalTimeInOffice')}\n"
                f" You have to spent atleast 8 hours in the work zone"
                ])

            except Exception as e:
                return f"Error while connecting to time spent API: {str(e)}"