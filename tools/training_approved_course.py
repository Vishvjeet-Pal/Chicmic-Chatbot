import httpx

def register_training_course(mcp):

    @mcp.tool()
    async def get_training_courses(
        auth_token: str,
        limit: int = 10,
        approved: bool | None = None
    ):
        """
        Retrieves ALL training courses using automatic pagination.

        Features:
        - Automatic pagination (while loop)
        - Optional filtering by approval status
        - Converts estimatedTime (seconds) into hours
        - Handles both 'courseName' and 'name' fields safely
        """

        base_url = "https://erp-staging.projectlabs.in/v1/training/course"

        headers = {
            "Authorization": auth_token
        }

        index = 0
        all_courses = []

        async with httpx.AsyncClient() as client:
            try:
                # 🔁 Automatic Pagination
                while True:

                    url = f"{base_url}?index={index}&limit={limit}"

                    response = await client.get(url, headers=headers)

                    if response.status_code == 401:
                        return "Unauthorized access. Please login again."

                    if response.status_code == 403:
                        return "You are not authorized to access this information."

                    if response.status_code != 200:
                        return f"Error {response.status_code}: {response.text}"

                    response_json = response.json()
                    courses = response_json.get("data", [])

                    # 🛑 Stop when no more records
                    if not courses:
                        break

                    all_courses.extend(courses)

                    # ✅ Correct offset increment
                    index += limit

                if not all_courses:
                    return "No training courses found."

                formatted_output = []

                for idx, course in enumerate(all_courses, start=1):

                    course_name = course.get("courseName") or course.get("name", "N/A")

                    is_approved = course.get("approved")
                    if is_approved is None:
                        is_approved = course.get("isApproved", False)

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
                    f"Total Courses Fetched: {len(all_courses)}\n"
                    f"Filtered Results: {len(formatted_output)}\n\n"
                    + "\n\n".join(formatted_output)
                )

            except httpx.RequestError as e:
                return f"An error occurred while requesting the API: {str(e)}"