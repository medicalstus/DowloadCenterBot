# coding=utf-8

import traceback
from pyrogram import filters
from pyromod.helpers import kb, ikb
from pyrogram.handlers import MessageHandler
from pyromod.exceptions.listener_timeout import ListenerTimeout

from utils import api
from utils.wait import wait
from handlers.admins.main import admin_cmd
from utils.helpers import CmdException, admin_buttons, isHead, isAdmin, send_error, log_error, chunk


# admins
async def admins_list_cmd(bot, msg):
	if not isHead(msg.from_user):
		return
	
	try:
		
		btns = kb([
			["➖ حذف ادمین", "➕ ثبت ادمین"],
			["🏛 پنل مدیریت"]
		], resize_keyboard=True)
		
		await msg.reply("انتخاب کنید:", reply_markup=btns)
		
	except CmdException as e:
		await send_error(bot, msg.chat.id, e.message, admin_buttons(msg.from_user), e.menu)
	except Exception:
		await log_error(msg.chat.id, traceback.format_exc(), admin_buttons(msg.from_user))

# add admin cmd
async def add_admin_cmd(bot, msg):
	if not isHead(msg.from_user):
		return
	
	try:
		
		btns = kb([
			["➖ حذف ادمین", "➕ ثبت ادمین"],
			["🏛 پنل مدیریت"]
		], resize_keyboard=True)
		
		await msg.reply("آیدی عددی کاربر مد نظر را ارسال کنید:")
		try:
			ask = await bot.listen(chat_id=msg.chat.id, timeout=120)
		except ListenerTimeout:
			await admin_cmd(bot, msg)
			return
		id = ask.text
		
		if id == "🏛 پنل مدیریت":
			await admin_cmd(bot, msg)
			return
		
		if not id.isdigit():
			raise CmdException("❌ باید یک آیدی عددی ارسال میکردید", menu=btns)
		
		id = int(id)
		
		user = api.user_get(id)
		if not user:
			raise CmdException("❌ کاربر یافت نشد", menu=btns)

		admin = api.admin_get(id)
		if admin:
			raise CmdException("❌ کاربر در حال حاضر ادمین است", menu=btns)

		api.admin_add(id, "admin")
		
		await msg.reply("✅ اضافه شد", reply_markup=btns)
		
	except CmdException as e:
		await send_error(bot, msg.chat.id, e.message, admin_buttons(msg.from_user), e.menu)
	except Exception:
		await log_error(msg.chat.id, traceback.format_exc(), admin_buttons(msg.from_user))

# remove admin cmd
async def remove_admin_cmd(bot, msg):
	if not isHead(msg.from_user):
		return
	
	try:
		
		admins = api.admin_ids('admin')

		if admins == []:
			raise CmdException("❌ هیچ ادمینی وجود ندارد", menu=False)
		
		btn = ikb([
			[("❌ حذف ادمین", "delete")],
			[("<<", "first"), ("<", "pre"), (">", "next"), (">>", "last")],
			[("بستن منو", "close")]
		])
		
		inx = 0
		first = True
		
		while True:
			if admins == []:
				await waiter.delete()
				return
			
			id = admins[inx]
			_user = api.user_get(id)
			username = _user["username"] if _user else None
			username = f"@{username}" if username != None else "ثبت نشده"
			text = f"{inx + 1}/{len(admins)}\n👤 `{id}`\n🆔 آیدی : {username}"
			
			if first:
				waiter = await msg.reply(text, reply_markup=btn)
				first = False
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
			
			if ans == "delete":
				
				conf_btn = ikb([
					[("❌ حذف ادمین", "confdelete")],
					[("بازگشت", "back")]
				])
				
				try:
					waiter = await waiter.edit("❌ آیا از حذف کردن ادمین اطمینان دارید؟", reply_markup=conf_btn)
				except:
					pass
				
				try:
					click = await waiter.wait_for_click(msg.from_user.id, timeout=60)
				except ListenerTimeout:
					continue
				ans = click.data
				
				if ans == "confdelete":
					api.admin_delete(id)
					admins.pop(inx)
					
					if inx - 1 > 0:
						inx -= 1
					else:
						inx =  0
					
					await click.reply("✅ حذف شد")
			
			elif ans == "first":
				inx = 0
				await click.reply("⏮️ اول لیست")
			
			elif ans == "pre":
				if inx - 1 > 0:
					inx -= 1
				else:
					inx =  0
					await click.reply("⏮️ اول لیست")
			
			elif ans == "next":
				if inx + 1 < len(admins):
					inx += 1
				else:
					inx = len(admins) - 1
					await click.reply("⏭️ آخر لیست")
			
			elif ans == "last":
				inx = len(admins) - 1
				await click.reply("⏭️ آخر لیست")
			
			elif ans == "close":
				await waiter.delete()
				return
		
	except CmdException as e:
		await send_error(bot, msg.chat.id, e.message, admin_buttons(msg.from_user), e.menu)
	except Exception:
		await log_error(msg.chat.id, traceback.format_exc(), admin_buttons(msg.from_user))

# forced join
async def forced_join_menu(bot, msg):
	if not isAdmin(msg.from_user):
		return
	
	try:
		
		btns = kb([
			["➖ حذف کانال", "➕ ثبت کانال"],
			["🏛 پنل مدیریت"]
		], resize_keyboard=True)
		
		await msg.reply("انتخاب کنید:", reply_markup=btns)
		
	except CmdException as e:
		await send_error(bot, msg.chat.id, e.message, admin_buttons(msg.from_user), e.menu)
	except Exception:
		await log_error(msg.chat.id, traceback.format_exc(), admin_buttons(msg.from_user))

# add channel cmd
async def add_channel_cmd(bot, msg):
	if not isAdmin(msg.from_user):
		return
	
	try:
		
		menu = kb([
			["➖ حذف کانال", "➕ ثبت کانال"],
			["🏛 پنل مدیریت"]
		], resize_keyboard=True)
		
		btns = kb([["🏛 پنل مدیریت"]], resize_keyboard=True)
		
		await msg.reply("🔻 ابتدا ربات را به عنوان ادمین در چنل مد نظرتان اضافه کنید، سپس یک پیام از چنل فوروارد کنید:", reply_markup=btns)
		try:
			ask = await bot.listen(chat_id=msg.chat.id, timeout=120)
		except ListenerTimeout:
			await admin_cmd(bot, msg)
			return
		ans = ask.text
		
		if ask.command:
			await admin_cmd(bot, ask)
			return
		
		if ans == "🏛 پنل مدیریت":
			await admin_cmd(bot, msg)
			return
		
		if not ask.forward_from_chat or str(ask.forward_from_chat.type) != "ChatType.CHANNEL":
			raise CmdException("❌ باید یک پیام از چنل فوروارد میکردید", menu=menu)
		
		chat = ask.forward_from_chat
		
		if not chat.username:
			raise CmdException("❌ کانال ایدی ندارد", menu=menu)
		
		ls = api.channel_ids()

		if chat.id in ls:
			raise CmdException("❌ کانال از قبل اضافه شده است", menu=menu)
		
		try:
			await bot.get_chat_member(chat.id, "me")
		except:
			raise CmdException("❌ ربات به کانال اضافه نشده است", menu=menu)
		
		api.channel_add(chat.id, chat.title)
		
		await msg.reply("✅ کانال اضافه شد", reply_markup=admin_buttons(msg.from_user))
		
	except CmdException as e:
		await send_error(bot, msg.chat.id, e.message, admin_buttons(msg.from_user), e.menu)
	except Exception:
		await log_error(msg.chat.id, traceback.format_exc(), admin_buttons(msg.from_user))

# remove channel cmd
async def remove_channel_cmd(bot, msg):
	if not isAdmin(msg.from_user):
		return
	
	try:
		
		menu = kb([
			["➖ حذف کانال", "➕ ثبت کانال"],
			["🏛 پنل مدیریت"]
		], resize_keyboard=True)
		
		channels = [v for c in api.channels_list() for v in (c["id"], c["name"])]

		if not channels:
			raise CmdException("❌ هیچ کانالی اضافه نشده است", menu=menu)

		first = True
		inx = 0

		while True:
			if not first:
				channels = [v for c in api.channels_list() for v in (c["id"], c["name"])]

				if not channels:
					await waiter.delete()
			
			channels = chunk(channels, 2)
			id, name = channels[inx]
			
			text = f"{inx + 1}/{len(channels)}\n📢 نام کانال: {name}"
			
			btn = ikb([
				[("❌ حذف کانال", "delete")],
				[("<<", "first"), ("<", "pre"), (">", "next"), (">>", "last")],
				[("بستن منو", "close")]
			])
			
			
			if first:
				waiter = await msg.reply(text, reply_markup=btn, disable_web_page_preview=True)
				first = False
			else:
				try:
					waiter = await waiter.edit(text, reply_markup=btn, disable_web_page_preview=True)
				except:
					pass
			
			try:
				click = await waiter.wait_for_click(msg.from_user.id, timeout=120)
			except ListenerTimeout:
				await bot.delete_messages(msg.chat.id, (msg.id, waiter.id), revoke=True)
				return
			ans = click.data
			
			if ans == "delete":
				
				conf_btn = ikb([
					[("✅ تایید", "confirm")],
					[("❌ انصراف", "back")]
				])
				
				try:
					waiter = await waiter.edit(f"⚠️ آیا از حذف کانال از لیست جوین اجباری اطمینان دارید؟", reply_markup=conf_btn)
				except:
					pass
				
				try:
					click = await waiter.wait_for_click(msg.from_user.id, timeout=120)
				except ListenerTimeout:
					await bot.delete_messages(msg.chat.id, (msg.id, waiter.id), revoke=True)
					return
				ans = click.data
				
				if ans == "confirm":
					api.channel_delete(id)
					
					if inx - 1 > 0:
						inx -= 1
					else:
						inx =  0
					
					await click.answer("✅ کانال حذف شد", show_alert=True)
			
			elif ans == "first":
				inx = 0
				await click.reply("⏮️ اول لیست")
			
			elif ans == "pre":
				if inx - 1 > 0:
					inx -= 1
				else:
					inx =  0
					await click.reply("⏮️ اول لیست")
			
			elif ans == "next":
				if inx + 1 < len(channels):
					inx += 1
				else:
					inx = len(channels) - 1
					await click.reply("⏭️ آخر لیست")
			
			elif ans == "last":
				inx = len(channels) - 1
				await click.reply("⏭️ آخر لیست")
			
			elif ans == "close":
				await waiter.delete()
				return
		
	except CmdException as e:
		await send_error(bot, msg.chat.id, e.message, admin_buttons(msg.from_user), e.menu)
	except Exception:
		await log_error(msg.chat.id, traceback.format_exc(), admin_buttons(msg.from_user))

# set messages menu
async def set_messages_menu(bot, msg):
	if not isAdmin(msg.from_user):
		return
	
	try:
		
		btns = kb([
			["🟢 استارت", "✅‌ رضایت های مشاوره"],
			["🛂‌ مشاوران مدیکال", "📃‌ قبولی ها"],
			["🏛 پنل مدیریت"]
		], resize_keyboard=True)
		
		await msg.reply("انتخاب کنید:", reply_markup=btns)
		
	except CmdException as e:
		await send_error(bot, msg.chat.id, e.message, admin_buttons(msg.from_user), e.menu)
	except Exception:
		await log_error(msg.chat.id, traceback.format_exc(), admin_buttons(msg.from_user))

# set messages cmd
async def set_messages_cmd(bot, msg):
	if not isAdmin(msg.from_user):
		return
	
	try:
		
		if msg.text == "🟢 استارت":
			part = "start"
			part_fa = "استارت"
		
		elif msg.text == "✅‌ رضایت های مشاوره":
			part = "satisfaction"
			part_fa = "رضایت های مشاوره"
		
		elif msg.text == "🛂‌ مشاوران مدیکال":
			part = "advisors"
			part_fa = "مشاوران مدیکال"
		
		elif msg.text == "📃‌ قبولی ها":
			part = "accepts"
			part_fa = "قبولی ها"
		
		btns = kb([["✅ اتمام ارسال"]], resize_keyboard=True)
		
		await msg.reply(f'📜 پیام های مد نظرتون برای دستور "{part_fa}" ارسال کنید و در آخر دکمه "اتمام ارسال" را کلیک کنید', reply_markup=btns)
		
		got = await wait(msg.chat.id, 600)
		
		if not got:
			await admin_cmd(bot, msg)
			return
		
		conf_btn = ikb([
			[("✅ ثبت پیام ها", "confirm")],
			[("انصراف", "cancel")]
		])
		
		try:
			waiter = await msg.reply(f'⚠️ آیا از ثبت {len(got):,} پیام برای دستور "{part_fa}" اطمینان دارید؟', reply_markup=conf_btn)
		except:
			pass
		
		try:
			click = await waiter.wait_for_click(msg.from_user.id, timeout=60)
		except ListenerTimeout:
			await waiter.delete()
			await admin_cmd(bot, msg)
			return
		ans = click.data
		
		await waiter.delete()
		
		if ans == "confirm":
			new = [(msg.from_user.id, m.id) for m in got]
			api.message_set(part, new)
			
			await msg.reply("✅ پیام ها ثبت شدند", reply_markup=admin_buttons(msg.from_user))
		
		else:
			await admin_cmd(bot, msg)
			return
		
	except CmdException as e:
		await send_error(bot, msg.chat.id, e.message, admin_buttons(msg.from_user), e.menu)
	except Exception:
		await log_error(msg.chat.id, traceback.format_exc(), admin_buttons(msg.from_user))


# register
def register_adminsSet(bot):
	bot.add_handler(MessageHandler(admins_list_cmd, filters.regex("^👥 ادمین ها$") & filters.private))
	bot.add_handler(MessageHandler(add_admin_cmd, filters.regex("^➕ ثبت ادمین$") & filters.private))
	bot.add_handler(MessageHandler(remove_admin_cmd, filters.regex("^➖ حذف ادمین$") & filters.private))
	bot.add_handler(MessageHandler(forced_join_menu, filters.regex("^🔒 جوین اجباری$") & filters.private))
	bot.add_handler(MessageHandler(add_channel_cmd, filters.regex("^➕ ثبت کانال$") & filters.private))
	bot.add_handler(MessageHandler(remove_channel_cmd, filters.regex("^➖ حذف کانال$") & filters.private))
	bot.add_handler(MessageHandler(set_messages_menu, filters.regex("^📜 تنظیم پیام ها$") & filters.private))
	bot.add_handler(MessageHandler(set_messages_cmd, filters.regex("^(🟢 استارت|✅‌ رضایت های مشاوره|📃‌ قبولی ها|🛂‌ مشاوران مدیکال)$") & filters.private))
