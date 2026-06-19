# coding=utf-8

import traceback
from pyrogram import filters
from utils.helpers import write_error
from pyrogram.handlers import MessageHandler
from utils.wait import get_waiting, set_waiting


# wait handler
async def wait_handler(bot, msg):
	try:
		
		id = msg.from_user.id
		waiting = get_waiting()
		
		if id in waiting:
			end = waiting[id]["end"]
			limit = waiting[id]["limit"]
			format = waiting[id]["format"]
			
			if msg.text == end:
				set_waiting(id, "status", "end")
				return
			
			if format:
				if msg.document and msg.document.file_name.lower().endswith(format):
					set_waiting(id, "got", waiting[id]["got"] + [msg])
			else:
				set_waiting(id, "got", waiting[id]["got"] + [msg])
			
			set_waiting(id, "time", 0)
				
			if limit:
				got = waiting[id]["got"]
				if len(got) >= limit:
					set_waiting(id, "status", "end")
					return
		
	except:
		write_error(None, traceback.format_exc())

# register waiter
def register_waiter(bot):
	bot.add_handler(MessageHandler(wait_handler, filters.private))
