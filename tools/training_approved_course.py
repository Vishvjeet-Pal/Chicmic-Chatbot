import httpx

def register_training_course(mcp):

    @mcp.tool()
    async def get_training_courses(
        auth_token: str,
        index: int = 0,
        limit: int = 10,
        approved: bool | None = None
    ):
        """
        Retrieves training courses with pagination support.

        Features:
        - Supports index & limit pagination
        - Optional filtering by approval status
        - Converts estimatedTime (seconds) into hours
        - Handles both 'courseName' and 'name' fields safely

        Use when user asks about:
        - Training courses
        - Course list
        - Approved training plans
        - Learning plans
        """

        base_url = "https://erp-staging.projectlabs.in/v1/training/course"

        url = f"{base_url}?index={index}&limit={limit}"

        headers = {
            "Authorization": auth_token
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)

        if response.status_code != 200:
            return f"Error {response.status_code}: {response.text}"

        response_json = response.json()

        courses = response_json.get("data", [])
        total_count = response_json.get("count", 0)

        if not courses:
            return "No training courses found."

        formatted_output = []

        for idx, course in enumerate(courses, start=1):

            course_name = course.get("courseName") or course.get("name", "N/A")

            is_approved = course.get("approved") or course.get("isApproved", False)

            # Optional filtering
            if approved is not None and is_approved != approved:
                continue

            estimated_seconds = course.get("estimatedTime", 0)
            estimated_hours = round(estimated_seconds / 3600, 2)

            formatted_output.append(
                f"{idx}. {course_name}\n"
                f"   Approved: {'Yes' if is_approved else 'No'}\n"
                f"   Total Phases: {course.get('totalPhases', 0)}\n"
                f"   Total Topics: {course.get('noOfTopics', 0)}\n"
                f"   Estimated Time: {estimated_hours} hrs\n"
                f"   Created By: {course.get('createdByName', 'N/A')}\n"
                f"------------------------------------"
            )

        if not formatted_output:
            return "No courses matched the given filter."

        return (
            f"Total Courses (DB Count): {total_count}\n"
            f"Showing: {len(formatted_output)}\n\n"
            + "\n\n".join(formatted_output)
        )