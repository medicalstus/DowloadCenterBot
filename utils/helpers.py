# coding=utf-8

import itertools
from asyncio import sleep
from threading import Thread
from pyromod.helpers import kb, ikb, kbtn
from pyrogram.types import ReplyKeyboardMarkup
from pyromod.exceptions.listener_timeout import ListenerTimeout

from utils import api
from utils.env import PROXY


# ==============================
#         Simple Helpers
# ==============================


# CMD Exception class
class CmdException(Exception):
	def __init__(self, message="❌ خطا", menu=True):
		self.message = message
		self.menu = menu
		super().__init__(self.message, self.menu)

# thread with return
class ThreadReturn(Thread):
	def __init__(self, target, *args, **kwargs):
		super().__init__(target=target, args=args, kwargs=kwargs)
		self._return = None

	def run(self):
		self._return = self._target(*self._args, **self._kwargs)

	def join(self, timeout=None):
		super().join(timeout=timeout)
		return self._return

# chunk
def chunk(it, size):
	it = iter(it)
	return list(iter(lambda: tuple(itertools.islice(it, size)), ()))

# send error
async def send_error(bot, id, error, btn=None, menu=True):
	try:
		if type(menu) == bool:
			btn = btn if menu else None
		elif type(menu) == ReplyKeyboardMarkup:
			btn = menu
		
		await bot.send_message(id, error, reply_markup=btn)
	except:
		pass

# write error
def write_error(id, full):
	if "pymysql.err.OperationalError: (" not in full:
		if PROXY:
			print(full)
		try:
			with open('./errors.txt', 'a') as f:
				f.write(f'\n\n\nfrom id: {id} error:\n{full}\n')
		except:
			pass

# log error
async def log_error(id, full, btn=None, menu=True):
	if "pymysql.err.OperationalError: (1130," not in full:
		write_error(id, full)
		await send_error(id, full, btn, menu)


# ==============================
#          Bot Helpers
# ==============================


# is user
def isUser(user):
	ids = api.user_ids()
	if user.id in ids:
		check_username(user)
		return True
	return False

# is admin
def isAdmin(user):
	ids = api.admin_ids(['admin', 'head', 'dev'])
	if user.id in ids:
		check_username(user)
		return True
	return False

# is head
def isHead(user):
	ids = api.admin_ids(['head', 'dev'])
	if user.id in ids:
		check_username(user)
		return True
	return False

# check username
def check_username(user):
	record = api.user_get(user.id)
	username = record["username"] if record else None
	name = record["name"] if record else None

	user_name = user.first_name
	if user.last_name:
		user_name += f" {user.last_name}"

	if user.username != username or user_name != name:
		api.user_update(user.id, username=user.username, name=user_name)

# check user
async def check_user(bot, msg):
	if not isUser(msg.from_user):
		btns = kb([[kbtn("📞 ارسال شماره تلفن", request_contact=True)]], resize_keyboard=True)
		
		label = await msg.reply("📞 لطفا شماره حساب خود را از طریق دکمه زیر ارسال کنید", reply_markup=btns)
		
		try:
			ask = await bot.listen(chat_id=msg.chat.id, timeout=60)
		except ListenerTimeout:
			await label.delete()
			await msg.reply("🔻 شروع مجدد:\n/start")
			return False
		
		if not ask.contact:
			await label.delete()
			await msg.reply("🔻 شروع مجدد:\n/start")
			return False
		
		contact = ask.contact
		if contact.user_id != msg.from_user.id:
			await label.delete()
			await msg.reply("❌ باید شماره خودتان را ارسال کنید! شروع مجدد:\n/start")
			return False
		
		user_name = msg.from_user.first_name
		if msg.from_user.last_name:
			user_name += f" {msg.from_user.last_name}"
		
		api.user_add(msg.from_user.id, msg.from_user.username, user_name, contact.phone_number)

	channels = api.channel_ids()
	if channels:
		joined = True
		
		for chl in channels:
			try:
				await bot.get_chat_member(chl, msg.from_user.id)
			except:
				joined = False
				break
			await sleep(.05)
		
		if joined == False:
			base = [[("✅ بررسی عضویت", "check_force")]]
			for chl in channels:
				try:
					chat = await bot.get_chat(chl)
					base.insert(0, [(f"👉 @{chat.username}", f"https://t.me/{chat.username}", "url")])
				except:
					pass
				await sleep(.05)
			
			btn = ikb(base)
			await bot.send_message(msg.from_user.id, '📌 برای استفاده از ربات، ابتدا باید در کانال های زیر عضو شوید\n\n🔻 سپس بر روی دکمه ی "بررسی عضویت" کلیک کنید', reply_markup=btn)
			
			return False
	
	return True

# send to all admins
async def send_to_all_admins(bot, message):
	admins = api.admin_ids()
	for admin in admins:
		try:
			await bot.send_message(admin, message)
		except:
			pass
		await sleep(0.2)
	return True


# ==============================
#            Buttons
# ==============================


# get buttuns
def buttons(user):
	
	base = [
		["🗃️ جزوه ها"],
		["🛂 مشاوران مدیکال", "📃 قبولی ها", "✅ رضایت های مشاوره"]
	]
	
	if isAdmin(user):
		base.append(["🏛 پنل مدیریت"])
	
	return kb(base, resize_keyboard=True)

# admin buttons
def admin_buttons(user):
	
	base = [
		["🗃️ مدیریت جزوه ها"],
		["📊 آمار ربات", "📜 تنظیم پیام ها"],
		["📄 لیست کاربران", "🔒 جوین اجباری"],
		["🔙 منو اصلی"]
	]
	
	if isHead(user):
		base[2].append("👥 ادمین ها")
	
	return kb(base, resize_keyboard=True)
