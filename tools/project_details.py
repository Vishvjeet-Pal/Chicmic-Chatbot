import httpx

def register_project(mcp):
    @mcp.tool()
    async def get_project_details(auth_token, request_data):
        """
    Use this tool when user asks about:
    - project overview
    - project status
    - tasks
    - billing
    - tracker details
    - PM time
    - milestone

    args:
    - query
    - auth_token
    - request_data
    """

        PROJECT_API_URL = "https://erp-staging.projectlabs.in/v1/project/list"

        headers = {
        "Authorization": auth_token,
        "Content-Type": "application/json"
        }


        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(PROJECT_API_URL, headers=headers, json={"billingType":request_data['billingType']})

                if response.status_code == 401:
                    return "Unauthorized access. Please login again."

                if response.status_code == 403:
                    return "You are not authorized to access this information."

                if response.status_code != 200:
                    return f"Error: Received {response.status_code} from API."

                project_list = response.json()["data"]["projectList"]
            # return project_list
                return "\n\n".join([
                f"Project name: {project.get('name')}\n"
                f"Project Description: {project.get('description')}\n"
                f"Starting date of the project: {project.get('startDate')}\n"
                f"Ending date of the project: {project.get('endDate')}\n"
                f"Tech stack used in the project: {[p.get('name') for p in project.get('projectTechStack')]}\n"
                f"Allocated Employees: {[employee.get('userName') for employee in project.get('allocatedEmployees')]}\n"
                f"Project Manager: {project.get('primaryProjectManagers').get('userName')}\n"
                # f"Trackers allocated: {[trackers.get('userName') for trackers in project.get('allocatedTrackers').get('allocatedUsers')]}\n"
                f"Client Name: {project.get('clientName')}\n"
                f"Client Company: {project.get('clientCompany')}\n"
                f"Default Task of the project {project.get('name')}: {[task.get('taskName') for task in project.get('defaultTask')]}\n"
                for project in project_list
                ])
            except Exception as e:
                return f"Error while connecting to project API: {str(e)}"