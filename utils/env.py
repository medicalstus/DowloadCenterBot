import os
from dotenv import load_dotenv

load_dotenv()

# bot (kept inside the bot itself)
TOKEN = os.getenv("TOKEN")
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")

# medical_website backend API (replaces the old MySQL database)
API_BASE_URL = os.getenv("API_BASE_URL", "https://apiwebsite.medicalstus.ir/api")
# Shared key the bot sends to the backend as X-Bot-Key; must equal the backend's
# key. Accept either name so the same value works whether it is set as API_KEY
# (bot side, as documented) or TGBOT_API_KEY (the backend's variable name).
API_KEY = os.getenv("API_KEY") or os.getenv("TGBOT_API_KEY", "")

# proxy
PROXY = os.getenv("PROXY", "0")
PROXY_ADDR = os.getenv("PROXY_ADDR", "127.0.0.1")
PROXY_PORT = int(os.getenv("PROXY_PORT", "10808"))
