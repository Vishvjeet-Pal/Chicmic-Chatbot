import httpx
from datetime import datetime
from utils.redis_cache import get_cached_or_search

def register_trainee_course(mcp):
        
    @mcp.tool()
    async def get_trainee_course(auth_token, request_data):
        """
        This tool provides course details of a user/trainee.

    Use this tool when the user asks about:
    - Course details 
    - Training programs assigned to the user/trainee
    - time consumed to complete task 
    - task completed by user/trainee in a course
    - Course completion status

        args:
        - auth_token
        - trainee_id
        """

        if not request_data.get('_id'):
            return "Your user id is not found"
        
        cache_key=f"trainee_course:{request_data.get('_id','')}"

        async def search():
            COURSE_DETAILS_API_URL = f"https://api.portal.chicmicstudios.in/v1/training/dashboard/{request_data['_id']}"

            headers = {
                "Authorization": auth_token,
                "Content-Type": "application/json"
            }

            async with httpx.AsyncClient() as client:
                try:
                    response = await client.get(COURSE_DETAILS_API_URL, headers=headers)
                    data = response.json().get("data", {})

                # Helper to convert seconds → HH:MM format
                    def format_seconds(seconds):
                        if not seconds:
                            return "00:00"
                        hours = seconds // 3600
                        minutes = (seconds % 3600) // 60
                        return f"{hours:02}:{minutes:02}"

                    # Build Course Summary
                    course_section = "\n\n".join([
                    f"Course Name: '{course.get('name')}'\n"
                        f"Your progress in this course is: {course.get('progress')}%\n"
                        f"Time Consumed by you in course {course.get('name')} is {format_seconds(course.get('consumedTime'))}\n"
                        f"Estimated Time/Total time to complete the course '{course.get('name')}' is {format_seconds(course.get('estimatedTime'))}\n"
                        f"Completed course Tasks: {course.get('completedTasks')}\n"
                    for course in data.get("courses", [])
                    ])

                    plan_section = "\n\n".join([
                        f"(Your course name is : '{plan.get('name')}'\n"
                        f"Task assigned to you in course '{plan.get('name')}' is '{plan.get('taskName')}'\n"
                            f"Date of course '{plan.get('name')}' having task '{plan.get('taskName')}' is {datetime.fromisoformat(plan.get('date').replace('Z', '+00:00')).strftime('%d %B %Y') if plan.get('date') else 'N/A'}\n"
                            f"Subtasks: {', '.join(plan.get('subtasks', []))}\n"
                            # f"Task Time Consumed by you till now: {format_seconds(plan.get('consumedTime'))}\n"
                            # f"Estimated Time/Total time to complete the task '{plan.get('taskName')}': {format_seconds(plan.get('estimatedTime'))}\n"
                            f"Completed Tasks in this Course/Plan: {plan.get('completedTasks')}\n"
                            f"Extra time taken to complete this task: {plan.get('extraConsumedTime')}"
                            f"Is this course/task Completed: {'Yes' if plan.get('isCompleted') else 'No'})\n"
                        for plan in data.get("plan", [])
                    ])
                    return f"{course_section}\n\n{plan_section}"
                        
                except Exception as e:
                    return f"Error while connecting to trainee course API: {str(e)}"
        return await get_cached_or_search(cache_key, search,ttl=1800)        