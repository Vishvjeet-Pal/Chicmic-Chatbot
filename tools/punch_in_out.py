import httpx
from datetime import datetime
from utils.format_date import normalize_date

def register_punch_tool(mcp):
  @mcp.tool()
  async def punch_in_out(auth_token, request_data, date=datetime.today().strftime('%d-%m-%Y')):

      """
Fetches employee punch in/out records for a specific date.

Use for queries about: punch time, punch direction (IN/OUT), device name, or floor of punch.

Rules:
- Do NOT assume year if not mentioned.
- If date not provided in query, use request_data["date"].

Params:
- auth_token (required)
- request_data (must contain empId, optionally date)
- date (optional, user-provided)
"""

      PUNCH_IN_OUT_URL="https://api.portal.chicmicstudios.in/v1/biometric/punches"

      headers = {
          "Authorization": auth_token,
          "Content-Type": "application/json"
        }

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
            response = await client.post(PUNCH_IN_OUT_URL, headers=headers, json={"date":datetime.strptime(final_date, "%d-%m-%Y").strftime("%Y-%m-%d") or request_data['date'],"empId":request_data['empId']})
          
            punch_data = response.json()["data"]

            return "\n\n".join([
              f"Punch Month is: { datetime.fromisoformat(punch.get('punchMonth').replace('Z', '+00:00')).strftime('%B')}\n"
              f"punched {punch.get('devDirection')} on date : {datetime.fromisoformat(punch.get('attPunchDownDate').replace('Z', '+00:00')).strftime('%d %B %Y, %I:%M %p')} or {display_date_short} or {final_date}\n"
              f"punched at : {punch.get('deviceName')}\n"
              
              for punch in punch_data if datetime.fromisoformat(punch.get('attPunchDownDate').replace('Z', '+00:00')).strftime('%d-%m-%Y') == final_date 
            ])
            
          except Exception as e:
            return f"Error while connecting to punch in/out API: {str(e)}"