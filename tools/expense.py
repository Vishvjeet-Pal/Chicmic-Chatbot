import httpx
from datetime import datetime

def register_expense_tool(mcp):

    @mcp.tool()
    async def get_expense_records(auth_token, request_data):
        """
        Use this tool when the user asks about:

        - Expense details
        - Vendor name
        - Expense amount
        - Fuel / Petrol / Diesel expenses
        - Expense by date
        - Expense by category
        - Expense history

        args:
        - auth_token
        - request_data
        """
        EXPENSE_API_URL = "https://erp-staging.projectlabs.in/v1/hrExpense/list"
        headers = {
            "Authorization": auth_token,
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    EXPENSE_API_URL,
                    headers=headers,
                    json=request_data
                )

                expense_data = response.json()["data"]["data"]

                if not expense_data:
                    return "No expense records found."

                return "\n\n".join([
                    f"Vendor Name is : {expense.get('vendorName')}\n"
                    f"Expense Date: {datetime.fromisoformat(expense.get('date').replace('Z', '+00:00')).strftime('%d %B %Y')}\n"
                    f"Total Amount of expense : ₹{expense.get('amount')} on "
                    f"Category: {expense.get('categoryData')[0].get('name') if expense.get('categoryData') else 'N/A'}\n"
                    f"Created By: {expense.get('employeeName')}\n"
                    for expense in expense_data
                ])

            except Exception as e:
                return f"Error while connecting to expense API: {str(e)}"
