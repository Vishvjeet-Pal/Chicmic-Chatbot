import os
from dotenv import load_dotenv

load_dotenv()

class Setting:
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    REDIS_HOST = os.getenv("REDIS_HOST")
    REDIS_PORT = os.getenv("REDIS_PORT")


settings=Setting()