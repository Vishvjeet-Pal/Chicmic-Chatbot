import httpx

def register_recruitment_report(mcp):
    @mcp.tool()
    async def recruitment_report(auth_token, month="", recruiter_name=""):
        """
Fetches recruitment report data from ERP.

Use for queries about: monthly hiring report, recruiter performance, candidate statistics, interview results, or recruitment summary.

Filters supported:
- month
- recruiter_name

Param: auth_token (required).
"""

        RECRUITMENT_REPORT_API_URL = "https://erp-staging.projectlabs.in/v1/interview/recuritment/report"

        headers = {
            "Authorization": auth_token,
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    RECRUITMENT_REPORT_API_URL,
                    headers=headers
                )

                if response.status_code == 401:
                    return "Unauthorized access. Please login again."

                if response.status_code == 403:
                    return "You are not authorized to access this information."

                if response.status_code != 200:
                    return f"Error: Received {response.status_code} from API."

                report_data = response.json().get("data", [])

                if not report_data:
                    return "No recruitment report data found."

                formatted_reports = []

                for record in report_data:

                    # Filtering
                    if month and month.lower() not in (record.get("monthName") or "").lower():
                        continue

                    if recruiter_name and recruiter_name.lower() not in (record.get("recruiterName") or "").lower():
                        continue

                    formatted_reports.append(
                        f"Month Name: {record.get('monthName')}\n"
                        f"Recruiter Name: {record.get('recruiterName')}\n"
                        f"Total Candidates: {record.get('totalCandidates')}\n"
                        f"Offer Sent: {record.get('offerSent')}\n"
                        f"Selected Candidates: {record.get('selectedCandidates')}\n"
                        f"Rejected In Screening: {record.get('rejectedInScreening')}\n"
                        f"Selected In Interview: {record.get('selectedInInterview')}\n"
                        f"Not Responding Candidates: {record.get('notRespondingCandidates')}\n"
                    )

                if not formatted_reports:
                    return "No recruitment report data found."

                return "\n\n".join(formatted_reports)

            except httpx.RequestError as e:
                return f"An error occurred while requesting the API: {str(e)}"