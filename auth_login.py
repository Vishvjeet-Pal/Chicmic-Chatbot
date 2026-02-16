import requests

LOGIN_URL = "https://api.portal.chicmicstudios.in/v1/auth/login"
# REFRESH_URL = "https://api.example.com/refresh"
# DATA_URL = "https://api.example.com/data"

EMAIL = "CMS/2026/820"
PASSWORD = "123456"

access_token = None
# refresh_token = None


def login():
    global access_token
    res = requests.post(LOGIN_URL, json={
        "loginId": EMAIL,
        "password": PASSWORD
    })

    print("Status:", res.status_code)
    # print("Headers:", res.headers.get("content-type"))
    # print("Raw response:", res.text) 

    data = res.json()
    data=dict(data)
    # print("data :",data.keys())
    print(data["data"]['accessToken'])
    # refresh_token = data["refresh_token"]
    print("✅ Logged in")

if __name__=="__main__":
    login()