import traceback
from asyncio import sleep
from utils.helpers import write_error

# waiters
waiting = {}

# get waiting
def get_waiting():
	return waiting

# set waiting
def set_waiting(id, key, value):
	waiting[id][key] = value

# wait functions
async def wait(user, timeout, end="✅ اتمام ارسال", limit=None, format=None):
	try:
		
		if user not in waiting.keys():
			waiting[user] = {
				"status": "wait",
				"limit": limit,
				"end": end,
				"format": format,
				"got": [],
				"time": 0
			}
		
		while True:
			if waiting[user]["status"] == "end":
				got = waiting[user]["got"]
				del waiting[user]
				return got
			
			waiting[user]["time"] += 1
			await sleep(1)
			
			if waiting[user]["time"] >= timeout:
				got = waiting[user]["got"]
				del waiting[user]
				return got
		
	except:
		write_error(None, traceback.format_exc())
