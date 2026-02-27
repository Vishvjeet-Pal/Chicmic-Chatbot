import httpx

def register_screening_request(mcp):
    @mcp.tool()
    async def screening_request(
        auth_token,
        candidate_name="",
        email="",
        recruiter_name="",
        team="",
        designation="",
        live_status="",
        screening_status="",
        status="",
        is_experienced=""
    ):
        """
Fetches screening/interview candidate list from ERP.

Use for queries about: screening requests, interview candidates, hiring pipeline, candidate status, recruiter-wise or team-wise candidates.

Filters supported:
- candidate_name, email
- recruiter_name, team
- designation
- live_status, screening_status, final status
- is_experienced (true/false)

Param: auth_token (required).
"""

        CANDIDATE_LIST_API_URL = "https://erp-staging.projectlabs.in/v1/interview/candidate/list"

        headers = {
            "Authorization": auth_token,
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    CANDIDATE_LIST_API_URL,
                    headers=headers
                )

                if response.status_code == 401:
                    return "Unauthorized access. Please login again."

                if response.status_code == 403:
                    return "You are not authorized to access this information."

                if response.status_code != 200:
                    return f"Error: Received {response.status_code} from API."

                response_json = response.json()
                candidate_data = response_json.get("data", {}).get("interviewData", [])

                if not candidate_data:
                    return "No candidates found."

                formatted_candidates = []

                for candidate in candidate_data:

                    # Filtering
                    if candidate_name and candidate_name.lower() not in (candidate.get("name") or "").lower():
                        continue

                    if email and email.lower() not in (candidate.get("email") or "").lower():
                        continue

                    if recruiter_name and recruiter_name.lower() not in (candidate.get("recruiterName") or "").lower():
                        continue

                    applied_teams = ", ".join(
                        [team_obj.get("name") for team_obj in candidate.get("appliedForTeam", [])]
                    )

                    if team and team.lower() not in applied_teams.lower():
                        continue

                    if designation and designation.lower() not in (candidate.get("designationName") or "").lower():
                        continue

                    if live_status and str(candidate.get("liveStatus")) != str(live_status):
                        continue

                    if screening_status and str(candidate.get("screeningStatus")) != str(screening_status):
                        continue

                    if status and str(candidate.get("status")) != str(status):
                        continue

                    if is_experienced and str(candidate.get("isExperienced")).lower() != is_experienced.lower():
                        continue

                    formatted_candidates.append(
                        f"Candidate Name: {candidate.get('name')}\n"
                        f"Email: {candidate.get('email')}\n"
                        f"Contact Number: {candidate.get('contactNumber')}\n"
                        f"Recruiter Name: {candidate.get('recruiterName')}\n"
                        f"Applied Team: {applied_teams}\n"
                        f"Designation: {candidate.get('designationName')}\n"
                        f"Current Salary: {candidate.get('currentSalary')}\n"
                        f"Expected Salary: {candidate.get('expectedSalary')}\n"
                        f"Total Work Experience: {candidate.get('totalWorkExperience')}\n"
                        f"Relevant Work Experience: {candidate.get('relavantWorkExperience')}\n"
                        f"Live Status: {candidate.get('liveStatus')}\n"
                        f"Screening Status: {candidate.get('screeningStatus')}\n"
                        f"Final Status: {candidate.get('status')}\n"
                        f"Experienced: {candidate.get('isExperienced')}\n"
                        f"Notice Period: {candidate.get('noticePeriod')}\n"
                        f"Expected Joining Date: {candidate.get('expectedJoiningDate')}\n"
                        f"Created At: {candidate.get('createdAt')}\n"
                        f"Updated At: {candidate.get('updatedAt')}\n"
                    )

                if not formatted_candidates:
                    return "No candidates found."

                return "\n\n".join(formatted_candidates)

            except httpx.RequestError as e:
                return f"An error occurred while requesting the API: {str(e)}"