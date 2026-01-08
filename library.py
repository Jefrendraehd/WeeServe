import os
import json

import weechat

from .mylogger import MyLogger

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

def lcyan(a_string, bg_color=None):
	if bg_color:
		return weechat.color("lightcyan,"+bg_color) + a_string + weechat.color("chat")
	else:
		return weechat.color("lightcyan") + a_string + weechat.color("chat")

class Library():

	#library format = self.library[filename] = [directory, full_path, filesize]

	def __init__(self, irc, server):
		self.irc = irc
		self.server = server
		self.buffer_name = "WeeServe"
		self.buffer_handle = None
		
		self.root_directory = self.server.files_directory
		self.exts_to_scan = [".*"]
		self.library_file = self.server.library_file
		#print(self.server.library_file)
		self.library = []
		self.file_trigger = self.server.file_trigger
		self.list_for_file = []
		self.list_for_ctcp = []
#		print(lcyan(self.server.logs_directory))
		self.logger = MyLogger(self.irc.botname, self.server.logs_directory)

	def getListOfFiles(self, directory_to_scan):
		directory_contents = os.listdir(directory_to_scan)
		list_for_file= []
		all_files = list()
		for entry in directory_contents:
			full_path = os.path.join(directory_to_scan, entry)
			if os.path.isdir(full_path):
				self.list_for_file.append("[" + full_path + "]" + '\n')
				all_files = all_files + self.getListOfFiles(full_path)
			else:
				filesize = os.path.getsize(full_path)
				all_files.append([entry, directory_to_scan, full_path, filesize])
				line = self.file_trigger + " " + entry + "\n"
				self.list_for_file.append(line)
				line = "/ctcp " + self.irc.botname + line
				self.list_for_ctcp.append(line)
		return all_files

	def ReadLibraryFile(self):
		the_lib_file = self.server.lists_directory + self.server.library_file
		if os.path.isfile(the_lib_file):
			with open(the_lib_file, 'r') as infile:
				self.library = json.load(infile)
				infile.close()
			self.LogLister("Server: Loaded %d library entries." %(len(self.library)))
		else:
			self.Rescan()
			self.LogLister("Server: No file library found.")

	def ListFiles(self):
		for prefix, entry in enumerate(self.bookshelf):
			pass
			#self.LogLister(str(prefix) + ": " + entry[1])

	def Rescan(self):
		self.LogLister("Re-scanning file directories")
		work = self.getListOfFiles(self.root_directory)
		for entry in work:
			self.library.append([entry[FILENAME], entry[FILEPATH], 
								entry[FULLPATH], entry[FILESIZE]])
		the_lib_file = self.server.lists_directory + self.server.library_file
		with open(the_lib_file, 'w') as outfile:
			json.dump(self.library, outfile)
		the_list_file = self.server.lists_directory + self.server.list_file
		with open(the_list_file, 'w') as outfile:
			for entry in self.list_for_file:
				outfile.write(entry)
		the_ctcp_file = self.server.lists_directory + self.server.ctcp_file
		with open(the_ctcp_file, 'w') as outfile:
			for entry in self.list_for_ctcp:
				outfile.write(entry)
		self.LogLister("New filelist generated. Found " + str(len(self.library)) + " entries")

	def GetFileData(self, file_to_find):
		#self.LogLister(" " + TimeStamp() + "Retrieving  " + file_to_find)
		rvalue = None
		for entry in self.library:
			if entry[FILENAME] == file_to_find:
				rvalue = entry
				return rvalue

	def SearchFor(self, searchterm):
		rvalue = []
		for entry in self.library:
			if searchterm in entry[FILENAME]:
				rvalue.append(self.server.file_trigger + " " +entry[FILENAME])
				return rvalue

	def Query(self, file_to_find):
		rvalue = False
		for entry in self.library:
			if file_to_find == entry[FILENAME]:
				rvalue = True
				return rvalue

	def LogLister(self, stufftolog):
		self.logger.Log(stufftolog)

	def RecordCount(self):
		return len(self.library)



"""

	def SayToBuffer(self, stuff_to_say):
		if self.FindBuffer():
			weechat.prnt(self.buffer_handle, stuff_to_say)
		else:
			weechat.prnt("", stuff_to_say)

	def FindBuffer(self):
		if weechat.buffer_search("python", self.buffer_name):
			return True
		return False

	def OpenBuffer(self):
		self.buffer_handle = weechat.buffer_new(self.buffer_name,"","","","")
#		self.ShowHelp()
"""