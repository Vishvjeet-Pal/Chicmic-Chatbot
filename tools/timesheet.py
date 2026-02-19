import httpx
from utils.redis_cache import get_cached_or_search

def register_timesheet(mcp):
    @mcp.tool()
    async def my_timesheet_search(auth_token, request_data)-> str:
        """
        Use this tool ONLY when the user asks about its timesheet details such as:
        - projects
        - timesheets
        - Upwork Status
        - Timesheet Status
        - Timesheet Date
        - tasks
        - time spent
        - work logs
        - employee work details

        This tool searches timesheet/project information from the given api.

        args:
        - auth_token
        - request_data
        """

        if not request_data.get('_id'):
            return "Your user id is not found"
        
        cache_key=f"timesheet:{request_data.get('_id','')}"

        async def search():
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
                        return "\n\n".join([
                            f"(- Date: {timesheet.get('entryDate')}\n"
                            f"- Time Spent: {timesheet.get('timeSpent')}\n"
                            f"- Projects: {timesheet.get('projects')}\n"
                            f"- Upwork Status: {'Approved' if timesheet.get('upworkStatus')==2 else 'Pending'}\n"
                            f"- Timesheet Status: {'Approved' if timesheet.get('timesheetStatus')==2 else 'Pending'}\n"
                            f"- User Name: {timesheet.get('userName')}\n"
                            f"- Employee Id: {timesheet.get('employeeId')})\n"
                            for timesheet in data
                        ])
                    else:
                        return f"Error: Received {response.status_code} from API."
                except Exception as e:
                    return f"Failed to connect to timesheet API: {str(e)}"
        return await get_cached_or_search(cache_key, search)        