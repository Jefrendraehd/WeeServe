import json
import os
from dataclasses import dataclass, asdict
import glob
import sys

import weechat

from .color import color as Clr

from .mylogger import MyLogger
from .sayto import SayTo

basepath = weechat.info_get("weechat_data_dir","")
script_dir = basepath + "/python/weeserve/"
script_data = script_dir + "weeservedata/"
list_dir = script_data + "lists/"
log_dir = script_data + "logs/"
lib_dir = script_data + "library/"
cfg_dir = script_dir

list_prefix_char = "@"
file_prefix_char = "!"
cmnd_prefix_char = "&"
prefixes = [list_prefix_char, file_prefix_char, cmnd_prefix_char]

@dataclass
class MiscData:
	basepath:         str = ""     #weechat.info_get("weechat_data_dir","")
	script_dir:       str = ""     #basepath + "/python/weeserve/"
	script_data:      str = ""     #script_dir + "weeservedata/"
	list_dir:         str = ""     #script_data + "lists/"
	log_dir:          str = ""     #script_data + "logs/"
	lib_dir:          str = ""     #script_data + "library/"
	cfg_dir:          str = ""     #script_dir
	list_prefix_char: str = ""     #"@"
	file_prefix_char: str = ""     #"!"
	cmnd_prefix_char: str = ""     #"&"
	weeleech_buffer:  str = ""     #"WeeChat"

@dataclass
class IrcData:
	irc_server:       str = ""
	irc_port:         int = 0
	irc_password:     str = ""
	irc_sasl:         str = ""
	serve_channel:    str = ""
	chan_password:    str = ""
	botname:          str = ""

@dataclass
class ServerData:
	files_directory:  str = ""
	lists_directory:  str = ""
	logs_directory:   str = ""
	list_trigger:     str = ""
	file_trigger:     str = ""
	serv_trigger:     str = ""
	info_trigger:     str = ""
	ctcp_trigger:     str = ""
	library_file:     str = ""
	list_file:        str = ""
	ctcp_file:        str = ""
	log_file:         str = ""
	advert_timer:     int = 0
	advert_type:      str = ""
	advert_text:      str = ""
	list_service:     bool = False
	find_service:     bool = False
	srch_service:     bool = False
	server_enabled:   bool = False


class Config():
	def __init__(self, bot_name=None):
		self.config_file = ""
		self.buffer_name = "WeeServe"
		self.buffer_handle = None
		self.SayTo = SayTo()
		file_to_load = None
		botlist = []
		if bot_name:
			file_name = "bot_" + bot_name + ".cfg"
			if os.path.isfile(file_name):
				self.config_file = file_name
			else:
				self.SayTo.Buffer(self.buffer_name, Clr.alert("Configuration file not found."))
		else:
			botlist = glob.glob(cfg_dir + "*.cfg")
			if botlist:
				if len(botlist) > 1:
					self.SayTo.Buffer(self.buffer_name, Clr.alert("Multiple Configuration files found. Please specify one on the command line.  Exiting."))
					sys.exit(1)
				else:
					self.config_file = botlist[0]
		if self.config_file:
			self.Load()
		else:
			self.SayTo.Buffer(self.buffer_name, Clr.alert("Creating default configuration"))
			self.DefaultMiscData()
			self.DefaultIrcData()
			self.DefaultServerData()
			self.config_file = cfg_dir + "bot_" + self.ircdata.botname + ".cfg"
			self.Save()
		self.logger = MyLogger(self.ircdata.botname, self.serverdata.logs_directory)

	def Load(self):
		with open(self.config_file, "r") as infile:
			data_block = json.load(infile)
		if len(data_block) == 2:       #old config
			data1 = data_block[0]
			data2 = data_block[1]
			self.miscdata = MiscData()
			self.DefaultMiscData()
			self.ircdata  = IrcData(**data1)
			self.serverdata = ServerData(**data2)
		else:
			data1 = data_block[0]
			data2 = data_block[1]
			data3 = data_block[2]
			self.ircdata  = IrcData(**data1)
			self.serverdata = ServerData(**data2)
			self.miscdata = MiscData(**data3)

	def Save(self):
		with open(self.config_file, "w") as outfile:
			json.dump([asdict(self.ircdata), asdict(self.serverdata), asdict(self.miscdata)], outfile)
			self.SayTo.Buffer(self.buffer_name, Clr.alert("Configuration successfully saved to %s" %(self.config_file)))

	def DefaultIrcData(self):
		self.ircdata = IrcData()
		self.ircdata.irc_server = "127.0.0.1"
		self.ircdata.irc_port = 6667
		self.ircdata.serve_channel = "#Bot-Test"
		self.ircdata.chan_password = ""
		self.ircdata.botname = "MyBot"
		self.ircdata.irc_password = ""
		self.ircdata.irc_sasl = ""
	
	def DefaultServerData(self):
		self.serverdata = ServerData()
		self.serverdata.files_directory = lib_dir
		self.serverdata.lists_directory = list_dir
		self.serverdata.logs_directory = log_dir
		self.serverdata.list_trigger = "@" + self.ircdata.botname
		self.serverdata.file_trigger = "!" + self.ircdata.botname
		self.serverdata.serv_trigger = "&" + self.ircdata.botname
		self.serverdata.info_trigger = "!" + "info"
		self.serverdata.ctcp_trigger = "@" + self.ircdata.botname + "-ctcp"
		self.serverdata.library_file = self.ircdata.botname + ".json"
		self.serverdata.list_file = self.ircdata.botname + ".txt"
		self.serverdata.ctcp_file = self.ircdata.botname + "-ctcp.txt"
		self.serverdata.log_file = "bot_" + self.ircdata.botname + ".log"
		self.serverdata.server_enabled = False
		self.serverdata.advert_timer = 600
		self.serverdata.list_service = True
		self.serverdata.find_service = True
		self.serverdata.srch_service = True
		self.serverdata.advert_type = ""
		self.serverdata.advert_text = "Type !info to access this server."
	
	def DefaultMiscData(self):
		self.miscdata = MiscData()
		self.miscdata.basepath = weechat.info_get("weechat_data_dir","")
		self.miscdata.script_dir = self.miscdata.basepath + "/python/weeserve/"
		self.miscdata.script_data = self.miscdata.script_dir + "weeservedata/"
		self.miscdata.list_dir = self.miscdata.script_data + "lists/"
		self.miscdata.log_dir = self.miscdata.script_data + "logs/"
		self.miscdata.lib_dir = self.miscdata.script_data + "library/"
		self.miscdata.cfg_dir = self.miscdata.script_dir
		self.miscdata.list_prefix_char = "@"
		self.miscdata.file_prefix_char = "!"
		self.miscdata.cmnd_prefix_char = "&"
		self.miscdata.weeleech_buffer = "WeeChat"

	def ChangeSetting(self, setting, new_value):
		successful = True
		match setting:
			case "irc_server":
				self.ircdata.irc_server = new_value
			case "irc_port":
				if new_value.isnum():
					self.ircdata.irc_port = int(new_value)
				else:
					self.LogLister("Invalid entry. Must be a numerical value.")
					successful = False
			case "irc_password":
				self.ircdata.irc_password = new_value
			case "irc_sasl":
				self.ircdata.irc_sasl = new_value
			case "serve_channel":
				self.ircdata.serve_channel = new_value
			case "chan_password":
				self.ircdata.chan_password = new_value
			case "botname":
				self.ircdata.botname = new_value
				self.serverdata.list_trigger = "@" + self.ircdata.botname
				self.serverdata.file_trigger = "!" + self.ircdata.botname
				self.serverdata.serv_trigger = "&" + self.ircdata.botname
				self.serverdata.ctcp_trigger = "@" + self.ircdata.botname + "-ctcp"
				self.serverdata.library_file = self.ircdata.botname + ".json"
				self.serverdata.list_file = self.ircdata.botname + ".txt"
				self.serverdata.ctcp_file = self.ircdata.botname + "-ctcp.txt"
				self.serverdata.log_file = "bot_" + self.ircdata.botname + ".log"
			case "files_directory":
				if self.CheckDir(new_value):
					self.serverdata.files_directory = new_value
				else:
					self.LogLister("Directory not found. Create in shell and retry.")
					successful = False
			case "lists_directory":
				if self.CheckDir(new_value):
					self.serverdata.lists_directory = new_value
				else:
					self.LogLister("Directory not found. Create in shell and retry.")
					successful = False
			case "logs_directory":
				if self.CheckDir(new_value):
					self.serverdata.logs_directory = new_value
				else:
					self.LogLister("Directory not found. Create in shell and retry.")
					successful = False
			case "list_trigger":
				self.serverdata.list_trigger = new_value
			case "file_trigger":
				self.serverdata.file_trigger = new_value
			case "serv_trigger":
				self.serverdata.serv_trigger = new_value
			case "info_trigger":
				self.serverdata.info_trigger = new_value
			case "library_file":
				self.serverdata.library_file = new_value
			case "list_file":
				self.serverdata.list_file = new_value
			case "ctcp_file":
				self.serverdata.ctcp_file = new_value
			case "log_file":
				self.serverdata.log_file = new_value
			case "advert_timer":
				self.serverdata.advert_timer = new_value
			case "advert_type":
				self.serverdata.advert_type = new_value
			case "advert_text":
				self.serverdata.advert_text = new_value
			case "list_service":
				self.serverdata.list_service = new_value
			case "find_service":
				self.serverdata.find_service = new_value
			case "srch_service":
				self.serverdata.srch_service = new_value
			case "server_enabled":
				self.serverdata.server_enabled = new_value
		self.LogLister(Clr.label(setting) + " changed to " + Clr.value(new_value))
		if successful:
			return "refresh"
		else:
			return None

	def CheckDir(self, dir_to_check):
		if os.path.isdir(dir_to_check):
			return True

	def HelpInfo(self):
		self.LogLister(Clr.title("Change settings with") + Clr.value(" botset <option> <new_value>"))
		self.LogLister(Clr.label("irc_server      ") + Clr.value("IRC server to serve on."))
		self.LogLister(Clr.label("irc_port        ") + Clr.value("IRC port (6667"))
		self.LogLister(Clr.label("serve_channel   ") + Clr.value("IRC channel to serve in."))
		self.LogLister(Clr.label("chan_password   ") + Clr.value("Password to access channel if needed."))
		self.LogLister(Clr.label("botname         ") + Clr.value("The name of the bot"))
		self.LogLister(Clr.label("irc_password    ") + Clr.value("IRC server password if used"))
		self.LogLister(Clr.label("irc_sasl        ") + Clr.value("IRC sasl if used"))

		self.LogLister(Clr.label("files_directory ") + Clr.value("The location of the files being offered"))
		self.LogLister(Clr.label("lists_directory ") + Clr.value("The location lists are stored"))
		self.LogLister(Clr.label("logs_directory  ") + Clr.value("The location logs are stored"))

		self.LogLister(Clr.label("list_trigger    ") + Clr.value("The trigger to request a file list"))
		self.LogLister(Clr.label("file_trigger    ") + Clr.value("The trigger to request a file"))
		self.LogLister(Clr.label("serv_trigger    ") + Clr.value("The trigger to access the server settings"))
		self.LogLister(Clr.label("info_trigger    ") + Clr.value("The trigger for server information"))
		self.LogLister(Clr.label("ctcp_trigger    ") + Clr.value("The trigger to request a file privately"))

		self.LogLister(Clr.label("library_file    ") + Clr.value("The name of the master library file"))
		self.LogLister(Clr.label("list_file       ") + Clr.value("The file list for public requests"))
		self.LogLister(Clr.label("ctcp_file       ") + Clr.value("The file list for private requests"))
		self.LogLister(Clr.label("log_file        ") + Clr.value("The log file name"))

		self.LogLister(Clr.label("server_enabled  ") + Clr.value("True if the server is serving"))
		self.LogLister(Clr.label("advert_timer    ") + Clr.value("Time between advertisments"))
		self.LogLister(Clr.label("list_service    ") + Clr.value("True if responding to !list"))
		self.LogLister(Clr.label("find_service    ") + Clr.value("True if responding to @find"))
		self.LogLister(Clr.label("srch_service    ") + Clr.value("True if responding to @search"))
		self.LogLister(Clr.label("advert_type     ") + Clr.value("Whether or not the advert is displayed"))
		self.LogLister(Clr.label("advert_text     ") + Clr.value("The actual advert to be displayed"))

	def ShowIrcConfig(self):
		self.LogLister(Clr.title("IRC Configuration"))
		temp_dict = asdict(self.ircdata)
		for key, value in temp_dict.items():
			self.LogLister(Clr.label(key.ljust(15)) + " - " + Clr.value(str(value)))
		self.LogLister(" ")

	def ShowServerConfig(self):
		self.LogLister(Clr.title("Server Configuration"))
		temp_dict = asdict(self.serverdata)
		for key, value in temp_dict.items():
			if len(str(value)) > 60:
				value = value[-60:]
			self.LogLister(Clr.label(key.ljust(15)) + " - " + Clr.value(str(value)))
		self.LogLister(" ")

	def ShowMiscConfig(self):		
		self.LogLister(Clr.title("Miscellanious Configuration"))
		temp_dict = asdict(self.miscdata)
		for key, value in temp_dict.items():
			if len(str(value)) > 60:
				value = value[-60:]
			self.LogLister(Clr.label(key.ljust(15)) + " - " + Clr.value(str(value)))
		self.LogLister(" ")

	def LogLister(self, stufftolog):
		self.logger.Log(stufftolog)

