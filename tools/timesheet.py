import httpx
from utils.redis_cache import get_cached_or_search
from utils.format_date import normalize_date
from datetime import datetime

def register_timesheet(mcp):
    @mcp.tool()
    async def my_timesheet_search(auth_token, request_data, date="")-> str:
        """
        Use this tool ONLY when the user asks about its timesheet details such as:
        - projects
        - Details of all timesheets of user
        - Upwork Status
        - Timesheet Status
        - Timesheet Date
        - tasks
        - time spent
        - work logs
        - employee work details

        This tool searches timesheet/project information from the given api.

        INSTRUCTIONS:
            - If year is not mentioned in user's query, DO NOT ASSUME year. Just provide date without year.

        STRICT RULES:
            - If no year is mentioned in date, Do NOT assume the year.

        args:
        - auth_token: provided in the header of request
        - request_data
        - date: provided by user in the query, if no date is mentioned in the query take default value of date provided in tool definition
        """

        if not request_data.get('_id'):
            return "Your user id is not found"
        
        # cache_key=f"timesheet:{request_data.get('_id','')}"

        display_date_full = "today"
        display_date_short = "today"

        try:
            final_date = normalize_date(date)
        except Exception:
            return "Please use format like '19 Feb' or '19-02-2026'."

        if final_date:
            dt = datetime.strptime(final_date, "%d-%m-%Y")
            display_date_full = dt.strftime("%d %b %Y")   
            display_date_short = dt.strftime("%d %b")

        # async def search():
            TIMESHEET_API_URL = "https://api.portal.chicmicstudios.in/v1/timesheet/history?index=0&limit=10"
            
            headers = {
                "Authorization": auth_token,
                "Content-Type": "application/json"
            }

            async with httpx.AsyncClient() as client:
                try:
                    response = await client.get(TIMESHEET_API_URL, headers=headers) 
                    if response.status_code == 200:
                        data = response.json()['data']['data']

                        pending_timesheet=0
                        for timesheet in data:
                            if timesheet.get('timesheetStatus','')==1:
                                pending_timesheet+=1

                        if final_date:
                            matched_leaves= "\n".join([
                                f"(- Date of the timesheet: {datetime.strptime(timesheet.get('entryDate'), '%Y-%m-%d').strftime('%d-%m-%Y')} or {display_date_full} or {display_date_short}\n"
                                f"- Time Spent on the timesheet: {timesheet.get('timeSpent')}\n"
                                f"- Projects included in timesheet: {timesheet.get('projects')}\n"
                                # f"- Upwork Status: {'Approved' if timesheet.get('upworkStatus')==2 else 'Pending'}\n"
                                f"- This timesheet is submitted and {'Approved' if timesheet.get('timesheetStatus')==2 else 'Pending'} (This is status of timesheet)\n"
                                f"- This timesheet is filled/submitted by you ({timesheet.get('userName')}) having employee id : {timesheet.get('employeeId')})"
                                for timesheet in data if datetime.strptime(timesheet.get('entryDate'), '%Y-%m-%d').strftime('%d-%m-%Y')==final_date
                            ])
                            if matched_leaves:
                                return matched_leaves
    

                        result=f"You have {pending_timesheet} pending timesheets and remaining are approved.\nDetails of your pending timesheets are:\n"
                        result+= "\n\n".join([
                            f"(- Date of the timesheet: {datetime.strptime(timesheet.get('entryDate'), '%Y-%m-%d').strftime('%d-%m-%Y')} or {'today' if datetime.today()==datetime.strptime(timesheet.get('entryDate'), '%Y-%m-%d') else datetime.strptime(timesheet.get('entryDate'), '%Y-%m-%d').strftime('%d-%B-%Y')} or {datetime.strptime(timesheet.get('entryDate'), '%Y-%m-%d').strftime('%d-%B')}\n"
                            f"- Time Spent on the timesheet: {timesheet.get('timeSpent')}\n"
                            f"- Projects included in timesheet: {timesheet.get('projects')}\n"
                            # f"- Upwork Status: {'Approved' if timesheet.get('upworkStatus')==2 else 'Pending'}\n"
                            f"- This timesheet is submitted and {'Approved' if timesheet.get('timesheetStatus')==2 else 'Pending'} (This is status of timesheet)\n"
                            f"- This timesheet is filled/submitted by you ({timesheet.get('userName')}) having employee id : {timesheet.get('employeeId')})"
                            for timesheet in data if timesheet.get('timesheetStatus')==1
                        ])

                        result+="\n\nDetails of your approved timesheets are:\n"
                        result+= "\n\n".join([
                            f"(- Date of the timesheet: {datetime.strptime(timesheet.get('entryDate'), '%Y-%m-%d').strftime('%d-%m-%Y')} or {display_date_full} or {display_date_short}\n"
                            f"- Time Spent on the timesheet: {timesheet.get('timeSpent')}\n"
                            f"- Projects included in timesheet: {timesheet.get('projects')}\n"
                            # f"- Upwork Status: {'Approved' if timesheet.get('upworkStatus')==2 else 'Pending'}\n"
                            f"- This timesheet is submitted and {'Approved' if timesheet.get('timesheetStatus')==2 else 'Pending'} (This is status of timesheet)\n"
                            f"- This timesheet is filled/submitted by you ({timesheet.get('userName')}) having employee id : {timesheet.get('employeeId')})"
                            for timesheet in data if timesheet.get('timesheetStatus')==2
                        ])
                        return result
                    else:
                        return f"Error: Received {response.status_code} from API."
                except Exception as e:
                    return f"Failed to connect to timesheet API: {str(e)}"
        # return await get_cached_or_search(cache_key, search)        