import httpx

def register_training_test_list(mcp):

    @mcp.tool()
    async def get_training_test_list(
        auth_token: str,
        index: int = 0,
        limit: int = 10
    ):
        """
Fetches training test list with milestones, tasks, and subtasks.

Use for queries about: training tests, available tests, milestones, tasks, approval status, or estimated time.

Params:
- auth_token (required)
- index (optional, pagination)
- limit (optional, pagination)

Returns test details including name, approval status, creator, milestone/topic count, estimated time, and full milestone-task-subtask structure.
"""

        url = f"https://erp-staging.projectlabs.in/v1/training/test?index={index}&limit={limit}"

        headers = {
            "Authorization": auth_token
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers)

        if response.status_code != 200:
            return f"Failed to fetch test list. Status Code: {response.status_code}"

        result = response.json()

        if not result.get("success"):
            return "API returned unsuccessful response."

        tests = result.get("data", [])
        total_count = result.get("count", 0)

        if not tests:
            return "No training tests found."

        formatted_response = []

        for test in tests:
            test_name = test.get("testName", "N/A")
            approved = test.get("approved", False)
            created_by = test.get("createdByName", "N/A")
            total_milestones = test.get("totalMilestones", 0)
            total_topics = test.get("noOfTopics", 0)
            estimated_time = test.get("estimatedTime", 0)

            milestone_details = []
            for milestone in test.get("milestones", []):
                milestone_name = milestone.get("name", "N/A")
                milestone_time = milestone.get("estimatedTime", "N/A")

                task_details = []
                for task in milestone.get("tasks", []):
                    task_name = task.get("mainTask", "N/A")
                    task_time = task.get("estimatedTime", "N/A")

                    subtask_details = []
                    for sub in task.get("subtasks", []):
                        sub_name = sub.get("subTask", "N/A")
                        sub_time = sub.get("estimatedTime", "N/A")

                        subtask_details.append(
                            f"        Subtask: {sub_name} ({sub_time})"
                        )

                    task_details.append(
                        f"    Task: {task_name} ({task_time})\n" +
                        "\n".join(subtask_details)
                    )

                milestone_details.append(
                    f"  Milestone: {milestone_name} ({milestone_time})\n" +
                    "\n".join(task_details)
                )

            formatted_response.append(
                f"Test Name: {test_name}\n"
                f"Approved: {approved}\n"
                f"Created By: {created_by}\n"
                f"Total Milestones: {total_milestones}\n"
                f"Total Topics: {total_topics}\n"
                f"Estimated Time (seconds): {estimated_time}\n"
                f"{'-'*40}\n" +
                "\n".join(milestone_details) +
                f"\n{'='*50}\n"
            )

        return (
            f"Total Tests: {total_count}\n\n" +
            "\n".join(formatted_response)
        )