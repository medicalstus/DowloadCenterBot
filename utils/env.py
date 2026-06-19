import os
from dotenv import load_dotenv

load_dotenv()

# bot
TOKEN = os.getenv("TOKEN")
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")

# database
DATABASE = os.getenv("DATABASE")
DBUSER = os.getenv("DBUSER")
DBPASS = os.getenv("DBPASS")

# proxy
PROXY = os.getenv("PROXY")
PROXY_ADDR = os.getenv("PROXY_ADDR")
PROXY_PORT = int(os.getenv("PROXY_PORT"))
