import httpx

def register_training_sample_code(mcp):

    @mcp.tool()
    async def get_training_sample_code(
        auth_token: str,
        limit: int = 10
    ):
        """
        This tool fetches Github Sample Code list from Training Module.

        Use this tool when user asks about:
        - Training sample code
        - Github sample projects
        - Sample repositories
        - Training project examples
        - Approved / pending sample codes

        Required:
        - auth_token (User authentication token)

        Optional:
        - limit (default: 10)

        Returns:
        - Project Name
        - URL
        - Comment
        - Approval status
        - Created date
        - Total records count
        """

        base_url = "https://erp-staging.projectlabs.in/v1/training/githubSample"

        headers = {
            "Authorization": auth_token
        }

        index = 0
        all_samples = []
        total_count = None

        async with httpx.AsyncClient(timeout=30.0) as client:

            while True:
                url = f"{base_url}?index={index}&limit={limit}"

                response = await client.get(url, headers=headers)

                if response.status_code != 200:
                    return f"Failed to fetch sample code list. Status Code: {response.status_code}"

                result = response.json()

                if not result.get("success"):
                    return "API returned unsuccessful response."

                samples = result.get("data", [])
                total_count = result.get("count", 0)

                if not samples:
                    break

                all_samples.extend(samples)

                index += limit

                if len(all_samples) >= total_count:
                    break

        if not all_samples:
            return "No Github sample code found."

        formatted_response = []

        for idx, sample in enumerate(all_samples, start=1):
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