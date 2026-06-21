# coding=utf-8

"""
Created by Cypher
ParsCoders = https://parscoders.com/resume/340299
"""


from pyromod import Client
from pyrogram import idle, filters

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

# pyrogarm Client
bot = Client(
	"bot",
	bot_token=TOKEN,
	api_id=API_ID,
	api_hash=API_HASH,
	proxy=proxy
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


# run bot
bot.start()

me = bot.get_users("me")
api.set_username(me.username)
bot.username = me.username

register()

print(f"{'='*30}\nBot started @{me.username}\nCreated By Cypher\n{'='*30}")

idle()
bot.stop()
