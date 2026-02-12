import os
from dotenv import load_dotenv

load_dotenv()

class Setting:
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    REDIS_HOST = os.getenv("REDIS_HOST")
    REDIS_PORT = os.getenv("REDIS_PORT")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    LOGIN_URL = os.getenv("LOGIN_URL")
    POLICY_URL = os.getenv("POLICY_URL")
    LEAVE_URL = os.getenv("LEAVE_URL")
    HOLIDAY_URL = os.getenv("HOLIDAY_URL")
    USERNAME = os.getenv("MY_USERNAME")
    PASSWORD = os.getenv("PASSWORD")
    LEAVE_CALCULATION_URL= os.getenv("LEAVE_CALCULATION_URL")


settings=Setting()
