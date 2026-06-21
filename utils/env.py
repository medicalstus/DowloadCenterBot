import os
from dotenv import load_dotenv

load_dotenv()

# bot (kept inside the bot itself)
TOKEN = os.getenv("TOKEN")
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")

# medical_website backend API (replaces the old MySQL database)
API_BASE_URL = os.getenv("API_BASE_URL", "https://apiwebsite.medicalstus.ir/api")
API_KEY = os.getenv("API_KEY", "")

# proxy
PROXY = os.getenv("PROXY", "0")
PROXY_ADDR = os.getenv("PROXY_ADDR", "127.0.0.1")
PROXY_PORT = int(os.getenv("PROXY_PORT", "10808"))
