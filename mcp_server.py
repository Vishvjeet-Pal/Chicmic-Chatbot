from mcp.server.fastmcp import FastMCP
from langchain_ollama import OllamaEmbeddings
from langchain_core.runnables import RunnableConfig
import os
import httpx
from vector_data import vector_store


import redis.asyncio as redis

# Redis connection
redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True,
    max_connections=10
)

async def get_cached_or_search(cache_key, search_fn, ttl=300):

    cached = await redis_client.get(cache_key)
    if cached:
        return f"(cached)\n{cached}"


    result = await search_fn()

    await redis_client.set(cache_key, result, ex=ttl)
    return result


mcp = FastMCP("Company Assistant")


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


@mcp.tool()
async def search_policy(query: str) -> str:
    """
    Search and extract information from company policy documents.

    This tool retrieves accurate policy details from official company documents such as:
    - Leave Policy (annual leave, earned leave, casual/sick leave, maternity leave, training leave, probation leave)
    - Leave Calculation Rules (sandwich rule, pro-rata leave, 5+2 rule, leave deduction, compensatory leave)
    - Work rules related to leave (approval process, leave during training, leave during probation)

    Use this tool when the user asks about:
    - Leave entitlement, leave balance, leave types
    - How leave is calculated or deducted
    - Sandwich rule or weekend/holiday leave counting
    - Working on holidays or compensatory leave
    - Leave during probation or training
    - Leave approval process
    - Any question combining leave + holidays

    Instructions:
    - Extract only relevant policy information matching the user query.
    - If multiple policies are relevant, combine them logically.
    - If exact answer is not found, return the closest matching policy rule.
    - If nothing relevant exists, return: "No relevant policy found."
    - Do NOT generate information outside the documents.
    """

    cache_key = f"leave_policy:{query}"

    async def search():
        docs = vector_store.similarity_search(
            query,
            k=5,
            filter=({"type": {
            "$in": ["leave_policy", "leave_calculation_policy"]
        }})
        )
        print(docs)
        if not docs:
            return "No relevant information found in PDF."

        return "\n\n".join([d.page_content for d in docs])

    return await get_cached_or_search(cache_key, search)


@mcp.tool()
async def referral_policy(query: str) -> str:
    """Provide information about the employee referral policy based on the content of the uploaded PDF documents."""

    cache_key = f"referral_policy:{query}"

    async def search():
        docs = vector_store.similarity_search(
            query,
            k=2,
            filter={"type": "referral_policy"}
        )
        # print(docs)
        if not docs:
            return "No relevant information found in PDF."

        return "\n\n".join([d.page_content for d in docs])

    return await get_cached_or_search(cache_key, search)

@mcp.tool()
async def my_timesheet_search(config: RunnableConfig)-> str:
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
    """
    TIMESHEET_API_URL = "https://api.portal.chicmicstudios.in/v1/timesheet/history?index=0&limit=10"
    
    headers = {
        "Authorization": config.get("configurable", {}).get("auth_token"),
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
                    f"- Upwork Status: {"Approved" if timesheet.get('upworkStatus')==2 else "Pending"}\n"
                    f"- Timesheet Status: {"Approved" if timesheet.get('timesheetStatus')==2 else "Pending"}\n"
                    f"- User Name: {timesheet.get("userName")}\n"
                    f"- Employee Id: {timesheet.get("employeeId")})\n"
                    for timesheet in data
                ])
            else:
                return f"Error: Received {response.status_code} from API."
        except Exception as e:
            return f"Failed to connect to timesheet API: {str(e)}"

@mcp.tool()
async def list_holidays(query: str) -> str:
    """
    Use this tool ONLY when the user asks about holidays.
    - Company holiday dates or holiday rules
    - Upcoming holidays or next holiday
    - Holiday calendar for a specific year
    - Leave planning with holidays
    This tool searches holidays calendar from the vector database.
    """
    cache_key = f"holiday:{query}"

    async def search():
        docs = vector_store.similarity_search(
            query,
            k=2,
            filter={"type": "holiday_calendar"}
        )
        # print(docs)
        if not docs:
            return "No relevant information found."

        return "\n\n".join([d.page_content for d in docs])

    return await get_cached_or_search(cache_key, search)

# Extracting data from API

@mcp.tool()
async def get_user_profile_data(auth_token: str="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI2OTViNmRlZjIwY2NmNzM0ZGE4ZDRkMGMiLCJ0aW1lIjoxNzcxMTQ1NjkzMTA0LCJpYXQiOjE3NzExNDU2OTMsImV4cCI6MTc3MzczNzY5M30.h57fxP4s1kGf_Wvo3yGrU7MtfTDuRktWQhiHg-A3_jA") -> str:
    """
    Fetches the current logged-in user's profile details (email, joining date, etc.)
    from the company API using their active Auth Token.
    """
    PROFILE_API_URL = "https://api.portal.chicmicstudios.in/v1/user?_id=695b6def20ccf734da8d4d0c"
    
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
                    f"- Teams: {[team.get('name') for team in data.get('teams')]}\n"
                    f"- Waiver Count: {data.get("waiverCount")}\n"
                    f"- Leave Balance: {data.get("leaveBalance")}\n"
                    f"- Role: {data.get("roleData").get("name")}\n"
                    f"- Shift Time: {data.get("minInTime")}"
                    # f"- Designation: {data.get('designation')}"
                )
                return profile_info
            else:
                return f"Error: Received {response.status_code} from API."
        except Exception as e:
            return f"Failed to connect to profile API: {str(e)}"

@mcp.tool()
async def get_user_leaves(config: RunnableConfig):
    """  
    This tool provides details / history of leaves taken by the user.
    It describes:
    - applied date of leave
    - leave duration
    - leave status
    - leave reason
    - leave send to
    - total leaves taken
    """
    USER_LEAVES_API="https://api.portal.chicmicstudios.in/v1/leave/history"

    headers={
        "authorization": config.get("configurable",{}).get("auth_token"),
        "content-type": "application/json"
    }

    body=config.get("configurable",{}).get("request_data",{})

    async with httpx.AsyncClient() as client:
        try:
            response=await client.post(USER_LEAVES_API,headers=headers,json=body)
            if response.status_code==200:
                data=response.json()['data']['data']
                # return [data]
                return "\n\n".join([
                f"(Leave Reason/Comment: {leave.get('reason')}\n"
                f"Date: {leave.get("fromDate")} to {leave.get("toDate")}\n"
                f"Status: {'Pending' if leave.get('status')==1 else "Approved"}\n"
                f"Leave application is sent to {[manager.get('name') for manager in leave.get("sendTo")]}\n"
                f"Duration of the leave is {leave.get("totalDays")}\n"
                f"Leave Type: {leave.get("leaveType")} -> {leave.get("leaveReasonName")}\n"
                f"Is sandwich applied: {'Yes' if leave.get("isSandwichApplied") else 'No'})\n"
                for leave in data
                ])
            else:
                return f"Error: Recieved status code {response.status_code} from API"
        except Exception as e:
            return f"Failed to connect to the leaves history API: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio")