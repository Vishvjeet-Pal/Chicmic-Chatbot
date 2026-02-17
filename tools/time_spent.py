import httpx

def register_time_spent(mcp):
    @mcp.tool()
    async def time_spent(auth_token, request_data):
        """
        Use this tool when user asks about:
        - time spent of the day
        - total time spent in office
        - total working hours/time in office
        - my biometric data

        args:
        - auth_token
        - request_data
        """

        TIME_SPENT_API_URL = "https://api.portal.chicmicstudios.in/v1/biometric/time-spent"

        headers = {
            "Authorization": auth_token,
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(TIME_SPENT_API_URL, headers=headers, json={"date":request_data['date'],"empId":request_data['empId']})

                if response.status_code == 401:
                    return "Unauthorized access. Please login again."

                if response.status_code == 403:
                    return "You are not authorized to access this information."

                if response.status_code != 200:
                    return f"Error: Received {response.status_code} from API."

                biometric_time = response.json()["data"]

                return "\n\n".join([
                f"total time spent in work zone is : {biometric_time.get('totalTimeInWorkZone')}\n"
                f"total time spent in office is :{biometric_time.get('totalTimeInOffice')}\n"
                ])

            except Exception as e:
                return f"Error while connecting to time spent API: {str(e)}"