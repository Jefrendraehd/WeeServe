#!/usr/bin/env python3.9
#
# irc xdcc serve bot
#

import weechat
weechat.register("weeserve.py", "jefrendraehd@gmail.com", "1.0", "GPL3", "Simple Fileserver", "", "")

#Local imports
from weeserve import config as config
from weeserve.mylogger import MyLogger
from weeserve.library import Library
from weeserve.color import color as Clr
from weeserve.sayto import SayTo

#Python imports
import os
import sys
import json
import datetime

#Constants
FILENAME = 0
FILEPATH = 1
FULLPATH = 2
FILESIZE = 3
CHANNEL = 4
NICK = 5
STATUS = 6
RETRIES = 7
#library entry = [FILENAME, FILEPATH, FULLPATH, FILESIZE]
#master_queue[FILENAME, FILEPATH, FULLPATH, FILESIZE, CHANNEL, NICK, STATUS, RETRIES]

main_queue_size = 50
main_queue_full_msg = "The main queue is full. Please wait a while."

max_concurrent_sends = 5
personal_queue_size = 5
filelist_queue = []

file_list_avail = True
file_transfer_avail = True
file_lib_file = ""

list_prefix_char = "@"
file_prefix_char = "!"
cmnd_prefix_char = "&"
respond_to_list = True
respond_to_search = False
list_response = []
find_response = []

def TimeStamp():
	time_stamp = datetime.datetime.now().strftime("%H:%M:%S")
	return time_stamp + " "

def NewLogName(tempname):
	suffix = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
	filename = tempname + "_" +  suffix + ".log"
	return filename

def UpdateScript():
	if os.path.isfile(script_source_dir + script_filename):
		shutil.rename(script_dest_dir + script_filename, script_dest_dir + script_backfile)
		shutil.move(script_source_dir + script_filename, script_dest_dir + script_filename)
		ServerReport("Server: Reloading weeserve.py script.")
		#SaveCurrrentState()
		weechat.command("weechat", "/script reload weeserve.py")
		return

def ServerReport(message):
	if not message:
		return
	buffer_handle = weechat.buffer_search("python", "WeeServe")
	if buffer_handle is None:
		buffer_handle = weechat.buffer_new("WeeServe","WeeServeInput_cb","","","")
	weechat.prnt(buffer_handle, message)


class Fserve():

	def __init__(self):
		self.buffer_name = "WeeServe"
		self.SayTo = SayTo()
		self.buffer_handle = None
		self.OpenBuffer()
	
		self.config = config.Config()
		self.irc = self.config.ircdata
		self.server = self.config.serverdata
		self.serving_channel = str(self.irc.serve_channel)
		self.bot_name = self.irc.botname

		self.prefixes = [list_prefix_char, file_prefix_char, cmnd_prefix_char]
		self.list_trigger = self.server.list_trigger
		self.file_trigger = self.server.file_trigger
		self.cmnd_trigger = self.server.serv_trigger
		self.ctcp_trigger = self.server.ctcp_trigger

		self.file_queue = []
		self.list_queue = []
		self.user_queue_limit = 5
		self.file_queue_limit = 50
		self.file_in_process = []
		self.list_in_process = []
		self.files_served = 0
		self.lists_served = 0
		self.library = Library(self.irc, self.server)
		self.library.ReadLibraryFile()
		self.server_enabled = self.server.server_enabled
		self.server_idle = True

		self.advert_timer = 900
		self.advert = self.server.advert_text
    self.advert_enabled = False
		self.logger = MyLogger(self.irc.botname, self.server.logs_directory)
		#self.config.ShowConfig()


	def register_command(self, name):
		"""Decorator function that allows registration of 'commands' """
		self.LogLister("Registering command %s" % name)
		def decorator( func ):
			self._registered_commands[name] = func
			def wrapper(*args, **kwargs):
				return func(*args, **kwargs)
			return wrapper
		return decorator

	def ShowStatus(self):
		self.LogLister("Status Report.")
		self.LogLister("Botname: " + self.irc.botname)
		self.LogLister("Serving channel: " + self.irc.serve_channel)
		self.LogLister("Files to serve: " + str(self.library.RecordCount()))
		self.LogLister("Advert: " + self.advert)
		self.LogLister("Advert timer: " + str(self.advert_timer))
		self.LogLister("Server enabled: " + str(self.server.server_enabled))
		self.LogLister("Server Idle: " + str(self.server_idle))
		self.LogLister("List trigger: " + self.list_trigger)
		self.LogLister("File Trigger: " + self.file_trigger)
		self.LogLister("Files Served: " + str(self.files_served))
		self.LogLister("Lists Served: " + str(self.lists_served))

	def Start(self):
		self.LogLister(" " + TimeStamp() + " Server starting.")
		self.server.server_enabled = True
		self.ShowAdvert()

	def Stop(self):
		self.LogLister(" " + TimeStamp() + "Server stopped")
		self.server.server_enabled = False

	def ShowAdvert(self):
    if not self.advert_enabled:
     return
		if self.server.server_enabled:
			print("advert enabled")
			#self.serving_channel_handle = self.irc.irc_server + self.irc.serve_channel
			#cmnd_chan = weechat.buffer_search("irc", self.irc.serve_channel)
			cmnd_chan = weechat.buffer_search("", "irc.dejatoons.net.#rpg-books")
			weechat.command(cmnd_chan, self.advert)
			print("sent advert")
			#self.SayTo.Buffer(self.irc.serve_channel, self.advert)

	def XferFailed(self, nick):
		if nick == self.current_file_data[NICK]:
			self.LogLister(clr["label"]("File transfer Failed! Retries") + ": " + clr["value"](self.current_file_data[RETRIES]))
			self.current_file_data[RETRIES] += 1
			if self.current_file_data[RETRIES] > 2:
				return
			else:
				self.file_queue.append(self.current_file_data)
				self.current_file_data = []
				return
		if nick == self.current_list_data[NICK]:
			self.LogLister(clr["label"]("List transfer Failed! Retries") + ": " + clr["value"](self.current_list_data[RETRIES]))
			self.current_list_data[RETRIES] += 1
			if self.current_list_data[RETRIES] > 2:
				return
			else:
				self.list_queue.append(self.current_list_data)
				self.current_list_data = []
				return

	def XferCompleted(self):
		if nick == self.current_file_data[NICK]:
			self.LogLister(clr["label"]("File transfer completed") + ": " + clr["value"](self.current_file_data[NICK]))
			self.current_file_data = []
			self.files_served += 1
			return
		if nick == self.current_list_data[NICK]:
			self.LogLister(clr["label"]("List transfer completed") + ": " + clr["value"](self.current_list_data[NICK]))
			self.current_list_data = []
			self.lists_served += 1
			return

	def ReQueue(self):
		if self.file_in_process:
			self.file_queue.append(self.file_in_process)
			self.LogLister(self.file_in_process[1] + " for " + self.file_in_process[0][1] + " added back to queue")
			self.file_in_process = []

	def ProcessQueue(self):
		if self.server.server_enabled:
			if self.list_queue:
				self.SendList()
			else:
				if self.file_queue:
					self.SendFile()

	def SendFile(self):
		if self.file_in_process:
			return
		if not self.file_queue:
			return
		self.file_in_process = self.file_queue.pop(0)
		weechat.command(self.file_in_process[CHANNEL], "/dcc send " + self.file_in_process[NICK], + " " + self.file_in_process[FULLPATH])
		part1 = clr["label"]("Sending") + ": "
		part2 = clr["value"](self.file_in_process[FILENAME]) + " to "
		part3 = clr["value"](self.file_in_process[NICK])
		self.LogLister(part1 + part2 + part3)

	def SendList(self):
		if self.list_in_process:
			return
		if not self.list_queue:
			return
		self.list_in_process = self.list_queue.pop(0)
		weechat.command(self.list_in_process[CHANNEL], "/dcc send " + self.list_in_process[NICK] + " " + self.list_in_process[FULLPATH])
		part1 = clr["label"]("Sending") + ": "
		part2 = clr["value"](self.list_in_process[FILENAME]) + " to "
		part3 = clr["value"](self.list_in_process[NICK])
		self.LogLister(part1 + part2 + part3)
		
	def ShowHelp(self):
		#self.LogLister
		self.LogLister("Help for WeeServe buffer")
		self.LogLister("set            Change a server setting.")
		self.LogLister("settings       View current server settings.")
		self.LogLister("start          Start the server.")
		self.LogLister("stop           Stop the server. Queue will finish.")
		self.LogLister("rescan         Rebuild the available file list.")
		self.LogLister("advert         Trigger advertisement.")
		self.LogLister("stats          View server statistics.")
		self.LogLister("help           Show configuration help")
		self.LogLister("irc            View IRC settings.")
		self.LogLister("server         View server settings.")
		self.LogLister("misc           Show miscellanious settings.")
		
#		self.LogLister
#		self.LogLister

	def ProcessInput(self, the_buffer, command_line):
		valid_commands = ["?", "set", "irc", "misc", "server", "start", "stop", "save", "rescan", "stats", "help", "advert"]
		if not command_line:
			return
		the_command = command_line[0].lower()
		if not command_line[0] in valid_commands:
			return
		if the_command == "?":
			self.ShowHelp()
		if the_command == "set" and len(command_line) == 3:
			setting = command_line[1]
			newvalue = command_line[2]
			if self.config.ChangeSetting(setting, newvalue) == "refresh":
				self.irc = self.config.ircdata
				self.server = self.config.serverdata
				self.serving_channel = str(self.irc.serve_channel)
				self.bot_name = self.irc.botname
				self.list_trigger = self.server.list_trigger
				self.file_trigger = self.server.file_trigger
				self.cmnd_trigger = self.server.serv_trigger
				self.ctcp_trigger = self.server.ctcp_trigger
				self.library = Library(self.irc, self.server)
				self.library.ReadLibraryFile()
				self.advert = self.server.advert_text
				self.logger = MyLogger(self.irc.botname, self.server.logs_directory)
		if the_command == "start":
			self.Start()
		if the_command == "stop":
			self.Stop()
		if the_command == "irc":
			self.config.ShowIrcConfig()
		if the_command == "server":
			self.config.ShowServerConfig()
		if the_command == "misc":
			self.config.ShowMiscConfig()
		if the_command == "save":
			self.config.Save()
		if the_command == "rescan":
			self.library.ReScan()
		if the_command == "stats":
			self.ShowStatus()
		if the_command == "help":
			self.config.HelpInfo()
		if the_command== "advert":
			self.ShowAdvert()

	def ProcessCommand(self, the_buffer, the_requester, command_line):
		if the_requester:
			if the_requester.startswith("@") or the_requester.startswith("&") or the_requester.startswith("+"):
				the_requester = the_requester[1:]

		valid_commands = [self.list_trigger, self.file_trigger, self.ctcp_trigger,
						"@find", "!info", "!list", "@search"]
		if not command_line:
			return
		command_line = command_line.split()
		the_command = command_line[0].lower()
		if not command_line[0] in valid_commands:
			return
#		print(command_line)
		if the_command == self.list_trigger and len(command_line) == 1:
			self.QueueList(the_buffer, the_requester)
			return
		if the_command == self.ctcp_trigger and len(command_line) == 1:
			self.QueueList(the_buffer, the_requester, "ctcp")
			return
		if the_command == self.file_trigger and len(command_line) > 1:
			the_file_requested = ' '.join(command_line[1:])
			self.QueueFile(the_buffer, the_requester, the_file_requested)
			return
		if the_command == "@find" and len(command_line) > 1:
			the_file_requested = ' '.join(command_line[1:])
			self.SayTo.RequesterMsg(the_buffer, the_requester, "Searching for: %s" %(the_file_requested))
			results = self.library.SearchFor(the_file_requested)
			if results:
				self.SayTo.RequesterMsg(the_buffer, the_requester, "I found %d entries matching your searchterm: %s." %(len(results), the_file_requested))
				if len(results) > 10:
					self.SayTo.Requester(the_buffer, the_requester, "Showing you the first 10 entries.")
				self.SayTo.RequesterMsg(the_buffer, the_requester, "Using @search will send you a file containing all entries found.")
				self.SayTo.RequesterMsg(the_buffer, the_requester, "Download my master list %s to access more files." %(self.list_trigger))
				results = results[:9]
				for entry in results:
					self.SayTo.RequesterMsg(the_buffer, the_requester, self.file_trigger + " " + entry)
			else:
				self.SayTo.RequesterMsg(the_buffer, the_requester, "No results found")
			return
		#print(the_command)
		if the_command == "!list" or the_command == "!info":
			self.SayTo.RequesterMsg(the_buffer, the_requester, "!!!!!!!!!!-> UNDER CONSTRUCTION <-!!!!!!!!!!")
			self.SayTo.RequesterMsg(the_buffer, the_requester, "Hello! I am %s." %(self.bot_name))
			self.SayTo.RequesterMsg(the_buffer, the_requester, "You can get my filelist by typing %s in %s." %(self.list_trigger, self.serving_channel))
			self.SayTo.RequesterMsg(the_buffer, the_requester, "or privately as /ctcp %s %s." %(self.bot_name, self.list_trigger))
			self.SayTo.RequesterMsg(the_buffer, the_requester, "Files can be requested in %s with %s <filename>." %(self.serving_channel, self.file_trigger))
			self.SayTo.RequesterMsg(the_buffer, the_requester, "or privately as /ctcp %s %s <filename>." %(self.bot_name, self.file_trigger))
			return
		if the_command == "@search":
			if not respond_to_search:
				return
			if len(command_line) < 2:
				self.SayTo.RequesterNotice(the_buffer, the_requester, "Malformed Request Command.")
				self.SayTo.RequesterNotice(the_buffer, the_requester, "Please use " + self.prefixes[0] + "search <keywords>")
				self.SayTo.RequesterNotice(the_buffer, the_requester, "For instance " + self.prefixes[0] + "search winnie the pooh")
				return
			the_file_requested = ' '.join(command_line[1:])
			self.SayTo.RequesterNotice(the_buffer, the_requester, "Searching for: %s" %(the_file_requested))
			results = self.library.SearchFor(the_file_requested)
			if results:
				self.QueueSearch(the_buffer, the_requester, results)
			else:
				self.SayTo.RequesterNotice(the_buffer, the_requester, "No results found")

	def QueueSearch(self, the_buffer, the_requester, the_list):
		filename = "search_results_for_" + the_requester + ".txt"
		filename = self.server.lists_directory + filename
		with open(filename, 'w') as outfile:
			for entry in the_list:
				outfile.write(bot.config.file_trigger + " " + entry + "\n")
		self.LogLister("Search file generated for " + the_requester)
		file_requested = filename
		file_dir = self.bot.config.lists_directory
		full_path_file = self.bot.config.lists_directory + filename
		filesize = os.path.getsize(full_path_file)
		file_data = [filename, file_dir, full_path_file, filesize]
		file_data.append(the_buffer)
		file_data.append(the_requester)
		file_data.append(1)
		file_data.append(3)
		self.list_queue.append(file_data)
		self.LogLister("Xfer: Queueing search results for " + the_requester)

	def CheckForFile(self, the_file):
		rvalue = False
		result = self.library.Query(the_file)
		if result:
			rvalue = True
		return rvalue

	def cmd_help(self, nick, args):
		return

	def QueueFile(self, the_buffer, the_requester, file_to_send):
		if self.CheckForFile(file_to_send):
			already_have = self.file_queue.count(the_requester)
			if already_have == self.user_queue_limit:
				self.SayTo.RequesterNotice(the_buffer, the_requester, "You already have 5 requests in my queue.")
			else:
				self.SayTo.RequesterNotice(the_buffer, the_requester, "Your request has been queued for download.")
				#file_queue[FILENAME, FILEPATH, FULLPATH, FILESIZE, CHANNEL, NICK, STATUS, RETRIES]
				file_data = self.library.GetFileData(file_to_send)
				file_data.append(the_buffer)
				file_data.append(the_requester)
				file_data.append(1)
				file_data.append(3)
				self.file_queue.append(file_data)
				self.LogLister("Xfer: Queueing %s for %s" %(file_to_send, the_requester))
		else:
			self.SayTo.RequesterNotice(the_buffer, the_requester, "That file was not found in my list.")
			self.LogLister("Xfer: File not found %s" %(file_to_send))

	def QueueList(self, the_buffer, the_requester, which_list="norm"):
		already_have = self.list_queue.count(the_requester)
		if already_have:
			self.SayTo.RequesterNotice(the_buffer, the_requester, "You already have a list request queued.")
		else:
			self.SayTo.RequesterNotice(the_buffer, the_requester, "Your list has been queued for download.")
			if which_list == "norm":
				file_requested = self.server.list_file
			elif which_list == "ctcp":
				file_requested = self.server.ctcp_file
			file_dir = self.server.lists_directory
			full_path_file = self.server.lists_directory + file_requested
			filesize = 1000000             #os.path.getsize(full_path_file)
			file_data = [file_requested, file_dir, full_path_file, filesize]
			file_data.append(the_buffer)
			file_data.append(the_requester)
			file_data.append(1)
			file_data.append(3)
			self.list_queue.append(file_data)
			self.LogLister("Xfer: Queueing master list for " + the_requester)

	def FindBuffer(self):
		if weechat.buffer_search("python", self.buffer_name):
			return True
		return False

	def OpenBuffer(self):
		self.buffer_handle = weechat.buffer_new(self.buffer_name,"WeeServeInput_cb","","","")

	def LogLister(self, stufftolog):
		self.logger.Log(stufftolog)

#file_queue[FILENAME, FILEPATH, FULLPATH, FILESIZE, CHANNEL, NICK, STATUS, RETRIES]
bot = Fserve()

def FileRecv_cb(data, signal, signal_data):
	weechat.infolist_next(signal_data)
	status = weechat.infolist_string(signal_data, 'status_string')
	filename = weechat.infolist_string(signal_data, 'filename')
	local_filename = weechat.infolist_string(signal_data, 'local_filename')
	size = weechat.infolist_string(signal_data, 'size')
	remote_nick = weechat.infolist_string(signal_data, 'remote_nick')
	direction = weechat.infolist_string(signal_data, 'type_string')
	if direction == "file_send_active":
		if status == "failed":
			bot.XferFailed(nick)
		if status == "done":
			bot.XferCompleted(nick)
	return weechat.WEECHAT_RC_OK

logfile = bot.server.log_file
logdir = bot.server.logs_directory
if os.path.isfile(logdir + logfile):
	newname = NewLogName(logfile)
	os.rename(logdir + logfile, logdir + newname)
base_logger = MyLogger(bot.irc.botname, bot.server.logs_directory)

list_trigger = bot.server.list_trigger     #list requesting
file_trigger = bot.server.file_trigger     #file requesting
#serv_trigger = bot.server.serv_trigger     #for bot interaction buffer
serving_buffer_pointer = weechat.buffer_search("", "irc.dejatoons.#rpg-books")
advert_timer = bot.server.advert_timer


def PVmessage_cb(data, signal, signal_data):
	pass
	
#	base_logger.Log(Clr.red(data))
#	base_logger.Log(Clr.lgreen(signal))
#	base_logger.Log(Clr.lcyan(signal_data))
	return weechat.WEECHAT_RC_OK

def Advert_cb(data, signal):
	bot.ShowAdvert()
	return weechat.WEECHAT_RC_OK

def WeeServe_cb(data, buffer, args):
	argument_list = args      #.split()
	bot.ProcessControl(buffer, argument_list)
	return weechat.WEECHAT_RC_OK

def WeeServeInput_cb(data, buffer, input_data):
#	print("in input callback")
	argument_list = input_data.split()
	bot.ProcessInput(buffer, argument_list)
	return weechat.WEECHAT_RC_OK_EAT

def WeePrint_cb(data, buffer, date, tags, displayed, highlight, prefix, message):	
	if bot.server.server_enabled:
		bot.ProcessCommand(buffer, prefix, message)         #.split())
		
#		if prefix.startswith("@") or prefix.startswith("&") or prefix.startswith("+"):
#			bot.ProcessCommand(buffer, prefix[1:], message)         #.split())
#		else:
#			bot.ProcessCommand(buffer, prefix, message)         #.split())
	return weechat.WEECHAT_RC_OK_EAT

def ProcessQueue(data, signal):
	bot.ProcessQueue()
	return weechat.WEECHAT_RC_OK


priv_hook = weechat.hook_signal("irc_ctcp;irc_pv", "PVmessage_cb", "")
wee_hook = weechat.hook_command("ws", "", "", "", "", "WeeServe_cb", "")
file_hook = weechat.hook_print(serving_buffer_pointer, "", "", 1, 'WeePrint_cb', "")

advert_hook = weechat.hook_timer(1000*bot.advert_timer, 0, 0, "Advert_cb", "")
que_hook = weechat.hook_timer(1000, 0, 0, "ProcessQueue", "")
 

#weechat.hook_signal('xfer_ended', 'xfer_callback', '')

# was xfer_ended.  xfer_resume_ready  xfer_start_resume  xfer_send_accept_resume
    # xfer_accept_resume    xfer_send_ready    xfer_add




