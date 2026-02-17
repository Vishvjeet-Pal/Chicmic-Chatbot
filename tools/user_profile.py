import httpx

def register_user_profile(mcp):
    @mcp.tool()
    async def get_user_profile_data(auth_token: str, request_data):
        """
        Provide the current logged-in user's profile details such as:
        - My Name
        - My email
        - My joining data
        - My Employee Id
        - My Official Email
        - My teams
        - My leave Balance
        - My role
        - My shift timing

        Args:
            - auth_token: The system authentication token.
            - request_data
        """
        # print("auth:",auth_token)
        # if auth_token == "placeholder":
        #     return "ERROR: Middleware failed to inject the real token!"
        # return auth_token[:20]
        # return auth_token
        PROFILE_API_URL = f"https://api.portal.chicmicstudios.in/v1/user?_id={request_data['_id']}"
        headers = {
            "Authorization": auth_token, #config.get("configurable",{}).get("auth_token",""),
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
                        f"- Teams: {[team.get('name') for team in data.get('teams')]}\n"
                        f"- Waiver Count: {data.get('waiverCount')}\n"
                        f"- Leave Balance: {data.get('leaveBalance')}\n"
                        f"- Role: {data.get('roleData').get('name')}\n"
                        f"- Shift Time: {data.get('minInTime')}"
                    )
                    return profile_info
                else:
                    return f"Error: Received {response.status_code} from API."
            except Exception as e:
                return f"Failed to connect to profile API: {str(e)}"