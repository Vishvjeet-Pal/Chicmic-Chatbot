# import httpx
# from datetime import datetime

# def register_it_task_tool(mcp):

#     @mcp.tool()
#     async def it_task_schedule(auth_token):
#         """
#         STRICT RULES:
#         - Use this tool ONLY when the user asks about IT TASKS.
#         - NEVER use this tool if IT tasks is not mentioned in user's query.

#         Use this tool when the user asks about:
#         - Assigned IT tasks
#         - IT Task schedule
#         - IT Tasks on a specific date
#         - IT Task details
#         - Who is assigned to a IT task
#         - Time allotted for a IT task
#         - Whether timesheet exists for a IT task

#         Args:
#         - auth_token
#         """
#         it_task_url = "https://api.portal.chicmicstudios.in/v1/it/list?index=0&limit=10"
#         headers = {
#             "Authorization": auth_token,
#             "Content-Type": "application/json"
#         }

#         async with httpx.AsyncClient() as client:
#             try:
#                 response = await client.get(
#                     it_task_url,
#                     headers=headers
#                 )

#                 if response.status_code != 200:
#                     return f"API Error {response.status_code}: {response.text}"

#                 response_json = response.json()
#                 task_data = response_json.get("data", {}).get("data", [])

#                 if not task_data:
#                     return "No task records found."

#                 formatted_tasks = []

#                 for task in task_data:

#                     task_date = task.get("taskDate")
#                     formatted_task_date = (
#                         datetime.fromisoformat(task_date.replace("Z", "+00:00"))
#                         .strftime("%d %B %Y")
#                         if task_date else "N/A"
#                     )
#                     resources = ", ".join([
#                         r.get("name")
#                         for r in task.get("resources", [])
#                     ])

#                     employees = ", ".join(task.get("employeeName", []))

#                     formatted_tasks.append(
#                         f"Task Title: {task.get('title')}\n"
#                         f"Task Date: {formatted_task_date}\n"
#                         f"Time Allotted: {task.get('timeAlloted')}\n"
#                         f"Description: {task.get('description')}\n"
#                         f"Assigned Resources: {resources}\n"
#                         f"Employee Name(s): {employees}\n"
#                         f"Timesheet Added: {task.get('timesheetAdd')}\n"
#                         f"Timesheet Exists: {task.get('isTimesheetExist')}\n"
#                     )

#                 return "\n\n".join(formatted_tasks)

#             except Exception as e:
#                 return f"Error while connecting to task schedule API: {str(e)}"


import httpx
from datetime import datetime

def register_it_task_tool(mcp):

    @mcp.tool()
    async def it_task_schedule(auth_token):
        """
        STRICT RULES:
        - Use this tool ONLY when the user asks about IT TASKS.
        - NEVER use this tool if IT tasks is not mentioned in user's query.

        Fetches ALL IT task records dynamically.
        """

        base_url = "https://api.portal.chicmicstudios.in/v1/it/list"

        headers = {
            "Authorization": auth_token,
            "Content-Type": "application/json"
        }

        index = 0
        limit = 10
        all_tasks = []

        async with httpx.AsyncClient() as client:
            try:
                while True:

                    params = {
                        "index": index,
                        "limit": limit
                    }

                    response = await client.get(
                        base_url,
                        headers=headers,
                        params=params
                    )

                    if response.status_code == 401:
                        return "Unauthorized access. Please login again."

                    if response.status_code == 403:
                        return "You are not authorized to access this information."

                    if response.status_code != 200:
                        return f"API Error {response.status_code}: {response.text}"

                    response_json = response.json()
                    data_section = response_json.get("data", {})
                    task_batch = data_section.get("data", [])
                    total_count = data_section.get("totalCount", 0)

                    if not task_batch:
                        break

                    all_tasks.extend(task_batch)

                    # Stop when all records fetched
                    if len(all_tasks) >= total_count:
                        break

                    index += limit  # 🔥 increase dynamically

                if not all_tasks:
                    return "No task records found."

                formatted_tasks = []

                for task in all_tasks:

                    task_date = task.get("taskDate")

                    formatted_task_date = "N/A"
                    if task_date:
                        try:
                            formatted_task_date = (
                                datetime.fromisoformat(
                                    task_date.replace("Z", "+00:00")
                                ).strftime("%d %B %Y")
                            )
                        except:
                            pass

                    resources = ", ".join([
                        r.get("name")
                        for r in task.get("resources", [])
                        if r.get("name")
                    ])

                    employees = ", ".join(task.get("employeeName", []))

                    formatted_tasks.append(
                        f"Task Title: {task.get('title')}\n"
                        f"Task Date: {formatted_task_date}\n"
                        f"Time Allotted: {task.get('timeAlloted')}\n"
                        f"Description: {task.get('description')}\n"
                        f"Assigned Resources: {resources}\n"
                        f"Employee Name(s): {employees}\n"
                        f"Timesheet Added: {task.get('timesheetAdd')}\n"
                        f"Timesheet Exists: {task.get('isTimesheetExist')}\n"
                        f"--------------------------------------"
                    )

                return (
                    f"Total IT Tasks: {len(all_tasks)}\n\n"
                    + "\n\n".join(formatted_tasks)
                )

            except Exception as e:
                return f"Error while connecting to task schedule API: {str(e)}"