import httpx

def register_user_assets(mcp):
    @mcp.tool()
    async def user_assets(auth_token, asset_name="", brand="", asset_status="", verified=""):
        """  
        This tool retrieves user asset records from the ERP system.

Use this tool when the user asks about:
- User assets
- Company assets
- Asset list
- Assigned assets
- Hardware inventory
- Devices assigned to users
- Asset details by name or brand
- Verified or unverified assets

The tool returns formatted asset data containing:

- Asset Name
- Brand
- Serial Number
- Processor
- RAM
- Storage
- Operating System
- Graphics
- Screen Size
- Adaptor
- IMEI1
- IMEI2
- MAC Address
- Verified Status
- Asset Status
- Created At
- Updated At

        args:
        - auth_token: The authentication token for API access. Provided in the Authorization header.
        - asset_name: (Optional) Filter by asset name.
        - brand: (Optional) Filter by brand name.
        - asset_status: (Optional) Filter by asset status (active, inactive, assigned, unassigned).
        - verified: (Optional) Filter by verification status (true/false).
        """

        ASSET_API_URL = "https://erp-staging.projectlabs.in/v1/user/assets"

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
                        ASSET_API_URL,
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

                # Status mapping (adjustable based on backend meaning)
                STATUS_MAP = {
                    1: "Active",
                    2: "Assigned",
                    3: "Inactive",
                    4: "Retired"
                }

                formatted_assets = []

                for asset in all_assets:

                    # Filtering
                    if asset_name and asset_name.lower() not in (asset.get("name") or "").lower():
                        continue

                    if brand and brand.lower() not in (asset.get("brand") or "").lower():
                        continue

                    if verified:
                        if str(asset.get("verified")).lower() != verified.lower():
                            continue

                    if asset_status:
                        mapped_status = STATUS_MAP.get(asset.get("assetStatus"), "Unknown")
                        if asset_status.lower() != mapped_status.lower():
                            continue

                    storage_details = ", ".join(
                        [f"{s.get('capacity')} ({s.get('type')})" for s in asset.get("storage", [])]
                    )

                    formatted_assets.append(
                        f"Asset Name: {asset.get('name')}\n"
                        f"Brand: {asset.get('brand')}\n"
                        f"Serial Number: {asset.get('serialNumber')}\n"
                        f"Processor: {asset.get('processor')}\n"
                        f"RAM: {asset.get('ram')}\n"
                        f"Storage: {storage_details}\n"
                        f"Operating System: {asset.get('osVersion')}\n"
                        f"Graphics: {asset.get('graphics')}\n"
                        f"Screen Size: {asset.get('screenSize')}\n"
                        f"Adaptor: {asset.get('adaptor')}\n"
                        f"IMEI1: {asset.get('imei1')}\n"
                        f"IMEI2: {asset.get('imei2')}\n"
                        f"MAC Address: {asset.get('macAddress')}\n"
                        f"Verified Status: {asset.get('verified')}\n"
                        f"Asset Status: {STATUS_MAP.get(asset.get('assetStatus'), 'Unknown')}\n"
                        f"Created At: {asset.get('createdAt')}\n"
                        f"Updated At: {asset.get('updatedAt')}\n"
                    )

                if not formatted_assets:
                    return "No assets found."

                return "\n\n".join(formatted_assets)

            except httpx.RequestError as e:
                return f"An error occurred while requesting the API: {str(e)}"