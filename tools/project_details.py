import httpx

def register_project(mcp):
    @mcp.tool()
    async def get_project_details(auth_token, request_data, billing_type):
        """
    Use this tool when user asks about:
    - project overview
    - project status
    - tasks
    - billing
    - tracker details
    - PM time
    - milestone
    - Teams allocated/assigned to the projects

    args:
    - auth_token: provided in the header of the request
    - request_data: provided in request body
    - billing_type: [1,2] if user asks about hourly projects take its value as '1'. If user asks about fixed projects take its value as '2'. Do Not take any other value except 1 or 2. If neither fixed nor hourly is mentioned, take the value as '2'. 
    """

        PROJECT_API_URL = "https://api.portal.chicmicstudios.in/v1/project/list"

        headers = {
        "Authorization": auth_token,
        "Content-Type": "application/json"
        }


        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(PROJECT_API_URL, headers=headers, json={"billingType":billing_type})

                if response.status_code == 401:
                    return "Unauthorized access. Please login again."

                if response.status_code == 403:
                    return "You are not authorized to access this information."

                if response.status_code != 200:
                    return f"Error: Received {response.status_code} from API."

                project_list = response.json()["data"]["projectList"]
                if not project_list:
                    return "You are not assigned any projects"
            # return project_list
                return "\n\n".join([
                f"Project name: {project.get('name')}\n"
                f"Project Description: {project.get('description')}\n"
                f"Starting date of the project: {project.get('startDate')}\n"
                f"Ending date of the project: {project.get('endDate')}\n"
                f"Project approval status: {'Pending' if project.get('approvalStatus')==1 else 'Approved'}"
                f"Tech stack used in the project: {[p.get('name') for p in project.get('projectTechStack')]}\n"
                f"Allocated Employees: {[employee.get('userName') for employee in project.get('allocatedEmployees')]}\n"
                f"Project Manager: {project.get('primaryProjectManagers').get('userName')}\n"
                f"Teams Allocated to project {project.get('name')} are: {[team_members.get('teamId','')[0].get('name') for team_members in project.get('originalTeamHours','')]}"
                # f"Trackers allocated: {[trackers.get('userName') for trackers in project.get('allocatedTrackers').get('allocatedUsers')]}\n"
                f"Client Name: {project.get('clientName')}\n"
                f"Client Company: {project.get('clientCompany')}\n"
                f"Task of the project {project.get('name')}: {[task.get('taskName') for task in project.get('defaultTask')]}\n"
                for project in project_list
                ])
            except Exception as e:
                return f"Error while connecting to project API: {str(e)}"