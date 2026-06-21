# coding=utf-8

"""
Created by Cypher
ParsCoders = https://parscoders.com/resume/340299
"""


import os
import time

from pyromod import Client
from pyrogram import idle, filters
from pyrogram.errors import FloodWait

from utils import api
from utils.env import TOKEN, API_ID, API_HASH, PROXY, PROXY_ADDR, PROXY_PORT


# ==============================
#            Client
# ==============================


proxy = None
if int(PROXY):
	proxy = {
		"scheme": "socks5",
		"hostname": PROXY_ADDR,
		"port": PROXY_PORT,
	}

# Persist the pyrogram session in its own dir so a container restart does NOT
# trigger a fresh auth.ImportBotAuthorization (that is what causes FloodWait).
# Mount a persistent disk on SESSION_DIR so the session survives redeploys.
SESSION_DIR = os.getenv("SESSION_DIR", "session")
os.makedirs(SESSION_DIR, exist_ok=True)

# pyrogarm Client
bot = Client(
	"bot",
	bot_token=TOKEN,
	api_id=API_ID,
	api_hash=API_HASH,
	proxy=proxy,
	workdir=SESSION_DIR,
)


# ==============================
#         Load Commands
# ==============================


# handlers
from handlers.users.main import register_usersMain
from handlers.admins.main import register_adminsMain
from handlers.admins.set import register_adminsSet
from handlers.admins.waiter import register_waiter

# register
def register():
	# user
	register_usersMain(bot)
	
	# admin
	register_adminsMain(bot)
	register_adminsSet(bot)
	register_waiter(bot)


# ==============================
#    Call back query reserve
# ==============================


# handler
@bot.on_callback_query(filters.regex("^WONT MATCH EVER IN ANY QUERY$"))
async def on_callback():
	pass


# ==============================
#              Run
# ==============================


# Start the client, surviving FloodWait instead of crash-looping. If we let
# FloodWait bubble up, the process dies, the platform restarts it, and it
# re-tries auth right away -> the wait Telegram demands keeps growing. Waiting
# *inside* the process lets the limit expire once and then the bot comes up.
# pyrogram's start() disconnects itself before re-raising, so a plain retry is
# safe. (Sync style on purpose: this kurigram's run() takes no coroutine.)
while True:
	try:
		bot.start()
		break
	except FloodWait as e:
		wait = int(getattr(e, "value", None) or getattr(e, "x", 60)) + 5
		print(f"[start] FloodWait from Telegram: waiting {wait}s before retrying...", flush=True)
		time.sleep(wait)

me = bot.get_users("me")
api.set_username(me.username)
bot.username = me.username

register()

print(f"{'='*30}\nBot started @{me.username}\nCreated By Cypher\n{'='*30}", flush=True)

idle()
bot.stop()
