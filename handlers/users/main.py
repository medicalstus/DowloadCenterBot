# coding=utf-8

import traceback
from asyncio import sleep
from pyrogram import filters
from pyromod.helpers import kb, ikb
from pyrogram.handlers import MessageHandler, CallbackQueryHandler 
from pyromod.exceptions.listener_timeout import ListenerTimeout

from utils import api
from utils.helpers import CmdException, send_error, log_error, buttons, check_user, write_error, chunk


# start cmd
async def start_cmd(bot, msg):
	check = await check_user(bot, msg)
	if not check:
		return
	
	if not msg.command or not msg.command[0] == "start":
		return
	
	try:
		
		ls = api.message_get("start")

		if not ls:
			await msg.reply("🤖 خوش آمدید", reply_markup=buttons(msg.from_user))
			return
		
		for user, id in ls:
			await bot.copy_message(msg.from_user.id, user, id, reply_markup=buttons(msg.from_user))
			await sleep(.2)
		
	except CmdException as e:
		await send_error(bot, msg.chat.id, e.message, buttons(msg.from_user), e.menu)
	except Exception:
		await log_error(msg.chat.id, traceback.format_exc(), buttons(msg.from_user))

# files cmd
async def files_cmd(bot, msg):
	check = await check_user(bot, msg)
	if not check:
		return
	
	try:
		
		if not api.dc_categories(0) and not api.dc_files(0):
			raise CmdException("❌ جزوه ای ثبت نشده")

		inx = 0
		top_inx = 0
		step = 0
		moves = []
		first = True
		resend = False

		categories = [v for c in api.dc_categories(inx) for v in (c["id"], c["name"])]

		while True:
			if not first:
				categories = [v for c in api.dc_categories(inx) for v in (c["id"], c["name"])]

			categories = chunk(categories, 2)
			base = []

			if inx == top_inx:
				base.append([("بستن منو", "close")])
			else:
				base.append([("بستن منو", "close"), ("بازگشت", "back")])

			for i in range(len(categories)):
				id, name = categories[i]
				base.insert(i, [(f"🔻 {name}", f"category/{id}")])

			files = [v for f in api.dc_files(inx) for v in (f["id"], f["name"], f["file_url"])]
			if files:
				files = chunk(files, 3)
				for i in range(len(files)):
					id, name, file_url = files[i]
					base.insert(i + len(categories), [(name, f"file/{id}")])
			
			if len(files) > 1:
				base.insert(-1, [("🗃️ ارسال همه جزوات", "sendallfiles")])
			
			btn = ikb(base)
			text = "📄 در لیست زیر جزوه ها و دسته ها رو مشاهده میکنید\n🔻 یک گزینه را انتخاب کنید"
			
			if first or resend:
				waiter = await msg.reply(text, reply_markup=btn)
				first = False
				resend = False
			else:
				try:
					await waiter.edit(text, reply_markup=btn)
				except:
					pass
			
			try:
				click = await waiter.wait_for_click(msg.from_user.id, timeout=60)
			except ListenerTimeout:
				await waiter.delete()
				return
			ans = click.data
			
			if ans.startswith("file/"):
				id = int(ans.split("/")[1])
				name, file_url = next((name, file_url) for fid, name, file_url in files if fid == id)

				await msg.reply_document(file_url, caption=f"📄 {name}")
				try:
					api.dc_file_increment(id)
				except:
					pass
				await waiter.delete()
				resend = True

			elif ans == "sendallfiles":
				for id, name, file_url in files:
					await msg.reply_document(file_url, caption=f"📄 {name}")
					try:
						api.dc_file_increment(id)
					except:
						pass
					await sleep(.2)
				await waiter.delete()
				resend = True
			
			elif ans.startswith("category/"):
				await click.answer()
				id = int(ans.split("/")[1])
				moves.append(inx)
				inx = id
				step += 1
			
			elif ans == "back":
				try:
					inx = moves[-1]
					moves.pop()
				except:
					inx = 0
					moves = []
				step -= 1
			
			elif ans == "close":
				await waiter.delete()
				return
		
	except CmdException as e:
		await send_error(bot, msg.chat.id, e.message, buttons(msg.from_user), e.menu)
	except Exception:
		await log_error(msg.chat.id, traceback.format_exc(), buttons(msg.from_user))

# saved msg cmd
async def saved_msg_cmd(bot, msg):
	check = await check_user(bot, msg)
	if not check:
		return
	
	try:
		
		if msg.text == "✅ رضایت های مشاوره":
			part = "satisfaction"
		elif msg.text == "📃 قبولی ها":
			part = "accepts"
		elif msg.text == "🛂 مشاوران مدیکال":
			part = "advisors"
		
		ls = api.message_get(part)

		if not ls:
			await msg.reply("❌ پیام این دستور هنوز تنظیم نشده", reply_markup=buttons(msg.from_user))
			return
		
		for user, id in ls:
			await bot.copy_message(msg.from_user.id, user, id, reply_markup=buttons(msg.from_user))
			await sleep(.2)
		
	except CmdException as e:
		await send_error(bot, msg.chat.id, e.message, buttons(msg.from_user), e.menu)
	except Exception:
		await log_error(msg.chat.id, traceback.format_exc(), buttons(msg.from_user))

# main menu cmd
async def main_menu_cmd(bot, msg):
	check = await check_user(bot, msg)
	if not check:
		return
	
	try:
		
		await msg.reply("🏛️ به منوی اصلی بازگشتید", reply_markup=buttons(msg.from_user))
		
	except CmdException as e:
		await send_error(bot, msg.chat.id, e.message, buttons(msg.from_user), e.menu)
	except Exception:
		await log_error(msg.chat.id, traceback.format_exc(), buttons(msg.from_user))

# check force
async def check_force_button(bot, call):
	
	try:
		
		channels = api.channel_ids()
		if channels:
			joined = True
			
			for chl in channels:
				try:
					await bot.get_chat_member(chl, call.from_user.id)
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
				await bot.send_message(call.from_user.id, '📌 برای استفاده از ربات، ابتدا باید در کانال های زیر عضو شوید\n\n🔻 سپس بر روی دکمه ی "بررسی عضویت" کلیک کنید', reply_markup=btn)
				
				return
		
		await call.message.delete()
		text = api.text("start")
		await bot.send_message(call.from_user.id, text, reply_markup=buttons(call.from_user))
		
	except:
		write_error(None, traceback.format_exc())


# register
def register_usersMain(bot):
	bot.add_handler(MessageHandler(start_cmd, filters.command("start") & filters.private))
	bot.add_handler(MessageHandler(files_cmd, filters.regex("^🗃️ جزوه ها$") & filters.private))
	bot.add_handler(MessageHandler(saved_msg_cmd, filters.regex("^(🛂 مشاوران مدیکال|📃 قبولی ها|✅ رضایت های مشاوره)$") & filters.private))
	bot.add_handler(MessageHandler(main_menu_cmd, filters.regex("^(🔙 منو اصلی|انصراف)$") & filters.private))
	
	bot.add_handler(CallbackQueryHandler(check_force_button, filters.regex("^check_force$")))
