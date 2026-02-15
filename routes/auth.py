import httpx

url = loginurl
credentials = {
    "loginId": login,
    "password": password
}
def login(loginId,password):
    with httpx.Client() as client:
        response = client.post(url, json=credentials)
        response=response.json()
        access_token=response['data']['accessToken']
        return access_token