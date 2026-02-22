import httpx
from utils.redis_cache import get_cached_or_search

def register_user_profile(mcp):
    @mcp.tool()
    async def get_user_profile_data(auth_token: str, request_data):
        """
        Provide the current logged-in user's profile/personal and official details such as:
        - AT WHAT TIME SHOULD I COME TO OFFICE
        - My Name
        - My email
        - My joining data
        - My Employee Id
        - My Official Email
        - My teams
        - My leave Balance
        - My role
        - MY SHIFT/OFFICE TIMING

        Args:
            - auth_token: The system authentication token.
            - request_data
        """

        if not request_data.get('_id'):
            return "Your user id is not found"
        cache_key=f"profile:{request_data.get('_id','')}"
        # async def search():
        PROFILE_API_URL = f"https://api.portal.chicmicstudios.in/v1/user?_id={request_data['_id']}"
        headers = {
            "Authorization": auth_token, 
            "Content-Type": "application/json"
        }
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(PROFILE_API_URL, headers=headers)
                if response.status_code == 200:
                    data = response.json()['data']
                    profile_info = (
                        f"User Profile Found:\n"
                        f"- Name: {data.get('name')}\n"
                        f"- Email: {data.get('personalEmail')}\n"
                        f"- Joining Date: {data.get('joiningDate')}\n"
                        f"- Employee Id: {data.get('employeeId')}\n"
                        f"- Official Email: {data.get('officialEmail')}\n"
                        f"- You are in teams: {[team.get('name') for team in data.get('teams')]}\n"
                        f"- Waiver Count: {data.get('waiverCount')}\n"
                        f"- Leave Balance: {data.get('leaveBalance')}\n"
                        f"- Your role/designation is {data.get('roleData').get('name')}\n"
                        f"- Your shift time or office timing is {data.get('minInTime')} and you have to complete 8 hours in the office. After completing 8 hours you can leave office and go home."
                    )
                    return profile_info
                else:
                    return f"Error: Received {response.status_code} from API."
            except Exception as e:
                return f"Failed to connect to profile API: {str(e)}"
        # return await get_cached_or_search(cache_key, search,ttl=3*3600)