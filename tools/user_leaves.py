import httpx
from datetime import datetime
from utils.redis_cache import get_cached_or_search

def register_user_leaves(mcp):
    @mcp.tool()
    async def get_user_leaves(auth_token, request_data)-> str:
        """  
        This tool provides details / history of leaves taken by the user.
        It describes:
        - applied date of leave
        - leave duration
        - leave status
        - leave reason
        - leave send to
        - total leaves taken
        DO NOT use this tool if user asks about LEAVE BALANCE
        args:
        - auth_token
        - request_data
        """
        if not request_data.get('_id'):
            return "Your user id is not found"
        
        cache_key=f"user_leaves:{request_data.get('_id','')}"

        async def search():
            USER_LEAVES_API="https://api.portal.chicmicstudios.in/v1/leave/history"

            headers={
                "authorization": auth_token,
                "content-type": "application/json"
            }

            body=request_data

            async with httpx.AsyncClient() as client:
                try:
                    response=await client.post(USER_LEAVES_API,headers=headers,json={"userId":body['_id']})
                    if response.status_code==200:
                        data=response.json()['data']['data']
                        return "\n\n".join([
                        f"(Leave Reason/Comment: {leave.get('reason')}\n"
                        f"Date: {leave.get('fromDate')} to {leave.get('toDate')}\n"
                        f"The leave is taken in {(datetime.strptime(leave.get('fromDate'), '%Y-%m-%dT%H:%M:%S.%fZ')).strftime('%B')} month\n"
                        f"Status: This leave is {'Pending' if leave.get('status')==1 else 'Approved'}\n"
                        f"Leave application is sent to {[manager.get('name') for manager in leave.get('sendTo')]}\n"
                        f"Duration of the leave is {leave.get('totalDays')}\n"
                        f"Leave Type: {leave.get('leaveType')} -> {leave.get('leaveReasonName')}\n"
                        f"Is sandwich applied on this leave: {'Yes' if leave.get('isSandwichApplied') else 'No'})\n"
                        for leave in data
                        ])
                    else:
                        return f"Error: Recieved status code {response.status_code} from API"
                except Exception as e:
                    return f"Failed to connect to the leaves history API: {str(e)}"
        return await get_cached_or_search(cache_key, search,ttl=600)