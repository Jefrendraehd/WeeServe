
import weechat

class SayTo():

	def __init__(self):
		self.buffer_name = ""
		self.buffer_handle = None

	def Buffer(self, target_buffer, stuff_to_say):
		target_handle = weechat.buffer_search("", target_buffer)
		#self.FindBuffer(target_buffer)
		if target_handle:
			weechat.prnt(target_handle, stuff_to_say)
		else:
			weechat.prnt("", stuff_to_say)

	def RequesterNotice(self, the_buffer, the_requester, stuff_to_say):
		cmnd_line = "/notice " + the_requester + " " + stuff_to_say
		weechat.command(the_buffer, cmnd_line)

	def RequesterMsg(self, the_buffer, the_requester, stuff_to_say):
		cmnd_line = "/msg " + the_requester + " " + stuff_to_say
		weechat.command(the_buffer, cmnd_line)

	def FindBuffer(self, the_buffer):
		handle = weechat.buffer_search("python", the_buffer)
		if not handle:
			handle = self.OpenBuffer(the_buffer)
		return handle

	def OpenBuffer(self, buffer_name):
		buffer_handle = weechat.buffer_new(buffer_name,"","","","")
		return buffer_handle
