import httpx

def register_training_feedback_history(mcp):

    @mcp.tool()
    async def get_training_feedback_history(
        auth_token: str,
        index: int = 0,
        limit: int = 10
    ):
        """
Fetches training feedback history from ERP.

Use for queries about: trainee feedback, reviewer feedback, rating history, behavior feedback, or training evaluations.

Params:
- auth_token (required)
- index (optional, pagination)
- limit (optional, pagination)

Returns reviewer/trainee details, ratings, comments, created date, total count, and overall average rating.
"""

        url = f"https://erp-staging.projectlabs.in/v1/training/feedback?index={index}&limit={limit}"

        headers = {
            "Authorization": auth_token
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers)

        if response.status_code != 200:
            return f"Failed to fetch feedback history. Status Code: {response.status_code}"

        result = response.json()

        if not result.get("success"):
            return "API returned unsuccessful response."

        feedbacks = result.get("data", [])
        total_count = result.get("count", 0)
        overall_rating = result.get("overallRating", 0)

        if not feedbacks:
            return "No feedback history found."

        formatted_response = []

        for idx, fb in enumerate(feedbacks, start=1):

            reviewer = fb.get("reviewer", {})
            trainee = fb.get("trainee", {})
            feedback_type = fb.get("feedbackType", {})

            reviewer_name = reviewer.get("name", "N/A")
            reviewer_team = reviewer.get("teamName", "N/A")
            reviewer_code = reviewer.get("empCode", "N/A")

            trainee_name = trainee.get("name", "N/A")
            trainee_team = trainee.get("teamName", "N/A")
            trainee_code = trainee.get("empCode", "N/A")

            feedback_type_name = feedback_type.get("name", "N/A")

            rating = fb.get("rating", 0)
            attitude_rating = fb.get("attitudeRating", 0)
            team_spirit_rating = fb.get("teamSpiritRating", 0)

            comment = fb.get("comment", "N/A")
            created_on = fb.get("createdOn", "N/A")

            formatted_response.append(
                f"{idx}. Reviewer: {reviewer_name} ({reviewer_code})\n"
                f"   Team: {reviewer_team}\n"
                f"   Trainee: {trainee_name} ({trainee_code})\n"
                f"   Team: {trainee_team}\n"
                f"   Feedback Type: {feedback_type_name}\n"
                f"   Rating: {rating}\n"
                f"   Attitude Rating: {attitude_rating}\n"
                f"   Team Spirit Rating: {team_spirit_rating}\n"
                f"   Comment: {comment}\n"
                f"   Created On: {created_on}\n"
                f"{'-'*45}"
            )

        return (
            f"Total Feedback Records: {total_count}\n"
            f"Overall Average Rating: {overall_rating}\n\n"
            + "\n".join(formatted_response)
        )