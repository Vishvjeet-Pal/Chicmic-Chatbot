from mcp.server.fastmcp import FastMCP
from langchain_ollama import OllamaEmbeddings
import os
import httpx
from vector_data import vector_store
from datetime import datetime, timedelta, timezone
from tools.attendance import register_attendance
from tools.holidays import register_holidays
from tools.project_details import register_project
from tools.punch_in_out import register_punch_tool
from tools.referral_policy import register_referral
from tools.search_policy import register_search_policy
from tools.time_spent import register_time_spent
from tools.timesheet import register_timesheet
from tools.tracker_details import register_tracker_details
from tools.user_leaves import register_user_leaves
from tools.user_profile import register_user_profile

# import redis.asyncio as redis

# Redis connection
# redis_client = redis.Redis(
#     host="localhost",
#     port=6379,
#     decode_responses=True,
#     max_connections=10
# )

# async def get_cached_or_search(cache_key, search_fn, ttl=300):

#     cached = await redis_client.get(cache_key)
#     if cached:
#         return f"(cached)\n{cached}"


#     result = await search_fn()

#     await redis_client.set(cache_key, result, ex=ttl)
#     return result


mcp = FastMCP("Company Assistant")

register_user_profile(mcp)
register_attendance(mcp)
register_holidays(mcp,vector_store)
register_punch_tool(mcp)
register_referral(mcp,vector_store)
register_search_policy(mcp,vector_store)
register_project(mcp)
register_time_spent(mcp)
register_timesheet(mcp)
register_tracker_details(mcp)
register_user_leaves(mcp)

embeddings = OllamaEmbeddings(model="nomic-embed-text")



# @mcp.tool()
# async def search_faq(query: str) -> str:
#     """Find answers to FAQs using semantic similarity search.
#     Answer frequently asked questions such as "How do I reset my password?" or "What are office hours?"."""
#     # Perform similarity search instead of SQL WHERE
#     docs = vector_store.similarity_search(query, k=3, filter={"type": "faq"})
    
#     if not docs:
#         return "No relevant FAQ found for your query."
    
#     results = []
#     for doc in docs:
#         results.append(f"Q: {doc.metadata.get('question')}\nA: {doc.page_content}")
    
#     return "\n---\n".join(results)



# @mcp.tool()
# async def get_policy_by_semantic_match(query: str) -> str:
#     """Return company policies such as employee leave policy, sick leave, maternity leave, etc."""

#     cache_key = f"policy:{query}"

#     async def search():
#         docs = vector_store.similarity_search(query, k=4, filter={"type": "policy"})
#         if not docs:
#             return "No matching policies found."
#         return "\n\n".join(
#             [f"Policy: {d.metadata.get('title')}\nDetails: {d.page_content}" for d in docs]
#         )

#     return await get_cached_or_search(cache_key, search)


# @mcp.tool()
# async def login_credentials(query: str) -> str:
#     """Provide login support for various company platforms.
#     Answer queries such as:
#     - "How can i reset my password?" or "What if I forget my ERP password?" 
#     """
#     cache_key = f"login:{query}"

#     async def search():
#         docs = vector_store.similarity_search(query, k=4, filter={"type": "login"})
#         if not docs:
#             return "No relevant credentials found for your query."

#         return "\n\n".join(
#             [f"Question: {d.metadata.get('question')}\nAnswer: {d.page_content}" for d in docs]
#         )

#     return await get_cached_or_search(cache_key, search)

# @mcp.tool()
# async def personal_info(query: str) -> str:
#     """Provide personal information of employees related to the ERP system such as how to access and edit personal details."""
#     cache_key=f"personal_info:{query}"

#     async def search():
#         docs = vector_store.similarity_search(query, k=3, filter={"type": "personal_info"})

#         if not docs:
#             return "No relevant credentials found for your query."
    
#         return "\n\n".join([f"Question: {d.metadata.get('question')}\nAnswer: {d.page_content}" for d in docs])
#     return await get_cached_or_search(cache_key, search)
   
# @mcp.tool()
# async def search_policy(query: str) -> str:
#     """
#     Search and extract information from company policy documents.

#     This tool retrieves accurate policy details from official company documents such as:
#     - Leave Policy (annual leave, earned leave, casual/sick leave, maternity leave, training leave, probation leave)
#     - Leave Calculation Rules (sandwich rule, pro-rata leave, 5+2 rule, leave deduction, compensatory leave)
#     - Work rules related to leave (approval process, leave during training, leave during probation)

#     Use this tool when the user asks about:
#     - Leave entitlement, leave balance, leave types
#     - How leave is calculated or deducted
#     - Sandwich rule or weekend/holiday leave counting
#     - Working on holidays or compensatory leave
#     - Leave during probation or training
#     - Leave approval process
#     - Any question combining leave + holidays

#     Instructions:
#     - Extract only relevant policy information matching the user query.
#     - If multiple policies are relevant, combine them logically.
#     - If exact answer is not found, return the closest matching policy rule.
#     - If nothing relevant exists, return: "No relevant policy found."
#     - Do NOT generate information outside the documents.
#     """

#     cache_key = f"pdf_policy:{query}"

#     async def search():
#         docs = vector_store.similarity_search(
#             query,
#             k=5
#         )
#         print(docs)
#         if not docs:
#             return "No relevant information found in PDF."

#         return "\n\n".join([d.page_content for d in docs])

#     return await get_cached_or_search(cache_key, search)


# @mcp.tool()
# async def search_policy(query: str) -> str:
#     """
#     Search and extract information from company policy documents.
#     DO NOT use this tool if user asks about LEAVE BALANCE
#     This tool retrieves accurate policy details from official company documents such as:
#     - Leave Policy (annual leave, earned leave, casual/sick leave, maternity leave, training leave, probation leave)
#     - Leave Calculation Rules (sandwich rule, pro-rata leave, 5+2 rule, leave deduction, compensatory leave)
#     - Work rules related to leave (approval process, leave during training, leave during probation)

#     Use this tool when the user asks about:
#     - leave types
#     - How leave is calculated or deducted
#     - Sandwich rule or weekend/holiday leave counting
#     - Working on holidays or compensatory leave
#     - Leave during probation or training
#     - Leave approval process
#     - Any question combining leave + holidays

#     Instructions:
#     - Extract only relevant policy information matching the user query.
#     - If multiple policies are relevant, combine them logically.
#     - If exact answer is not found, return the closest matching policy rule.
#     - If nothing relevant exists, return: "No relevant policy found."
#     - Do NOT generate information outside the documents.
#     """

#     cache_key = f"leave_policy:{query}"

#     async def search():
#         docs = vector_store.similarity_search(
#             query,
#             k=5,
#             filter=({"type": {
#             "$in": ["leave_policy", "leave_calculation_policy"]
#         }})
#         )
#         print(docs)
#         if not docs:
#             return "No relevant information found in PDF."

#         return "\n\n".join([d.page_content for d in docs])

#     return await get_cached_or_search(cache_key, search)


# @mcp.tool()
# async def referral_policy(query: str) -> str:
#     """Provide information about the employee referral policy based on the content of the uploaded PDF documents."""

#     cache_key = f"referral_policy:{query}"

#     async def search():
#         docs = vector_store.similarity_search(
#             query,
#             k=2,
#             filter={"type": "referral_policy"}
#         )
#         # print(docs)
#         if not docs:
#             return "No relevant information found in PDF."

#         return "\n\n".join([d.page_content for d in docs])

#     return await get_cached_or_search(cache_key, search)

# @mcp.tool()
# async def my_timesheet_search(auth_token)-> str:
#     """
#     Use this tool ONLY when the user asks about its timesheet details such as:
#     - projects
#     - timesheets
#     - Upwork Status
#     - Timesheet Status
#     - Timesheet Date
#     - tasks
#     - time spent
#     - work logs
#     - employee work details

#     This tool searches timesheet/project information from the given api.

#     args:
#     - auth_token
#     """
#     TIMESHEET_API_URL = "https://api.portal.chicmicstudios.in/v1/timesheet/history?index=0&limit=10"
    
#     headers = {
#         "Authorization": auth_token,
#         "Content-Type": "application/json"
#     }

#     async with httpx.AsyncClient() as client:
#         try:
#             response = await client.get(TIMESHEET_API_URL, headers=headers) 
#             if response.status_code == 200:
#                 data = response.json()['data']['data']
#                 return "\n\n".join([
#                     f"(- Date: {timesheet.get('entryDate')}\n"
#                     f"- Time Spent: {timesheet.get('timeSpent')}\n"
#                     f"- Projects: {timesheet.get('projects')}\n"
#                     f"- Upwork Status: {'Approved' if timesheet.get('upworkStatus')==2 else 'Pending'}\n"
#                     f"- Timesheet Status: {'Approved' if timesheet.get('timesheetStatus')==2 else 'Pending'}\n"
#                     f"- User Name: {timesheet.get('userName')}\n"
#                     f"- Employee Id: {timesheet.get('employeeId')})\n"
#                     for timesheet in data
#                 ])
#             else:
#                 return f"Error: Received {response.status_code} from API."
#         except Exception as e:
#             return f"Failed to connect to timesheet API: {str(e)}"

# @mcp.tool()
# async def list_holidays(query: str) -> str:
#     """
#     Use this tool ONLY when the user asks about holidays.
#     - Company holiday dates or holiday rules
#     - Upcoming holidays or next holiday
#     - Holiday calendar for a specific year
#     - Leave planning with holidays
#     This tool searches holidays calendar from the vector database.
#     """
#     cache_key = f"holiday:{query}"

#     async def search():
#         docs = vector_store.similarity_search(
#             query,
#             k=2,
#             filter={"type": "holiday_calendar"}
#         )
#         # print(docs)
#         if not docs:
#             return "No relevant information found."

#         return "\n\n".join([d.page_content for d in docs])

#     return await get_cached_or_search(cache_key, search)

# Extracting data from API

# @mcp.tool()
# async def get_user_profile_data(auth_token: str, request_data):
#     """
#     Provide the current logged-in user's profile details such as:
#     - My Name
#     - My email
#     - My joining data
#     - My Employee Id
#     - My Official Email
#     - My teams
#     - My leave Balance
#     - My role
#     - My shift timing

#     Args:
#         - auth_token: The system authentication token.
#         - request_data
#     """
#     # print("auth:",auth_token)
#     # if auth_token == "placeholder":
#     #     return "ERROR: Middleware failed to inject the real token!"
#     # return auth_token[:20]
#     # return auth_token
#     PROFILE_API_URL = f"https://api.portal.chicmicstudios.in/v1/user?_id={request_data['_id']}"
#     headers = {
#         "Authorization": auth_token, #config.get("configurable",{}).get("auth_token",""),
#         "Content-Type": "application/json"
#     }
#     async with httpx.AsyncClient() as client:
#         try:
#             response = await client.get(PROFILE_API_URL, headers=headers)
#             if response.status_code == 200:
#                 data = response.json()['data']
#                 profile_info = (
#                     f"User Profile Found:\n"
#                     f"- Name: {data.get('name')}\n"
#                     f"- Email: {data.get('personalEmail')}\n"
#                     f"- Joining Date: {data.get('joiningDate')}\n"
#                     f"- Employee Id: {data.get('employeeId')}\n"
#                     f"- Official Email: {data.get('officialEmail')}\n"
#                     f"- Teams: {[team.get('name') for team in data.get('teams')]}\n"
#                     f"- Waiver Count: {data.get('waiverCount')}\n"
#                     f"- Leave Balance: {data.get('leaveBalance')}\n"
#                     f"- Role: {data.get('roleData').get('name')}\n"
#                     f"- Shift Time: {data.get('minInTime')}"
#                 )
#                 return profile_info
#             else:
#                 return f"Error: Received {response.status_code} from API."
#         except Exception as e:
#             return f"Failed to connect to profile API: {str(e)}"

# @mcp.tool()
# async def get_user_leaves(auth_token, request_data)-> str:
#     """  
#     This tool provides details / history of leaves taken by the user.
#     It describes:
#     - applied date of leave
#     - leave duration
#     - leave status
#     - leave reason
#     - leave send to
#     - total leaves taken
#     DO NOT use this tool if user asks about LEAVE BALANCE
#     args:
#     - auth_token
#     - request_data
#     """
#     USER_LEAVES_API="https://api.portal.chicmicstudios.in/v1/leave/history"

#     headers={
#         "authorization": auth_token,
#         "content-type": "application/json"
#     }

#     body=request_data

#     async with httpx.AsyncClient() as client:
#         try:
#             response=await client.post(USER_LEAVES_API,headers=headers,json={"userId":body['_id']})
#             if response.status_code==200:
#                 data=response.json()['data']['data']
#                 return "\n\n".join([
#                 f"(Leave Reason/Comment: {leave.get('reason')}\n"
#                 f"Date: {leave.get('fromDate')} to {leave.get('toDate')}\n"
#                 f"The leave is taken in {(datetime.strptime(leave.get('fromDate'), '%Y-%m-%dT%H:%M:%S.%fZ')).strftime('%B')} month\n"
#                 f"Status: {'Pending' if leave.get('status')==1 else 'Approved'}\n"
#                 f"Leave application is sent to {[manager.get('name') for manager in leave.get('sendTo')]}\n"
#                 f"Duration of the leave is {leave.get('totalDays')}\n"
#                 f"Leave Type: {leave.get('leaveType')} -> {leave.get('leaveReasonName')}\n"
#                 f"Is sandwich applied: {'Yes' if leave.get('isSandwichApplied') else 'No'})\n"
#                 for leave in data
#                 ])
#             else:
#                 return f"Error: Recieved status code {response.status_code} from API"
#         except Exception as e:
#             return f"Failed to connect to the leaves history API: {str(e)}"
        
# @mcp.tool()
# async def get_tracker_details(auth_token: str) -> str:
#     """
#     Use this tool when user asks about:
#     - Tracker details
#     - Allocated users in tracker
#     - Project linked to tracker
#     - My trackers (backend filters by token)

#     args: auth_token
#     """

#     TRACKER_API_URL = "https://api.portal.chicmicstudios.in/v1/project/trackers/detail"

#     # auth_token = config.get("configurable", {}).get("auth_token")

#     if not auth_token:
#         return "Authorization token is missing."

#     headers = {
#         "Authorization": auth_token,
#         "Content-Type": "application/json"
#     }

#     async with httpx.AsyncClient(timeout=30.0) as client:
#         try:
#             response = await client.get(TRACKER_API_URL, headers=headers)

#             if response.status_code == 401:
#                 return "Unauthorized access. Please login again."

#             if response.status_code == 403:
#                 return "You are not authorized to view tracker details."

#             if response.status_code != 200:
#                 return f"Error: Received {response.status_code} from API."

#             response_json = response.json()
#             tracker_list = response_json.get("data", {}).get("trackerData", [])

#             if not tracker_list:
#                 return "No tracker data found."

#             formatted_output = []

#             for tracker in tracker_list:
#                 tracker_name = tracker.get("trackerName", "N/A")
#                 tracker_email = tracker.get("email", "N/A")
#                 tracker_owner = tracker.get("name", "N/A")

#                 for proj in tracker.get("projectDetail", []):
#                     project_name = proj.get("projectName", "N/A")

#                     allocated_users = proj.get("allocatedUsers", [])
#                     user_list = ", ".join(
#                         [u.get("userName", "Unknown") for u in allocated_users]
#                     ) or "No allocated users"

#                     formatted_output.append(
#                         f"Tracker Name: {tracker_name}\n"
#                         f"Tracker Owner: {tracker_owner}\n"
#                         f"Email: {tracker_email}\n"
#                         f"Project: {project_name}\n"
#                         f"Allocated Users: {user_list}\n"
#                         f"{'-'*40}"
#                     )

#             return "\n".join(formatted_output)

#         except Exception as e:
#             return f"Failed to fetch tracker details: {str(e)}"
        
# @mcp.tool()
# async def get_project_details(auth_token, request_data):
#     """
#     Use this tool when user asks about:
#     - project overview
#     - project status
#     - tasks
#     - billing
#     - tracker details
#     - PM time
#     - milestone

#     args:
#     - query
#     - auth_token
#     - request_data
#     """

#     PROJECT_API_URL = "https://erp-staging.projectlabs.in/v1/project/list"

#     headers = {
#         "Authorization": auth_token,
#         "Content-Type": "application/json"
#     }


#     async with httpx.AsyncClient() as client:
#         try:
#             response = await client.post(PROJECT_API_URL, headers=headers, json={"billingType":request_data['billingType']})

#             if response.status_code == 401:
#                 return "Unauthorized access. Please login again."

#             if response.status_code == 403:
#                 return "You are not authorized to access this information."

#             if response.status_code != 200:
#                 return f"Error: Received {response.status_code} from API."

#             project_list = response.json()["data"]["projectList"]
#             # return project_list
#             return "\n\n".join([
#                 f"Project name: {project.get('name')}\n"
#                 f"Project Description: {project.get('description')}\n"
#                 f"Starting date of the project: {project.get('startDate')}\n"
#                 f"Ending date of the project: {project.get('endDate')}\n"
#                 f"Tech stack used in the project: {[p.get('name') for p in project.get('projectTechStack')]}\n"
#                 f"Allocated Employees: {[employee.get('userName') for employee in project.get('allocatedEmployees')]}\n"
#                 f"Project Manager: {project.get('primaryProjectManagers').get('userName')}\n"
#                 # f"Trackers allocated: {[trackers.get('userName') for trackers in project.get('allocatedTrackers').get('allocatedUsers')]}\n"
#                 f"Client Name: {project.get('clientName')}\n"
#                 f"Client Company: {project.get('clientCompany')}\n"
#                 f"Default Task of the project {project.get('name')}: {[task.get('taskName') for task in project.get('defaultTask')]}\n"
#                 for project in project_list
#             ])
#         except Exception as e:
#             return f"Error while connecting to project API: {str(e)}"
        
# @mcp.tool()
# async def time_spent(auth_token, request_data):
#     """
#     Use this tool when user asks about:
#     - time spent of the day
#     - total time spent in office
#     - total working hours/time in office
#     - my biometric data

#     args:
#     - auth_token
#     - request_data
#     """

#     TIME_SPENT_API_URL = "https://api.portal.chicmicstudios.in/v1/biometric/time-spent"

#     headers = {
#         "Authorization": auth_token,
#         "Content-Type": "application/json"
#     }

#     async with httpx.AsyncClient() as client:
#         try:
#             response = await client.post(TIME_SPENT_API_URL, headers=headers, json={"date":request_data['date'],"empId":request_data['empId']})

#             if response.status_code == 401:
#                 return "Unauthorized access. Please login again."

#             if response.status_code == 403:
#                 return "You are not authorized to access this information."

#             if response.status_code != 200:
#                 return f"Error: Received {response.status_code} from API."

#             biometric_time = response.json()["data"]

#             return "\n\n".join([
#                f"total time spent in work zone is : {biometric_time.get('totalTimeInWorkZone')}\n"
#                f"total time spent in office is :{biometric_time.get('totalTimeInOffice')}\n"
#             ])

#         except Exception as e:
#             return f"Error while connecting to time spent API: {str(e)}"

# @mcp.tool()
# async def get_daily_attendence(auth_token):
#     """
#     This tool provides daily timesheet and attendance details of a user.

# Use this tool when the user asks about:
# - Daily attendance
# - In-time or out-time
# - Total working hours
# - Time spent in office or work zone
# - Work from home status
# - Holiday status
# - How much of my Leaves deducted
# - Timesheet status
# - Upwork status
# - Main Gate in/out time

#     args:
#     - auth_token
#     - request_data
#     """
#     DAILY_ATTENDENCE_API_URL = f"https://api.portal.chicmicstudios.in/v1/timesheet/in/out?month=1&year=2026&userId=695b6def20ccf734da8d4d0c"

#     headers = {
#         "Authorization": auth_token,
#         "Content-Type": "application/json"
#     }

#     IST = timezone(timedelta(hours=5, minutes=30))

#     async with httpx.AsyncClient() as client:
#         try:
#             response = await client.get(DAILY_ATTENDENCE_API_URL, headers=headers)

#             if response.status_code == 401:
#                 return "Unauthorized access. Please login again."

#             if response.status_code == 403:
#                 return "You are not authorized to access this information."

#             if response.status_code != 200:
#                 return f"Error: Received {response.status_code} from API."

#             attendance_data = response.json()["data"]["data"][0]['stats']

#             return "\n\n".join([
#     f"(Day: {attendance.get('day')}\n"
#     f"work zone in Time: {datetime.strptime(attendance.get('inTime'), '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc).astimezone(IST).strftime('%I:%M %p') if attendance.get('inTime') else 'N/A'}\n"
#     f"work zone Out Time: {datetime.strptime(attendance.get('outTime'), '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc).astimezone(IST).strftime('%I:%M %p') if attendance.get('outTime') else 'N/A'}\n"
#     f"Date: {datetime.fromisoformat(attendance.get('date').replace('Z','+00:00')).strftime('%d %B %Y') if attendance.get('date') else 'N/A'}\n"
#     f"Is it Work From Home: {'Yes' if attendance.get('isWfh') else 'No'}\n"
#     f"Is it Holiday: {'Yes' if attendance.get('isHoliday') else 'No'}\n"
#     f"Leaves Deducted: {attendance.get('leavesDeducted', 0)}\n"
#     f"Main gate Out Time: {datetime.strptime(attendance.get('guardOutTime'), '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc).astimezone(IST).strftime('%I:%M %p') if attendance.get('guardOutTime') else 'N/A'}\n"
#     f"main gate in Time: {datetime.strptime(attendance.get('guardInTime'), '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc).astimezone(IST).strftime('%I:%M %p') if attendance.get('guardInTime') else 'N/A'}\n"
#     f"Timesheet Time: {attendance.get('timeSheetTime', 'N/A')}\n"
#     f"Total Time in Office: {attendance.get('totalTimeInOffice', 'N/A')}\n"
#     f"Total Time in Work Zone: {attendance.get('totalTimeInWorkZone', 'N/A')}\n"
#     f"Timesheet Status: {'Approved' if attendance.get('timesheetStatus') == 2 else 'Pending'}\n"
#     f"Upwork Status: {'Approved' if attendance.get('upworkStatus') == 2 else 'Pending'})\n"
#     for attendance in attendance_data
# ])

#         except Exception as e:
#             return f"Error while connecting to daily attendence API: {str(e)}"
        

# @mcp.tool()
# async def punch_in_out(auth_token, request_data):

#     """
#     Use this tool when the user asks about:
# - Punch in or punch out time
# - Device punch records
# - From which device or floor the punch was recorded
# - Direction of punch (IN / OUT)

# args:
# - auth_token
# - request_data
#     """

#     PUNCH_IN_OUT_URL="https://api.portal.chicmicstudios.in/v1/biometric/punches"

#     headers = {
#         "Authorization": auth_token,
#         "Content-Type": "application/json"
#       }

#     async with httpx.AsyncClient() as client:
#         try:
#           response = await client.post(PUNCH_IN_OUT_URL, headers=headers, json={"date":request_data['date'],"empId":request_data['empId']})
        
#           punch_data = response.json()["data"]

#           return "\n\n".join([
#             f"Punch Month is: { datetime.fromisoformat(punch.get('punchMonth').replace('Z', '+00:00')).strftime('%B')}\n"
#              f"punched {punch.get('devDirection')} on date : {datetime.fromisoformat(punch.get('attPunchDownDate').replace('Z', '+00:00')).strftime('%d %B %Y, %I:%M %p')}\n"
#             f"punch device name is : {punch.get('deviceName')}\n"
            
#             for punch in punch_data
#           ])
          
#         except Exception as e:
#           return f"Error while connecting to punch in/out API: {str(e)}"
               

if __name__ == "__main__":
    mcp.run(transport="stdio")