import httpx
from datetime import datetime

def register_punch_tool(mcp):
  @mcp.tool()
  async def punch_in_out(auth_token, request_data, date):

      """
      Use this tool when the user asks about:
  - Punch in or punch out time
  - Device punch records
  - From which device or floor the punch was recorded
  - Direction of punch (IN / OUT)

  args:
  - auth_token
  - request_data
  - date: provided by user in the query
      """

      PUNCH_IN_OUT_URL="https://api.portal.chicmicstudios.in/v1/biometric/punches"

      headers = {
          "Authorization": auth_token,
          "Content-Type": "application/json"
        }

      async with httpx.AsyncClient() as client:
          try:
            response = await client.post(PUNCH_IN_OUT_URL, headers=headers, json={"date":date,"empId":request_data['empId']})
          
            punch_data = response.json()["data"]

            return "\n\n".join([
              f"Punch Month is: { datetime.fromisoformat(punch.get('punchMonth').replace('Z', '+00:00')).strftime('%B')}\n"
              f"punched {punch.get('devDirection')} on date : {datetime.fromisoformat(punch.get('attPunchDownDate').replace('Z', '+00:00')).strftime('%d %B %Y, %I:%M %p')}\n"
              f"punch device name is : {punch.get('deviceName')}\n"
              
              for punch in punch_data
            ])
            
          except Exception as e:
            return f"Error while connecting to punch in/out API: {str(e)}"