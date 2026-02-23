import httpx
import re
from datetime import datetime
from difflib import get_close_matches
from utils.redis_cache import get_cached_or_search
from utils.format_date import normalize_date


def register_user_leaves(mcp):

    @mcp.tool()
    async def get_user_leaves(
        auth_token,
        request_data,
        leave_type="",
        leave_reason="",
        date=""
    ):
        """ 
        This tool provides details / history of leaves taken by the user. 
        STRICT RULES:
        - DO NOT call this tool if user asks about attendance or present/absent status
        - DO NOT call this tool if user asks about LEAVE DEDUCTION
        It describes: 
        - applied date of leave 
        - leave duration 
        - leave status 
        - leave reason 
        - leave send to 
        - total leaves taken DO NOT use this tool if user asks about LEAVE BALANCE 
        args: 
        - auth_token: provided in header of request 
        - leave_type: [casual leave, sick leave]. DO NOT take any other value for this argument. 
        - leave_reason: [Exams, Urgent work, emergency, marriage, other]. DO NOT take any other value for this argument. 
        - date
        - request_data: request body 
        """
        if not request_data.get('_id'):
            return "Your user id is not found"

        # cache_key = f"user_leaves:{request_data.get('_id','')}"

        def clean(text) -> str:
            return re.sub(r"\s+", " ", text.strip().lower())

        LEAVE_TYPE_MAP = {
            "sick leave": "Sick Leave",
            "sick leaves": "Sick Leave",
            "casual leave": "Casual Leave",
            "casual leaves": "Casual Leave",
            "exam": "EXAMS",
            "exams": "EXAMS",
            "urgent work": "Urgent work",
            "emergency": "emergency",
            "marriage": "marriage",
            "other": "other",
            "full day": "Full day",
            "half day": "Half day",
            "half day first half": "Half day",
            "half day second half": "Half day",
            "first half": "Half day",
            "second half": "Half day",
            "short leave": "Short leave",
            "full + half day": "Full + Half day",
            "full and half day": "Full + Half day",
        }

        display_date_short = "today"

        try:
                final_date = normalize_date(date or request_data.get("date"))
        except Exception:
                return "Invalid date provided. Please use format like '19 Feb' or '19-02-2026'."

        if final_date:
                dt = datetime.strptime(final_date, "%d-%m-%Y")
                display_date_full = dt.strftime("%d %b %Y")   
                display_date_short = dt.strftime("%d %b")

        # LEAVE_REASON_MAP = {
        #     "exam": "EXAMS",
        #     "exams": "EXAMS",
        #     "urgent work": "Urgent work",
        #     "emergency": "emergency",
        #     "marriage": "marriage",
        #     "other": "other",
        # }

        # LEAVE_CATEGORY_MAP = {
        #     "full day": "Full day",
        #     "half day": "Half day",
        #     "half day first half": "Half day",
        #     "half day second half": "Half day",
        #     "first half": "Half day",
        #     "second half": "Half day",
        #     "short leave": "Short leave",
        #     "full + half day": "Full + Half day",
        #     "full and half day": "Full + Half day",
        # }

        def normalize(value, mapping: dict):
            if not value:
                return ""
            value = clean(value)

            if value in mapping:
                return mapping[value]

            # Fuzzy fallback
            match = get_close_matches(value, mapping.keys(), n=1, cutoff=0.7)
            return mapping[match[0]] if match else value

        # async def search():

        USER_LEAVES_API = "https://api.portal.chicmicstudios.in/v1/leave/history"

        headers = {
            "authorization": auth_token,
            "content-type": "application/json"
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    USER_LEAVES_API,
                    headers=headers,
                    json={"userId": request_data['_id']}
                )

                if response.status_code != 200:
                    return f"Error: Received status code {response.status_code} from API"

                data = response.json()['data']['data']

                normalized_type = normalize(leave_type, LEAVE_TYPE_MAP)
                normalized_reason = normalize(leave_reason, LEAVE_TYPE_MAP)

                matched_leaves = []

                for leave in data:

                    api_type = leave.get("leaveType", "")
                    api_reason = leave.get("leaveReasonName", "")
                    api_category = leave.get("leaveCategory", "")

                    if (
                        (normalized_type and (api_type == normalized_type or api_reason == normalized_type or api_category==normalized_type or (normalized_type.lower() in leave.get('reason','').lower()) or (leave.get('reason','').lower() in normalized_type.lower())))
                        or (normalized_reason and (api_reason == normalized_reason or api_category==normalized_reason or api_type==normalized_reason or (normalized_reason.lower() in leave.get('reason','').lower()) or (leave.get('reason','').lower() in normalized_reason.lower())))
                        or (date and datetime.strptime(leave.get('fromDate'), '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%d-%m-%Y') == final_date)
                    ):
                        if leave not in matched_leaves:
                            matched_leaves.append(leave)

                final_leaves = matched_leaves if matched_leaves else data

                if not final_leaves:
                    return "No leave records found."

                return "\n\n".join([
                    f"(Leave Reason/Comment: {leave.get('reason','Not mentioned')}\n"
                    f"Date: {leave.get('fromDate')} to {leave.get('toDate')}\n"
                    f"The leave is taken in "
                    f"{datetime.strptime(leave.get('fromDate'), '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%B')} month\n"
                    f"Status: {'Pending' if leave.get('status')==1 else 'Approved'}\n"
                    f"Leave application is sent to "
                    f"{[manager.get('name') for manager in leave.get('sendTo')]}\n"
                    f"Duration of the leave is {leave.get('totalDays')}\n"
                    f"Leave Type: {leave.get('leaveType')} -> {leave.get('leaveReasonName')}\n"
                    f"Is sandwich applied on this leave: "
                    f"{'Yes' if leave.get('isSandwichApplied') else 'No'})\n"
                    for leave in final_leaves
                ])

            except Exception as e:
                return f"Failed to connect to the leaves history API: {str(e)}"

        # return await get_cached_or_search(cache_key, search, ttl=600)