# coding=utf-8

import os
import json
import traceback
from pyrogram import filters
from pyromod.helpers import ikb
from pyrogram.handlers import MessageHandler
from pyromod.exceptions.listener_timeout import ListenerTimeout

from utils import api
from utils.helpers import CmdException, admin_buttons, isAdmin, send_error, log_error, chunk


# admin cmd
async def admin_cmd(bot, msg):
	if not isAdmin(msg.from_user):
		return
	
	try:
		
		await msg.reply("🏛️ پنل مدیریت", reply_markup=admin_buttons(msg.from_user))
		
	except CmdException as e:
		await send_error(bot, msg.chat.id, e.message, admin_buttons(msg.from_user), e.menu)
	except Exception:
		await log_error(msg.chat.id, traceback.format_exc(), admin_buttons(msg.from_user))

# files list
async def manage_files_cmd(bot, msg):
	if not isAdmin(msg.from_user):
		return
	
	try:
		
		roots = api.categories_roots()
		inx = roots[0]["top"] if roots else 0
		top_inx = inx
		step = 0
		moves = []
		first = True
		resend = False

		categories = [v for c in roots for v in (c["id"], c["name"])]

		while True:
			if not first:
				if inx == top_inx:
					cats = api.categories_roots()
				else:
					cats = api.categories_by_top(inx)
				categories = [v for c in cats for v in (c["id"], c["name"])]

			categories = chunk(categories, 2)
			base = [[("✅ ثبت جزوه", "newFile"), ("🗃️ زیر دسته", "sub")]]

			if inx == top_inx:
				base.append([("بستن منو", "close")])
			else:
				base.append([("بستن منو", "close"), ("بازگشت", "back")])

			for i in range(len(categories)):
				id, name = categories[i]
				base.insert(i, [(f"🔻 {name}", f"category/{id}")])

			files = [v for f in api.files_by_category(inx) for v in (f["id"], f["name"])]
			if files:
				files = chunk(files, 2)
				for i in range(len(files)):
					id, name = files[i]
					base.insert(i + len(categories), [(name, f"file/{id}")])
			
			btn = ikb(base)
			text = "📜 پیش نمایش منو\n✍️ میتوانید زیر دسته ها و جزوه آن ها را اضافه و یا حذف کنید"
			
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
				
				while True:
					_file = api.file_get(id)
					name, file_id = _file["name"], _file["file_id"]
					
					conf_btn = ikb([
						[("❌ حذف جزوه", "delete")],
						[("✍️ ویرایش", "edit"), ("📄 ارسال جزوه", "sendfile")],
						[("بستن منو", "close"), ("بازگشت", "back")]
					])
					
					try:
						waiter = await waiter.edit(f"📄 نام جزوه : {name}\n\n🔻 میتوانید جزوه را حذف کنید یا نام آن را تغییر دهید`", reply_markup=conf_btn)
					except:
						pass
					
					try:
						click = await waiter.wait_for_click(msg.from_user.id, timeout=60)
					except ListenerTimeout:
						continue
					ans = click.data
					
					if ans == "delete":
						
						conf_btn = ikb([
							[("❌ حذف جزوه", "confdelete")],
							[("بازگشت", "back")]
						])
						
						try:
							waiter = await waiter.edit("❌ آیا از حذف کردن جزوه اطمینان دارید؟", reply_markup=conf_btn)
						except:
							pass
						
						try:
							click = await waiter.wait_for_click(msg.from_user.id, timeout=60)
						except ListenerTimeout:
							continue
						ans = click.data
						
						if ans == "confdelete":
							api.file_delete(id)
							await click.answer("✅ حذف شد")
							break
					
					elif ans == "edit":
						btn = ikb([
							[("📄 تغییر فایل", "file"), ("✍️ تغییر نام", "name")],
							[("بازگشت", "back")]
						])
						
						try:
							waiter = await waiter.edit("🔻 یک گزینه را انتخاب کنید:", reply_markup=btn)
						except:
							pass
						
						try:
							click = await waiter.wait_for_click(msg.from_user.id, timeout=60)
						except ListenerTimeout:
							await waiter.delete()
							return
						ans = click.data
						
						if ans == "name":
							part = "name"
							part_fa = "نام"
						
						elif ans == "file":
							part = "file_id"
							part_fa = "فایل"
						
						else:
							continue
						
						await click.answer()
						
						deletes = []
						label = await msg.reply(f"✍️ {part_fa} جدید را ارسال کنید:")
						deletes.append(label.id)
						
						try:
							ask = await bot.listen(chat_id=msg.chat.id, timeout=120)
							deletes.append(ask.id)
						except ListenerTimeout:
							await bot.delete_messages(msg.chat.id, deletes, revoke=True)
							continue
						ans = ask.text
						
						if part == "name":
							if ans == None:
								await bot.delete_messages(msg.chat.id, deletes, revoke=True)
								continue
							
							if len(ans) > 250:
								await bot.delete_messages(msg.chat.id, deletes, revoke=True)
								await msg.reply("❌ نام باید از 250 کارکتر کمتر باشد")
								continue
						
						elif part == "file_id":
							if not ask.document:
								await bot.delete_messages(msg.chat.id, deletes, revoke=True)
								await msg.reply("❌ باید یک فایل ارسال میکردید")
								continue
							
							ans = ask.document.file_id
						
						api.file_update(id, **{part: ans})
						await bot.delete_messages(msg.chat.id, deletes, revoke=True)
					
					elif ans == "sendfile":
						await click.answer()
						await msg.reply_document(file_id)
					
					elif ans == "back":
						break
					
					elif ans == "close":
						await waiter.delete()
						return
			
			elif ans.startswith("category/"):
				await click.answer()
				id = int(ans.split("/")[1])
				moves.append(inx)
				inx = id
				step += 1
			
			elif ans == "newFile":
				await click.answer()
				resend = True
				await waiter.delete()
				
				name_label = await msg.reply("✍️ نام جزوه را ارسال کنید:")
				try:
					name_ask = await bot.listen(chat_id=msg.chat.id, timeout=60)
				except ListenerTimeout:
					continue
				name = name_ask.text
				
				if name == None:
					continue
				
				if len(name) > 250:
					await msg.reply("❌ نام باید از 250 کارکتر کمتر باشد")
					continue
				
				await msg.reply("📄 فایل جزوه را ارسال کنید:")
				try:
					file_ask = await bot.listen(chat_id=msg.chat.id, timeout=60)
				except ListenerTimeout:
					continue
				
				if not file_ask.document:
					await msg.reply("❌ باید فایل جزوه را ارسال میکردید")
					continue
				
				api.file_add(inx, name, step, file_ask.document.file_id)
				await msg.reply("✅ جزوه اضافه شد")
			
			elif ans == "sub":
				await click.answer()
				
				sub_btn = ikb([
					[("🗑️ حذف زیردسته", "delete"), ("✅ ثبت زیردسته", "create")],
					[("بستن منو", "close"), ("بازگشت", "back")]
				])
				
				while True:
					try:
						waiter = await waiter.edit(text, reply_markup=sub_btn)
					except:
						pass
					
					try:
						click = await waiter.wait_for_click(msg.from_user.id, timeout=60)
					except ListenerTimeout:
						break
					ans = click.data
					
					if ans == "create":
						deletes = []
						name_label = await msg.reply("🔻 نام دسته را ارسال کنید:")
						deletes.append(name_label.id)
						
						try:
							name_ask = await bot.listen(chat_id=msg.chat.id, timeout=60)
							deletes.append(name_ask.id)
						except ListenerTimeout:
							await bot.delete_messages(msg.chat.id, deletes, revoke=True)
							continue
						name = name_ask.text
						
						if name == None:
							await bot.delete_messages(msg.chat.id, deletes, revoke=True)
							continue
						
						if inx == top_inx:
							new_top = 0
						else:
							new_top = inx
						
						api.category_add(name, new_top, step)
						await bot.delete_messages(msg.chat.id, deletes, revoke=True)
						break
					
					elif ans == "delete":
						if categories == []:
							await click.answer("❌ هیچ زیردسته ای ثبت نشده")
						
						else:
							del_base = [[("بستن منو", "close"), ("بازگشت", "back")]]
							for i in range(len(categories)):
								id, name = categories[i]
								del_base.insert(i, [(f"🔻 {name}", f"deletecat/{id}")])
							
							del_btn = ikb(del_base)
							
							try:
								waiter = await waiter.edit(text, reply_markup=del_btn)
							except:
								pass
							
							try:
								click = await waiter.wait_for_click(msg.from_user.id, timeout=60)
							except ListenerTimeout:
								break
							ans = click.data
							
							if ans.startswith("deletecat/"):
								id = int(ans.split("/")[1])
								
								conf_btn = ikb([
									[("❌ حذف زیردسته", "confdelete")],
									[("بستن منو", "close"), ("بازگشت", "back")]
								])
								
								try:
									waiter = await waiter.edit("❌ آیا از حذف کردن زیردسته اطمینان دارید؟ با این کار تمامی جزوه ها در این زیر دسته و زیر دسته های داخل ان حذف خواهد شد!", reply_markup=conf_btn)
								except:
									pass
								
								try:
									click = await waiter.wait_for_click(msg.from_user.id, timeout=60)
								except ListenerTimeout:
									break
								ans = click.data
								
								if ans == "confdelete":
									api.category_delete(id, cascade=True)

									try:
										inx = moves[-1]
										moves.pop()
									except:
										inx = 0
										moves = []
									await click.answer("✅ حذف شد")
								
								elif ans == "back":
									continue
								
								elif ans == "close":
									await waiter.delete()
									return
							
							elif ans == "back":
								continue
							
							elif ans == "close":
								await waiter.delete()
								return
					
					elif ans == "back":
						break
					
					elif ans == "close":
						await waiter.delete()
						return
			
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
		await send_error(bot, msg.chat.id, e.message, admin_buttons(msg.from_user), e.menu)
	except Exception:
		await log_error(msg.chat.id, traceback.format_exc(), admin_buttons(msg.from_user))

# bot stats
async def bot_stats_cmd(bot, msg):
	if not isAdmin(msg.from_user):
		return
	
	try:
		
		data = api.stats()
		users = data["users"]
		files = data["files"]
		down = data["downloads"]
		users = users if users != None else 0
		files = files if files != None else 0
		down = down if down != None else 0
		
		await msg.reply(f"📊 **آمار ربات**\n\n👥 **تعداد کاربران:** {users:,} نفر\n📄 **تعداد جزوه ها:** {files:,} عدد\n📥 **دفعات دریافت فایل های موجود:** {down:,} بار")
		
	except CmdException as e:
		await send_error(bot, msg.chat.id, e.message, admin_buttons(msg.from_user), e.menu)
	except Exception:
		await log_error(msg.chat.id, traceback.format_exc(), admin_buttons(msg.from_user))

# phone numbers list
async def users_list_cmd(bot, msg):
	if not isAdmin(msg.from_user):
		return
	
	try:
		
		ls = api.users_all()

		if not ls:
			raise CmdException("❌ اطلاعاتی ثبت نشده است")

		await msg.reply("⌛ لطفا صبر کنید...")

		users = []

		for u in ls:
			users.append({
				"id": u["id"],
				"username": u["username"],
				"name": u["name"],
				"number": u["number"]
			})
		
		filename = "users_data.json"
		with open(filename, "w", encoding="utf-8") as f:
			json.dump(users, f, ensure_ascii=False, indent=2)
		
		await msg.reply_document(filename, caption=f"👥 خروجی اطلاعات {len(ls):,} کاربر")
		
		try:
			os.remove(filename)
		except:
			pass
		
	except CmdException as e:
		await send_error(bot, msg.chat.id, e.message, admin_buttons(msg.from_user), e.menu)
	except Exception:
		await log_error(msg.chat.id, traceback.format_exc(), admin_buttons(msg.from_user))


# register admins
def register_adminsMain(bot):
	bot.add_handler(MessageHandler(admin_cmd, filters.regex("^(🏛 پنل مدیریت|🔙 پنل مدیریت)$") & filters.private))
	bot.add_handler(MessageHandler(manage_files_cmd, filters.regex("^🗃️ مدیریت جزوه ها$") & filters.private))
	bot.add_handler(MessageHandler(bot_stats_cmd, filters.regex("^📊 آمار ربات$") & filters.private))
	bot.add_handler(MessageHandler(users_list_cmd, filters.regex("^📄 لیست کاربران$") & filters.private))
