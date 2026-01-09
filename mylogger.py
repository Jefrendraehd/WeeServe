import weechat
import os
import datetime

from .sayto import SayTo

class MyLogger():
	def __init__(self, botname, logdir):
		self.SayTo = SayTo()
		self.logfile_dir = logdir
		self.log_filename = "bot_" + botname + ".log"
		self.full_log_path = self.logfile_dir + self.log_filename
		self.buffer_name = "WeeServe"
		temp = self.GetLog()
		if temp:
			self.log = temp
		else:
			self.log = []

	def GetLog(self):
		if os.path.isfile(self.full_log_path):
			with open(self.full_log_path, 'r', encoding='utf-8', errors='ignore') as infile:
				log_list = infile.readlines()
				return log_list

	def Log(self, stufftolog):
		newstuff = []
		if stufftolog:
			if type(stufftolog) == int:
				stufftolog = str(stufftolog)
			elif type(stufftolog) == list:
				for entry in stufftolog:
					if type(entry) == int:
						entry = str(entry)
					newstuff.append(entry)
				stufftolog = " ".join(newstuff)
			if stufftolog == "" or stufftolog == None:
				return
			self.SayTo.Buffer(self.buffer_name, stufftolog)
			stufftolog = self.TimeStamp() + stufftolog
               stufftolog = weechat.string_remove_color(stufftolog)
			self.log.append(stufftolog.strip())
			with open(self.full_log_path, 'w') as outfile:
				for entry in self.log:
					if entry[0] in "0123456789":
						outfile.write(entry.strip() + "\n")

	def TimeStamp(self):
		time_stamp = datetime.datetime.now().strftime("%H:%M:%S")
		return time_stamp + " "