import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    MAX_TIME_PAGE = int(os.getenv("MAX_TIME_PAGE", 300))
    MAX_THREADS = int(os.getenv("MAX_THREADS", 10))