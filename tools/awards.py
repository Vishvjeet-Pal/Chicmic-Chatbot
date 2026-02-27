import httpx

def register_award_list(mcp):
    @mcp.tool()
    async def award_list(auth_token, award_name="", award_type="", award_status="", year="", is_eligible="", can_see_nomination=""):
        """
Fetches award list records.

Use for queries about: award list, quarterly/monthly/annual awards, award status (active/upcoming/completed/closed), nomination eligibility, nomination visibility, or awards by year.

Filters supported:
- award_name
- award_type (Quarterly/Monthly/Annual)
- award_status (Active/Upcoming/Completed/Closed)
- year
- is_eligible (true/false)
- can_see_nomination (true/false)

Params: auth_token (required), other filters optional.
"""

        AWARD_LIST_API_URL = "https://erp-staging.projectlabs.in/v1/awards/list"

        headers = {
            "Authorization": auth_token,
            "Content-Type": "application/json"
        }

        index = 0
        limit = 10
        all_awards = []

        async with httpx.AsyncClient() as client:
            try:
                while True:
                    response = await client.get(
                        AWARD_LIST_API_URL,
                        headers=headers,
                        params={"index": index, "limit": limit}
                    )

                    if response.status_code == 401:
                        return "Unauthorized access. Please login again."

                    if response.status_code == 403:
                        return "You are not authorized to access this information."

                    if response.status_code != 200:
                        return f"Error: Received {response.status_code} from API."

                    response_json = response.json()
                    award_batch = response_json.get("data", {}).get("data", [])

                    if not award_batch:
                        break

                    all_awards.extend(award_batch)
                    index += 10

                if not all_awards:
                    return "No awards found."

                AWARD_TYPE_MAP = {
                    1: "Quarterly",
                    2: "Monthly",
                    3: "Annual"
                }

                AWARD_STATUS_MAP = {
                    1: "Active",
                    2: "Upcoming",
                    3: "Completed",
                    4: "Closed"
                }

                formatted_awards = []

                for award in all_awards:

                    # Filtering
                    if award_name and award_name.lower() not in (award.get("name") or "").lower():
                        continue

                    if award_type:
                        mapped_type = AWARD_TYPE_MAP.get(award.get("awardType"))
                        if not mapped_type or award_type.lower() != mapped_type.lower():
                            continue

                    if award_status:
                        mapped_status = AWARD_STATUS_MAP.get(award.get("awardStatus"))
                        if not mapped_status or award_status.lower() != mapped_status.lower():
                            continue

                    if year and year not in (award.get("name") or ""):
                        continue

                    if is_eligible:
                        if str(award.get("isEligibleForNomination")).lower() != is_eligible.lower():
                            continue

                    if can_see_nomination:
                        if str(award.get("canSeeNomination")).lower() != can_see_nomination.lower():
                            continue

                    formatted_awards.append(
                        f"Award Name: {award.get('name')}\n"
                        f"Award Type: {AWARD_TYPE_MAP.get(award.get('awardType'), 'Unknown')}\n"
                        f"Due Date: {award.get('dueDate')}\n"
                        f"Last Due Date: {award.get('lastDueDate')}\n"
                        f"Can See Nomination: {award.get('canSeeNomination')}\n"
                        f"Eligible For Nomination: {award.get('isEligibleForNomination')}\n"
                        f"Award Status: {AWARD_STATUS_MAP.get(award.get('awardStatus'), 'Unknown')}\n"
                        f"Award ID: {award.get('awardId')}\n"
                        f"User ID: {award.get('userId')}\n"
                    )

                if not formatted_awards:
                    return "No awards found."

                return "\n\n".join(formatted_awards)

            except httpx.RequestError as e:
                return f"An error occurred while requesting the API: {str(e)}"