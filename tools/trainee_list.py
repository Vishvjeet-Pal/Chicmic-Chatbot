import httpx

def register_training_trainee_list(mcp):

    @mcp.tool()
    async def get_training_trainee_list(
        auth_token: str,
        limit: int = 10,
        status: int | None = None,
        trainee_name: str | None = None,
        mentor_name: str | None = None
    ):
        """
        Retrieves Training Trainee List (All Pages) with optional filtering.

        Features:
        - Automatic pagination using while loop
        - Optional filtering by:
            • status (int)
            • trainee name (partial match)
            • mentor name (partial match)
        - Formats plan & mentor names cleanly

        Use when user asks about:
        - Training list
        - Trainees list
        - Who is under training
        - Training status
        """

        base_url = "https://erp-staging.projectlabs.in/v1/training/traineeList"
        index = 0
        all_trainees = []
        total_count = None

        headers = {
            "Authorization": auth_token
        }

        async with httpx.AsyncClient(timeout=30.0) as client:

            while True:
                url = f"{base_url}?index={index}&limit={limit}"
                response = await client.get(url, headers=headers)

                if response.status_code != 200:
                    return f"Error {response.status_code}: {response.text}"

                response_json = response.json()
                trainees = response_json.get("data", [])
                total_count = response_json.get("count", 0)

                if not trainees:
                    break

                all_trainees.extend(trainees)
                index += limit

                if len(all_trainees) >= total_count:
                    break

        if not all_trainees:
            return "No trainees found."

        # Apply filters & format output
        formatted_output = []
        for idx, trainee in enumerate(all_trainees, start=1):

            # Optional Filters
            if status is not None and trainee.get("status") != status:
                continue

            if trainee_name and trainee_name.lower() not in trainee.get("name", "").lower():
                continue

            mentor_list = trainee.get("mentor", [])
            mentor_names = ", ".join([m.get("name", "") for m in mentor_list])

            if mentor_name and mentor_name.lower() not in mentor_names.lower():
                continue

            plan_list = trainee.get("plan", [])
            plan_names = ", ".join([p.get("name", "") for p in plan_list])

            formatted_output.append(
                f"{idx}. {trainee.get('name', 'N/A')}\n"
                f"   Employee Code: {trainee.get('employeeCode', 'N/A')}\n"
                f"   Plan: {plan_names if plan_names else 'N/A'}\n"
                f"   Mentor(s): {mentor_names if mentor_names else 'N/A'}\n"
                f"   Status: {trainee.get('status', 'N/A')}\n"
                f"   Rating: {trainee.get('rating', 0)}\n"
                f"   Start Date: {trainee.get('startDate', 'N/A')}\n"
                f"------------------------------------"
            )

        if not formatted_output:
            return "No trainees matched the given filter."

        return (
            f"Total Trainees (DB Count): {total_count}\n"
            f"Showing: {len(formatted_output)}\n\n"
            + "\n\n".join(formatted_output)
        )