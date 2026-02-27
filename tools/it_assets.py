import httpx

def register_asset_list(mcp):
    @mcp.tool()
    async def asset_list(auth_token, asset_name="", brand="", employee_name="", request_status="", asset_status=""):
        """
Fetches organization asset list.

Use for queries about: asset inventory, assigned assets, laptop/hardware allocation, asset requests, or assets by brand/employee/status.

Filters supported:
- asset_name, brand, employee_name
- request_status (Pending/Approved/Rejected)
- asset_status (Active/Assigned/Inactive/Retired)

Param: auth_token (required), others optional.
"""

        ASSET_LIST_API_URL = "https://erp-staging.projectlabs.in/v1/asset/list"

        headers = {
            "Authorization": auth_token,
            "Content-Type": "application/json"
        }

        index = 0
        limit = 10
        all_assets = []

        async with httpx.AsyncClient() as client:
            try:
                while True:
                    response = await client.get(
                        ASSET_LIST_API_URL,
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
                    asset_batch = response_json.get("data", {}).get("items", [])

                    if not asset_batch:
                        break

                    all_assets.extend(asset_batch)
                    index += 10

                if not all_assets:
                    return "No assets found."

                STATUS_MAP = {
                    1: "Active",
                    2: "Assigned",
                    3: "Inactive",
                    4: "Retired"
                }

                REQUEST_STATUS_MAP = {
                    1: "Pending",
                    2: "Approved",
                    3: "Rejected"
                }

                formatted_assets = []

                for asset in all_assets:

                    # Filtering
                    if asset_name and asset_name.lower() not in (asset.get("assetName") or "").lower():
                        continue

                    if brand and brand.lower() not in (asset.get("brand") or "").lower():
                        continue

                    user_data = asset.get("userData") or {}
                    request_data = asset.get("userRequestedData") or {}

                    if employee_name and employee_name.lower() not in (user_data.get("name") or "").lower():
                        continue

                    if request_status:
                        mapped_request_status = REQUEST_STATUS_MAP.get(request_data.get("requestStatus"))
                        if not mapped_request_status or request_status.lower() != mapped_request_status.lower():
                            continue

                    if asset_status:
                        mapped_status = STATUS_MAP.get(asset.get("assetStatus"))
                        if not mapped_status or asset_status.lower() != mapped_status.lower():
                            continue

                    storage_details = ", ".join(
                        [f"{s.get('capacity')} ({s.get('type')})" for s in asset.get("storage", [])]
                    )

                    formatted_assets.append(
                        f"Asset Name: {asset.get('assetName')}\n"
                        f"Brand: {asset.get('brand')}\n"
                        f"Serial Number: {asset.get('serialNumber')}\n"
                        f"RAM: {asset.get('ram')}\n"
                        f"Storage: {storage_details}\n"
                        f"MAC Address: {asset.get('macAddress')}\n"
                        f"Screen Size: {asset.get('screenSize')}\n"
                        f"Graphics: {asset.get('graphics')}\n"
                        f"Adaptor: {asset.get('adaptor')}\n"
                        f"IMEI1: {asset.get('imei1')}\n"
                        f"IMEI2: {asset.get('imei2')}\n"
                        f"Model Number: {asset.get('modelNumber')}\n"
                        f"Asset Status: {STATUS_MAP.get(asset.get('assetStatus'), 'Unknown')}\n"
                        f"Assigned To: {user_data.get('name')}\n"
                        f"Assigned Employee ID: {user_data.get('employeeId')}\n"
                        f"Requested By: {request_data.get('name')}\n"
                        f"Request Status: {REQUEST_STATUS_MAP.get(request_data.get('requestStatus'), 'N/A')}\n"
                        f"Created At: {asset.get('createdAt')}\n"
                    )

                if not formatted_assets:
                    return "No assets found."

                return "\n\n".join(formatted_assets)

            except httpx.RequestError as e:
                return f"An error occurred while requesting the API: {str(e)}"