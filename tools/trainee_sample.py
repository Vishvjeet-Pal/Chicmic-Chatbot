import httpx

def register_training_sample_code(mcp):

    @mcp.tool()
    async def get_training_sample_code(
        auth_token: str,
        index: int = 0,
        limit: int = 10
    ):
        """
Fetches training GitHub sample code list from ERP.

Use for queries about: training sample code, sample projects, GitHub repositories, or approved/pending training code.

Params:
- auth_token (required)
- index (optional, pagination)
- limit (optional, pagination)

Returns project name, URL, comment, approval status, created date, and total count.
"""

        url = f"https://erp-staging.projectlabs.in/v1/training/githubSample?index={index}&limit={limit}"

        headers = {
            "Authorization": auth_token
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers)

        if response.status_code != 200:
            return f"Failed to fetch sample code list. Status Code: {response.status_code}"

        result = response.json()

        if not result.get("success"):
            return "API returned unsuccessful response."

        samples = result.get("data", [])
        total_count = result.get("count", 0)

        if not samples:
            return "No Github sample code found."

        formatted_response = []

        for idx, sample in enumerate(samples, start=1):
            project_name = sample.get("projectName", "N/A")
            url_link = sample.get("url", "N/A")
            comment = sample.get("comment", "N/A")
            approved = sample.get("approved", False)
            created_at = sample.get("createdAt", "N/A")

            formatted_response.append(
                f"{idx}. Project Name: {project_name}\n"
                f"   URL: {url_link}\n"
                f"   Comment: {comment}\n"
                f"   Approved: {approved}\n"
                f"   Created At: {created_at}\n"
                f"{'-'*40}"
            )

        return (
            f"Total Sample Codes: {total_count}\n\n" +
            "\n".join(formatted_response)
        )