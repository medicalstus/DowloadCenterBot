import os
import re
import time

cmd = "tmux" # "screen" or "tmux"

def get_sessions():
	if cmd == "screen":
		os.system("screen -wipe")
		return os.popen("screen -list").read()
	elif cmd == "tmux":
		return os.popen("tmux list-sessions 2>/dev/null").read()

def create_session(name, command):
	if cmd == "screen":
		os.system(f"screen -dmS {name} {command}")
	elif cmd == "tmux":
		os.system(f"tmux new-session -d -s {name} '{command}'")

while True:
	ls = get_sessions()
	lines = ls.split("\n")
	
	bot = False
	
	if cmd == "screen":
		for line in lines:
			if line.startswith("\t"):
				part = line.split("\t")[1]
				
				if re.search(r"^\d+\.BOT$", part):
					bot = True
	
	elif cmd == "tmux":
		for line in lines:
			if "BOT" in line:
				bot = True
	
	if not bot:
		create_session("BOT", "python3 bot.py")
	
	time.sleep(1)
