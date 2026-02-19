import httpx
from datetime import datetime

def register_learning_tool(mcp):

    @mcp.tool()
    async def get_learning_details(auth_token):
        """
        Use this tool when the user asks about:

        - leraning and r&d Task details
        - leraning and r&d Task status
        - Assigned employees to leraning and r&d tasks
        - Employee leraning and r&d task progress
        - Pending / Completed leraning and r&d task list
        - Time spent on leraning and r&d tasks

        args:
        - auth_token
        """
        TASK_API_URL = "https://erp-staging.projectlabs.in/v1/learning/list?index=0&limit=10"
        headers = {
            "Authorization": auth_token,
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    TASK_API_URL,
                    headers=headers
                )

                task_data = response.json()["data"]["data"]

                if not task_data:
                    return "No task records found."

                formatted_tasks = []

                for task in task_data:
                    employees_info = "\n".join([
                        f"- {emp.get('name')} | Status: {emp.get('status')} | Time Spent: {emp.get('totalTimeSpent')}"
                        for emp in task.get("employeeIds", [])
                    ])

                    formatted_tasks.append(
                        f"Task Name: {task.get('taskName')}\n"
                        f"Allocated Time: {task.get('time')}\n"
                        f"Created On: {datetime.fromisoformat(task.get('createdAt').replace('Z', '+00:00')).strftime('%d %B %Y')}\n"
                        f"Created By: {task.get('createdByUserName')}\n"
                        f"Description: {task.get('description')}\n"
                        f"Assigned Employees:\n{employees_info}\n"
                        "------------------------------------"
                    )

                return "\n\n".join(formatted_tasks)

            except Exception as e:
                return f"Error while connecting to learning API: {str(e)}"
